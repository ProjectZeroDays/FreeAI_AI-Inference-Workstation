"""Terminal WebSocket server for FreeAI dashboard.

Runs alongside Flask on port 8081. Provides /ws/terminal WebSocket endpoint
with command whitelist enforcement and process lifecycle management.
"""
import asyncio
import json
import os
import re
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, Optional

# ── Config ─────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "terminal.json"

def _load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return _default_config()

def _default_config() -> dict:
    return {
        "whitelist": {
            "commands": [
                "ls", "dir", "cat", "type", "echo", "pwd", "whoami", "hostname",
                "date", "time", "cls", "clear", "reset",
                "ps", "tasklist", "netstat", "ss", "ipconfig", "ifconfig",
                "docker", "docker-compose",
                "git", "git status", "git log", "git diff", "git branch",
                "nvidia-smi", "nvtop",
                "python", "python3", "pip", "pip3", "node", "npm", "yarn",
                "curl", "wget", "ping", "traceroute", "nslookup", "dig",
                "head", "tail", "less", "more", "grep", "find", "locate",
                "df", "du", "free", "top", "htop", "vmstat",
                "env", "set", "printenv",
                "tree", "file", "which", "where",
                "uptime", "w", "who", "last",
                "mkdir", "touch", "cp", "mv", "rm", "rmdir",
                "history",
                "systemctl", "service",
                "kubectl", "helm",
                "ssh", "scp", "rsync",
                "make", "cmake", "cargo", "go", "gradle", "mvn",
                "ffmpeg", "ffprobe",
                "sqlite3", "mysql", "psql",
                "zip", "unzip", "tar", "gzip",
                "man", "info",
                "htop", "iotop", "lsof",
            ],
        },
        "paths": {
            "blocked_prefixes": [
                "/etc/shadow", "/etc/sudoers", "/proc/kcore",
                "C:\\Windows\\System32\\config\\SAM",
                "C:\\Windows\\System32\\config\\SECURITY",
            ],
            "default_working_dir": True,
        },
        "security": {
            "max_command_length": 4096,
            "timeout_seconds": 60,
            "max_output_bytes": 100000,
            "allow_pipe_redirection": False,
            "allow_background_jobs": False,
            "block_sudo": True,
            "block_interactive_commands": ["passwd", "chsh", "chfn", "useradd", "userdel"],
        },
        "ui": {
            "default_font_size": 14,
            "term": "xterm-256color",
            "rows": 30,
            "cols": 120,
        },
    }

_cfg = _load_config()
WHITELIST = set(_cfg.get("whitelist", {}).get("commands", []))
BLOCKED_PREFIXES = _cfg.get("paths", {}).get("blocked_prefixes", [])
SECURITY = _cfg.get("security", {})
UI_CFG = _cfg.get("ui", {})

# ── Process tracking ──────────────────────────────────────────────
_active_procs: Dict[str, subprocess.Popen] = {}
_proc_lock = asyncio.Lock()

# ── Shell detection ───────────────────────────────────────────────
def _get_shell(shell_type: str = "powershell") -> tuple:
    """Return (cmd_list, prompt_pattern) for the requested shell."""
    if sys.platform == "win32":
        if shell_type == "powershell":
            exe = os.environ.get("POWERSHELL", "powershell")
            return (
                [exe, "-NoLogo", "-NoProfile", "-Command", "-"],
                r"^PS\s+.*$",
            )
        elif shell_type == "cmd":
            return (
                ["cmd", "/Q", "/V:ON", "/K", "prompt $P$G"],
                r"^.*>.*$",
            )
        else:
            # Fallback to PowerShell
            exe = os.environ.get("POWERSHELL", "powershell")
            return (
                [exe, "-NoLogo", "-NoProfile", "-Command", "-"],
                r"^PS\s+.*$",
            )
    else:
        if shell_type == "bash":
            return (
                ["bash", "--norc", "--noprofile", "--login"],
                r"^\$.*$",
            )
        elif shell_type == "zsh":
            return (
                ["zsh", "--no-rcs"],
                r"^\%.*$",
            )
        else:
            return (
                ["bash", "--norc", "--noprofile", "--login"],
                r"^\$.*$",
            )


def _detect_platform_shell() -> tuple:
    """Auto-detect the best shell for the platform."""
    if sys.platform == "win32":
        return _get_shell("powershell")
    return _get_shell("bash")


PLATFORM_SHELL, PROMPT_RE = _detect_platform_shell()

# ── Command validation ────────────────────────────────────────────
def validate_command(cmd: str) -> Optional[str]:
    """Validate a command against the whitelist and security rules.
    Returns None if allowed, or an error message string if blocked."""
    cmd = cmd.strip()
    if not cmd:
        return None  # empty input is fine (e.g. Enter)

    # Length check
    if len(cmd) > SECURITY.get("max_command_length", 4096):
        return f"Command too long (max {SECURITY.get('max_command_length', 4096)} chars)"

    # Block dangerous patterns
    # Pipe/redirection
    if not SECURITY.get("allow_pipe_redirection", False):
        if any(c in cmd for c in ["|", ">", ">>", "<", "<<", "2>", "2>&1", "&>"]):
            return "Pipe/redirection characters are not allowed"

    # Background jobs
    if not SECURITY.get("allow_background_jobs", False):
        if cmd.endswith("&") or "; " in cmd:
            return "Background jobs are not allowed"

    # Sudo/block list
    if SECURITY.get("block_sudo", True):
        if re.match(r"^\s*sudo\b", cmd):
            return "sudo is blocked"

    blocked_cmds = SECURITY.get("block_interactive_commands", [])
    base_cmd = cmd.split()[0] if cmd.split() else cmd
    if base_cmd in blocked_cmds:
        return f"Command '{base_cmd}' is blocked"

    # Block dangerous flag combinations
    dangerous_patterns = [
        (r"rm\s+.*-\w*r\w*", "Dangerous rm flags (recursive) are blocked"),
        (r"rm\s+/\s*$", "rm / is blocked"),
        (r"\brm\s+-rf\b", "rm -rf is blocked"),
        (r"\brm\s+-rf\s+/?\s*$", "rm -rf on root is blocked"),
        (r":\(\)\{\s*:\|:&\s*-\s*\|:\s*;", "Fork bomb detected"),
        (r">\s*/dev/\w+", "Redirecting to /dev is blocked"),
    ]
    for pattern, msg in dangerous_patterns:
        if re.search(pattern, cmd, re.IGNORECASE):
            return msg

    # Path restrictions
    for prefix in BLOCKED_PREFIXES:
        if prefix in cmd:
            return f"Path containing '{prefix}' is blocked"

    # Whitelist check — allow if base command is in whitelist
    allowed = False
    for wc in WHITELIST:
        if base_cmd == wc or cmd.startswith(wc + " "):
            allowed = True
            break
    if not allowed:
        return f"Command '{base_cmd}' is not in the allowed list"

    return None


# ── WebSocket server ──────────────────────────────────────────────
class TerminalSession:
    """Manages a single terminal WebSocket connection."""

    def __init__(self, ws, tab_id: str, shell_type: str):
        self.ws = ws
        self.tab_id = tab_id
        self.shell_type = shell_type
        self.proc: Optional[subprocess.Popen] = None
        self.running = True
        self.output_queue: asyncio.Queue = asyncio.Queue()
        self._reader_task: Optional[asyncio.Task] = None
        self._writer_task: Optional[asyncio.Task] = None
        self._start_time = time.time()

    async def start(self):
        """Start the terminal process and I/O tasks."""
        try:
            shell_cmd, _ = _get_shell(self.shell_type)
            env = os.environ.copy()
            env["TERM"] = UI_CFG.get("term", "xterm-256color")
            env["LANG"] = "en_US.UTF-8"

            self.proc = subprocess.Popen(
                shell_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,  # binary mode for proper terminal I/O
                env=env,
                bufsize=0,
            )
            async with _proc_lock:
                _active_procs[self.tab_id] = self.proc

            self._reader_task = asyncio.create_task(self._read_loop())
            self._writer_task = asyncio.create_task(self._write_loop())

            # Send prompt
            await self._send({
                "type": "prompt",
                "prompt": self._get_prompt(),
            })
        except Exception as e:
            await self._send({"type": "error", "error": f"Failed to start shell: {e}"})
            self.running = False

    def _get_prompt(self) -> str:
        if sys.platform == "win32":
            try:
                user = os.environ.get("USERNAME", "user")
                host = os.environ.get("COMPUTERNAME", "localhost")
                return f"[FreeAI] {user}@{host}: "
            except Exception:
                return "[FreeAI] ~: "
        else:
            try:
                user = os.environ.get("USER", "user")
                host = os.environ.get("HOSTNAME", "localhost")
                return f"[FreeAI] {user}@{host}:~$ "
            except Exception:
                return "[FreeAI] ~$ "

    async def _read_loop(self):
        """Read from subprocess stdout and push to queue."""
        try:
            while self.running and self.proc and self.proc.poll() is None:
                try:
                    data = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, self.proc.stdout.read, 4096),
                        timeout=0.1,
                    )
                    if data:
                        await self.output_queue.put(data)
                except asyncio.TimeoutError:
                    continue
                except ValueError:
                    break
        except Exception:
            pass
        finally:
            await self.cleanup()

    async def _write_loop(self):
        """Drain output queue and send to WebSocket."""
        try:
            while self.running:
                try:
                    data = await asyncio.wait_for(self.output_queue.get(), timeout=0.05)
                    max_bytes = SECURITY.get("max_output_bytes", 100000)
                    if len(data) > max_bytes:
                        data = data[:max_bytes]
                        await self._send({"type": "output", "output": data.decode("utf-8", errors="replace") + "\n...[truncated]"})
                    else:
                        await self._send({"type": "output", "output": data.decode("utf-8", errors="replace")})
                except asyncio.TimeoutError:
                    continue
        except Exception:
            pass

    async def _send(self, msg: dict):
        """Send a JSON message to the WebSocket."""
        try:
            if self.ws and self.ws.open:
                await self.ws.send(json.dumps(msg, ensure_ascii=False))
        except Exception:
            self.running = False

    async def input(self, data: str):
        """Send input to the subprocess."""
        if not self.proc or self.proc.poll() is not None:
            await self.start()

        cmd = data.strip()

        # Validate
        err = validate_command(cmd)
        if err:
            await self._send({"type": "error", "error": err})
            await self._send({"type": "prompt", "prompt": self._get_prompt()})
            return

        # Send to subprocess stdin
        try:
            if self.proc and self.proc.stdin:
                self.proc.stdin.write(data.encode("utf-8") + b"\n")
                await self.proc.stdin.drain() if hasattr(self.proc.stdin, 'drain') else asyncio.sleep(0)
        except Exception as e:
            await self._send({"type": "error", "error": f"Write error: {e}"})

    async def cleanup(self):
        """Clean up subprocess resources."""
        self.running = False
        async with _proc_lock:
            _active_procs.pop(self.tab_id, None)
        if self.proc:
            try:
                if self.proc.poll() is None:
                    if sys.platform == "win32":
                        self.proc.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        self.proc.terminate()
                    try:
                        self.proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.proc.kill()
            except Exception:
                pass
            self.proc = None
        if self._reader_task:
            self._reader_task.cancel()
        if self._writer_task:
            self._writer_task.cancel()

    def is_alive(self) -> bool:
        if self.proc:
            return self.proc.poll() is None
        return False


# ── Session registry ──────────────────────────────────────────────
_sessions: Dict[str, TerminalSession] = {}
_sessions_lock = asyncio.Lock()


async def handle_terminal(ws):
    """Main WebSocket handler for terminal connections."""
    tab_id = "main"
    shell_type = "powershell" if sys.platform == "win32" else "bash"

    # Parse query params
    try:
        path = ws.path if hasattr(ws, 'path') else ws.request.path if hasattr(ws, 'request') else "/"
        if "?" in path:
            params = path.split("?", 1)[1]
            for param in params.split("&"):
                if param.startswith("tab="):
                    tab_id = param[4:]
                elif param.startswith("shell="):
                    shell_type = param[6:]
    except Exception:
        pass

    session = TerminalSession(ws, tab_id, shell_type)
    async with _sessions_lock:
        _sessions[tab_id] = session

    try:
        await session.start()
        async for message in ws:
            if not session.running:
                break
            try:
                msg = json.loads(message)
                msg_type = msg.get("type", "")
                if msg_type == "input":
                    await session.input(msg.get("data", ""))
                elif msg_type == "paste":
                    await session.input(msg.get("data", ""))
                elif msg_type == "keypress":
                    key = msg.get("key", "")
                    key_map = {
                        "Enter": "\r",
                        "Backspace": "\x7f",
                        "Tab": "\t",
                        "Ctrl+C": "\x03",
                        "ArrowUp": "\x1b[A",
                        "ArrowDown": "\x1b[B",
                        "ArrowRight": "\x1b[C",
                        "ArrowLeft": "\x1b[D",
                        "Home": "\x1b[1~",
                        "End": "\x1b[4~",
                        "Insert": "\x1b[2~",
                        "Delete": "\x1b[3~",
                        "PageUp": "\x1b[5~",
                        "PageDown": "\x1b[6~",
                    }
                    for i in range(1, 13):
                        key_map[f"F{i}"] = f"\x1b[{11+i}~"
                    if key in key_map:
                        await session.input(key_map[key])
                elif msg_type == "resize":
                    rows = msg.get("rows", UI_CFG.get("rows", 30))
                    cols = msg.get("cols", UI_CFG.get("cols", 120))
                    try:
                        if sys.platform == "win32":
                            import ctypes
                            kernel32 = ctypes.windll.kernel32
                            handle = kernel32.GetStdHandle(-11)
                            coord = ctypes.wintypes.COORD(cols, rows)
                            kernel32.SetConsoleScreenBufferSize(handle, coord)
                        else:
                            pass  # ptsresize handled by shell
                    except Exception:
                        pass
            except json.JSONDecodeError:
                await session._send({"type": "error", "error": "Invalid JSON"})
    except Exception as e:
        print(f"[terminal] Session error for tab {tab_id}: {e}", file=sys.stderr)
    finally:
        await session.cleanup()
        async with _sessions_lock:
            _sessions.pop(tab_id, None)


async def health_check():
    """Periodic cleanup of dead sessions."""
    while True:
        await asyncio.sleep(30)
        async with _sessions_lock:
            dead = [tid for tid, s in _sessions.items() if not s.is_alive()]
            for tid in dead:
                await _sessions[tid].cleanup()
                del _sessions[tid]
        if _sessions:
            print(f"[terminal] Active sessions: {len(_sessions)}", file=sys.stderr)


# ── Server startup ────────────────────────────────────────────────
async def main():
    port = int(os.environ.get("TERMINAL_WS_PORT", "8081"))
    host = os.environ.get("TERMINAL_WS_HOST", "0.0.0.0")

    server = await asyncio.start_server(handle_terminal, host, port)
    print(f"[terminal] WebSocket server listening on ws://{host}:{port}/ws/terminal", flush=True)

    asyncio.create_task(health_check())

    async with server:
        await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[terminal] Shutting down...", flush=True)
        sys.exit(0)
