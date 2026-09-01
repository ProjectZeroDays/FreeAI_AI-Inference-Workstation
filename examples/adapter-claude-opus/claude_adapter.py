"""
Claude/Opus Adapter — Provider-specific integration with streaming support.
Demonstrates the adapter pattern FreeAI uses for multi-provider routing.

Usage:
    python claude_adapter.py --prompt "Explain quantum computing"
    python claude_adapter.py --prompt "Write a Python script" --stream
    python claude_adapter.py --list-models
"""
import argparse
import json
import sys
import time
from typing import Optional


# ── Provider Adapters ──────────────────────────────────────────────────────────

class BaseAdapter:
    """Base class for LLM provider adapters."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def chat(self, messages: list, stream: bool = False) -> str:
        raise NotImplementedError

    def list_models(self) -> list:
        return [self.model]


class AgnesAdapter(BaseAdapter):
    """Adapter for Agnes AI API (primary provider for FreeAI)."""

    ENDPOINT = "https://api.agnes-ai.com/v1/chat/completions"

    def chat(self, messages: list, stream: bool = False) -> str:
        import urllib.request
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 4096,
        }).encode()
        req = urllib.request.Request(
            self.ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]

    def list_models(self) -> list:
        return [
            "agnes-2.0-flash",
            "agnes-2.0",
            "agnes-1.5-pro",
        ]


class OllamaAdapter(BaseAdapter):
    """Adapter for local Ollama instances."""

    ENDPOINT = "http://localhost:11434/api/chat"

    def __init__(self, model: str = "llama3.1"):
        super().__init__("", model)

    def chat(self, messages: list, stream: bool = False) -> str:
        import urllib.request
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": 0.7, "num_predict": 2048},
        }).encode()
        req = urllib.request.Request(
            self.ENDPOINT,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result["message"]["content"]

    def list_models(self) -> list:
        import urllib.request
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return ["llama3.1", "llama3", "mistral", "codellama"]


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI-compatible APIs (ChatGPT, Azure OpenAI, etc.)."""

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str = "https://api.openai.com/v1"):
        super().__init__(api_key, model)
        self.base_url = base_url

    def chat(self, messages: list, stream: bool = False) -> str:
        import urllib.request
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 4096,
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]

    def list_models(self) -> list:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]


# ── Router ─────────────────────────────────────────────────────────────────────

class ProviderRouter:
    """Routes requests to the correct provider adapter."""

    PROVIDERS = {
        "agnes": AgnesAdapter,
        "ollama": OllamaAdapter,
        "openai": OpenAIAdapter,
    }

    @classmethod
    def create(cls, provider: str, api_key: str, model: Optional[str] = None) -> BaseAdapter:
        adapter_cls = cls.PROVIDERS.get(provider)
        if not adapter_cls:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(cls.PROVIDERS)}")
        if provider == "ollama":
            return adapter_cls(model or "llama3.1")
        return adapter_cls(api_key, model or "agnes-2.0-flash")

    @classmethod
    def list_all_models(cls) -> dict:
        result = {}
        for name, adapter_cls in cls.PROVIDERS.items():
            if name == "ollama":
                result[name] = adapter_cls().list_models()
            else:
                result[name] = adapter_cls("", "").list_models()
        return result


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Claude/Opus Adapter Demo")
    parser.add_argument("--provider", default="agnes", choices=list(ProviderRouter.PROVIDERS))
    parser.add_argument("--key", default="", help="API key")
    parser.add_argument("--model", default=None)
    parser.add_argument("--prompt", default=None, help="Single prompt (non-interactive)")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--stream", action="store_true", help="Stream output")
    args = parser.parse_args()

    if args.list_models:
        models = ProviderRouter.list_all_models()
        for provider, model_list in models.items():
            print(f"\n{provider}:")
            for m in model_list:
                print(f"  - {m}")
        return

    router = ProviderRouter.create(args.provider, args.key, args.model)
    model = router.model
    print(f"Provider: {args.provider} | Model: {model}")

    if args.prompt:
        response = router.chat([{"role": "user", "content": args.prompt}], args.stream)
        print(response)
        return

    print("Interactive mode. Type 'quit' to exit.")
    messages = []
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
        messages.append({"role": "user", "content": user})
        t0 = time.time()
        response = router.chat(messages, args.stream)
        messages.append({"role": "assistant", "content": response})
        print(f"\n{response}")
        print(f"\n[{time.time() - t0:.1f}s]")


if __name__ == "__main__":
    main()
