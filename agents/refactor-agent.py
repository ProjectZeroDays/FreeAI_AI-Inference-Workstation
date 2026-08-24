#!/usr/bin/env python3
import os

import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")


def refactor(code: str, language: str = "python"):
    prompt = f"""
You are a refactor agent for {language}.

Task:
Refactor the following code for readability, maintainability, and performance.

Code:
```{language}
{code}
```

Deliver:
- Refactored code
- Short explanation of improvements
"""
    r = requests.post(ROUTER_URL, json={"prompt": prompt, "max_tokens": 2048})
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    sample = "def add(a,b):return a+b"
    print(refactor(sample))
