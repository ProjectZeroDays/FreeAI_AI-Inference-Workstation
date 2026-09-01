"""
Jarvis Demo — Agent orchestration with memory, tools, and a conversational shell.
Demonstrates the pattern FreeAI uses for autonomous agent coordination.
"""
import json
import time
from pathlib import Path
from typing import Optional


class ConversationMemory:
    """Simple in-memory conversation store with summarisation."""

    def __init__(self, max_turns: int = 50):
        self.max_turns = max_turns
        self.turns: list[dict] = []

    def add(self, role: str, content: str) -> None:
        self.turns.append({"role": role, "content": content, "ts": time.time()})
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def summary(self) -> str:
        if not self.turns:
            return "No prior context."
        recent = self.turns[-10:]
        return "\n".join(f"[{t['role']}] {t['content'][:200]}" for t in recent)

    def to_messages(self) -> list[dict]:
        return [{"role": t["role"], "content": t["content"]} for t in self.turns]


class ToolRegistry:
    """Extensible tool registry — mirrors FreeAI's plugin pattern."""

    def __init__(self):
        self._tools: dict[str, callable] = {}

    def register(self, name: str, desc: str, fn):
        self._tools[name] = {"desc": desc, "fn": fn}

    def call(self, name: str, args: dict) -> str:
        if name not in self._tools:
            return f"Unknown tool: {name}"
        return self._tools[name]["fn"](args)

    def list_tools(self) -> str:
        return "\n".join(f"  {n}: {t['desc']}" for n, t in self._tools.items())


class JarvisAgent:
    """
    Minimal Jarvis-style agent with tool use and memory.
    Demonstrates the orchestration pattern used by FreeAI's agent workforce.
    """

    SYSTEM_PROMPT = """You are Jarvis, a personal AI assistant. You have access to tools
for searching, computing, and file operations. Be helpful, concise, and proactive.
When a tool result is returned, use it directly in your response."""

    def __init__(self, api_key: str, model: str = "agnes-2.0-flash"):
        self.memory = ConversationMemory()
        self.tools = ToolRegistry()
        self.api_key = api_key
        self.model = model
        self._register_builtins()

    def _register_builtins(self):
        import subprocess
        self.tools.register("run_command", "Run a shell command", lambda a: subprocess.run(
            a.get("cmd", ""), shell=True, capture_output=True, text=True, timeout=30
        ).stdout[:1000])
        self.tools.register("read_file", "Read a file", lambda a: Path(a["path"]).read_text()[:2000])
        self.tools.register("search_web", "Search the web for information",
                            lambda a: f"[web search for: {a.get('query', '')}] — simulated result")
        self.tools.register("list_tools", "List available tools", lambda _: self.tools.list_tools())

    def _call_llm(self, messages: list[dict]) -> str:
        import urllib.request
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2048,
        }).encode()
        req = urllib.request.Request(
            "https://api.agnes-ai.com/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result["choices"][0]["message"].get("content", "")

    def think(self, user_input: str) -> str:
        """Main reasoning loop: LLM → tool call → LLM → response."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        messages.extend(self.memory.to_messages())
        messages.append({"role": "user", "content": user_input})
        self.memory.add("user", user_input)

        # First LLM call
        response = self._call_llm(messages)
        self.memory.add("assistant", response)

        # Check for tool calls (simplified — looks for [TOOL:name] markers)
        if "[TOOL:" in response:
            import re
            tool_calls = re.findall(r'\[TOOL:(\w+)\(([^)]*)\)\]', response)
            for tool_name, tool_args in tool_calls:
                try:
                    args = json.loads(tool_args) if tool_args else {}
                except json.JSONDecodeError:
                    args = {"query": tool_args}
                tool_result = self.tools.call(tool_name, args)
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "tool", "content": tool_result, "tool_name": tool_name})
                response = self._call_llm(messages)
                self.memory.add("assistant", response)

        return response


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Jarvis Demo Agent")
    parser.add_argument("--key", default="", help="Agnes API key")
    parser.add_argument("--model", default="agnes-2.0-flash")
    parser.add_argument("--once", default=None, help="Single prompt mode")
    args = parser.parse_args()

    agent = JarvisAgent(api_key=args.key, model=args.model)
    print("=" * 60)
    print("  Jarvis Demo Agent")
    print("  Model: " + agent.model)
    print("  Tools: " + agent.tools.list_tools())
    print("  Type 'quit' to exit, 'tools' to list tools")
    print("=" * 60)

    if args.once:
        print("\n" + agent.think(args.once))
        return

    while True:
        try:
            user = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not user:
            continue
        if user.lower() in ("quit", "exit", "q"):
            print("Bye.")
            break
        if user.lower() == "tools":
            print(agent.tools.list_tools())
            continue
        if user.lower() == "memory":
            print(agent.memory.summary())
            continue
        print("\n" + agent.think(user))


if __name__ == "__main__":
    main()
