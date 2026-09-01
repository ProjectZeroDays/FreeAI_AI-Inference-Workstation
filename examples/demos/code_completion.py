"""
Code Completion Demo — Context-aware code suggestions.
Demonstrates how to use LLMs for IDE-like code completion.
"""
import argparse
import json
import sys
import time


SYSTEM_PROMPT = """You are a code completion engine. Given the user's code and request,
provide the most relevant code snippet. Output ONLY the code, no explanations.
Use the same language, style, and conventions as the input."""


def complete(api_key: str, model: str, code: str, request: str = "") -> str:
    import urllib.request
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Code:\n```\n{code}\n```\n\nRequest: {request or 'Continue the code'}"},
    ]
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
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
    parser = argparse.ArgumentParser(description="Code Completion Demo")
    parser.add_argument("--key", default="", help="Agnes API key")
    parser.add_argument("--model", default="agnes-2.0-flash")
    parser.add_argument("--file", default=None, help="Read code from file")
    parser.add_argument("--request", default="", help="Additional request")
    args = parser.parse_args()

    if not args.key:
        print("ERROR: Provide --key with your Agnes API key")
        sys.exit(1)

    if args.file:
        with open(args.file) as f:
            code = f.read()
    else:
        print("Paste your code (end with EOF on its own line):")
        lines = []
        while True:
            line = sys.stdin.readline()
            if line.strip() == "EOF":
                break
            lines.append(line)
        code = "".join(lines)

    print(f"\nAnalyzing {len(code)} chars of code...")
    t0 = time.time()
    response = complete(api_key=args.key, model=args.model, code=code, request=args.request)
    elapsed = time.time() - t0

    print("\n" + "=" * 60)
    print(" SUGGESTION:")
    print("=" * 60)
    print(response)
    print(f"\n[{elapsed:.1f}s]")


if __name__ == "__main__":
    main()
