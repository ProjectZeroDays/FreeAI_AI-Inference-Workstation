"""Knight-Shade Intelligence & Reverse Engineering Pipeline.

Integrates Ghidra (static analysis), Frida (runtime instrumentation),
Burp Suite (MITM proxy), and CloakBrowser (stealth backend) into
the browser automation pipeline.
"""
import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
GHIDRA_DIR = Path(os.environ.get("GHIDRA_HOME", r"C:\Program Files\ghidra"))
FRIDA_DIR = Path(os.environ.get("FRIDA_DIR", r""))


class GhidraAnalyzer:
    """Static binary analysis via Ghidra headless mode."""

    def __init__(self, ghidra_path=None):
        self.ghidra_path = Path(ghidra_path or GHIDRA_DIR)
        self._java_available = False
        self._analyze3_path = None
        self._check()

    def _check(self):
        java = os.environ.get("JAVA_HOME")
        if java:
            java_bin = Path(java) / "bin" / "java.exe"
            if java_bin.exists():
                self._java_available = True
        analyze3 = self.ghidra_path / "support" / "analyzeHeadless"
        if analyze3.exists():
            self._analyze3_path = str(analyze3)

    def analyze_binary(self, binary_path, output_dir=None):
        """Run Ghidra headless analysis on a binary file.
        Returns structured decompiled output.
        """
        if not self._java_available or not self._analyze3_path:
            return {"error": "Ghidra not available (Java + Ghidra required)"}

        binary = Path(binary_path)
        if not binary.exists():
            return {"error": f"Binary not found: {binary_path}"}

        out_dir = Path(output_dir or binary.parent / "ghidra_output")
        out_dir.mkdir(parents=True, exist_ok=True)
        proj_name = f"ks_{binary.stem}_{int(time.time())}"

        # Ghidra script for structured output
        script = '''
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.framework.model.*;

public class Extract extends GhidraScript {
    protected void run() throws Exception {
        println("=== GHIDRA ANALYSIS ===");
        println("Program: " + currentProgram.getName());
        println("Entry Points:");
        for (Symbol s : currentProgram.getSymbolTable().getSymbols(currentProgram.getEntryPoint())) {
            println("  " + s.getName() + " @ " + s.getAddress());
        }
        println("Functions:");
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            println("  " + f.getName() + " @ " + f.getEntryPoint() + " (" + f.getBody().getNumBytes() + " bytes)");
        }
    }
}
'''
        script_path = out_dir / "extract.ghidra"
        script_path.write_text(script)

        cmd = [
            self._analyze3_path, str(out_dir), proj_name, "-import", str(binary),
            "-scriptPath", str(out_dir), "-postScript", "extract.ghidra",
            "-deleteProject",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[-5000:],
                "stderr": result.stderr[-2000:],
                "project": str(out_dir / proj_name),
            }
        except subprocess.TimeoutExpired:
            return {"error": "Ghidra analysis timed out (300s)"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_wasm(self, wasm_path, output_dir=None):
        """Analyze WebAssembly binary."""
        return self.analyze_binary(wasm_path, output_dir)

    def is_available(self):
        return self._java_available and bool(self._analyze3_path)


class FridaInstrumentor:
    """Runtime process instrumentation via Frida."""

    def __init__(self, frida_path=None):
        self.frida_path = Path(frida_path or FRIDA_DIR)
        self._frida_available = False
        try:
            import frida
            self._frida = frida
            self._frida_available = True
        except ImportError:
            pass

    def hook_process(self, target_name, script):
        """Attach Frida to a running process and execute script."""
        if not self._frida_available:
            return {"error": "Frida Python binding not installed"}
        try:
            session = self._frida.attach(target_name)
            frida_script = session.create_script(script)
            results = []

            def on_message(msg, data):
                results.append(msg)

            frida_script.on('message', on_message)
            frida_script.load()
            return {"attached": target_name, "messages": results[:100]}
        except Exception as e:
            return {"error": str(e)}

    def hook_browser_session(self, target_pid, script):
        """Hook a specific browser process by PID."""
        if not self._frida_available:
            return {"error": "Frida not available"}
        try:
            session = self._frida.attach(target_pid)
            frida_script = session.create_script(script)
            results = []
            frida_script.on('message', lambda msg, data: results.append(msg))
            frida_script.load()
            return {"pid": target_pid, "attached": True, "results": results[:50]}
        except Exception as e:
            return {"error": str(e)}

    def is_available(self):
        return self._frida_available


class BurpProxy:
    """MITM proxy integration via Burp Suite bappstore extensions."""

    def __init__(self, burp_config=None):
        self.config = burp_config or {}
        self._host = self.config.get("host", "127.0.0.1")
        self._port = self.config.get("port", 8080)

    def get_proxy_config(self):
        """Return proxy config for browser/engine."""
        return {
            "server": f"http://{self._host}:{self._port}",
            "scheme": "http",
        }

    def is_configured(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((self._host, self._port))
            s.close()
            return True
        except Exception:
            return False

    def describe(self):
        return {
            "host": self._host,
            "port": self._port,
            "configured": self.is_configured(),
            "bappstore_count": "400+",
        }


# ── Orchestrator ───────────────────────────────────────────────────
class IntelligencePipeline:
    """Coordinate Ghidra, Frida, Burp Suite into a unified pipeline."""

    def __init__(self, config=None):
        self.config = config or {}
        self.ghidra = GhidraAnalyzer()
        self.frida = FridaInstrumentor()
        self.burp = BurpProxy(self.config.get("burp", {}))

    def analyze(self, artifact_path, artifact_type="binary"):
        """Route artifact to appropriate analyzer."""
        if artifact_type in ("binary", "exe", "elf", "wasm"):
            return self.ghidra.analyze_binary(artifact_path)
        elif artifact_type == "wasm":
            return self.ghidra.analyze_wasm(artifact_path)
        return {"error": f"Unknown artifact type: {artifact_type}"}

    def instrument(self, target, script):
        """Run Frida instrumentation."""
        if isinstance(target, int):
            return self.frida.hook_browser_session(target, script)
        return self.frida.hook_process(target, script)

    def describe(self):
        return {
            "ghidra": {"available": self.ghidra.is_available()},
            "frida": {"available": self.frida.is_available()},
            "burp": self.burp.describe(),
        }


if __name__ == "__main__":
    pipeline = IntelligencePipeline()
    print(json.dumps(pipeline.describe(), indent=2))
