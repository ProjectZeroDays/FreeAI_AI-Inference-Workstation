#!/usr/bin/env python3
"""Shared GitHub helpers for skill install scripts."""

from __future__ import annotations

import os
import re
import urllib.request
from urllib.parse import urlparse


def _validate_github_url(url: str) -> str:
    try:
        if "/../" in url or re.search(r"/%2e%2e/", url, re.IGNORECASE):
            raise ValueError("Invalid path")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Invalid protocol")
        if not parsed.hostname:
            raise ValueError("Invalid host")
        allowed_domains = ["api.github.com", "github.com", "raw.githubusercontent.com"]
        if parsed.hostname.lower() not in allowed_domains:
            raise ValueError("Invalid host")
        return url
    except Exception:
        raise ValueError("Invalid URL")


def github_request(url: str, user_agent: str) -> bytes:
    validated_url = _validate_github_url(url)
    headers = {"User-Agent": user_agent}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(validated_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def github_api_contents_url(repo: str, path: str, ref: str) -> str:
    return f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
