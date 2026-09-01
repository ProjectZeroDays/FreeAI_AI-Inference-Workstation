"""
CLI Chat Demo — Simple non-streaming chat with LLM providers.
Quick-start example for integrating FreeAI into any CLI tool.
"""
import argparse
import json
import sys
import time


SYSTEM_PROMPT = "You are a helpful assistant."


def chat(api_key: str, model: str, messages: list) -> str:
    import urllib.request
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048,
    }).encode()
    req = urllib.request.Request(
        "https://api.agnes-ai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="CLI Chat Demo")
    parser.add_argument("--key", default="", help="Agnes API key")
    parser.add_argument("--model", default="agnes-2.0-flash")
    parser.add_argument("--prompt", default=None)
    args = parser.parse_args()

    if not args.key:
        print("ERROR: Provide --key with your Agnes API key")
        print("Get one from: https://api.agnes-ai.com")
        sys.exit(1)

    print("=" * 60)
    print("  CLI Chat Demo")
    print(f"  Model: {args.model}")
    print("  Type 'quit' to exit, 'clear' to reset context")
    print("=" * 60)

    if args.prompt:
        response = chat(args.key, args.model, [{"role": "user", "content": args.prompt}])
        print(response)
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
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
        if user.lower() == "clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("[context cleared]")
            continue
        t0 = time.time()
        messages.append({"role": "user", "content": user})
        response = chat(args.key, args.model, messages)
        messages.append({"role": "assistant", "content": response})
        print(f"\n{response}")
        print(f"\n[{time.time() - t0:.1f}s]")


if __name__ == "__main__":
    main()
