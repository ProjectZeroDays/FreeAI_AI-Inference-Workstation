#!/usr/bin/env python3
import os

import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")


def debug(code: str, error: str, language: str = "python"):
    prompt = f"""
You are a debug agent for {language}.

Code:
```{language}
{code}
```

Error:
{error}

Deliver:
- Root cause
- Fixed code
- Explanation
"""
    r = requests.post(ROUTER_URL, json={"prompt": prompt, "max_tokens": 2048})
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    sample = "print(1/0)"
    print(debug(sample, "ZeroDivisionError"))
