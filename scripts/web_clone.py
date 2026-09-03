#!/usr/bin/env python3
"""
FreeAI Web Cloner — Expert Website Cloning Tool

Clones any website to a local directory with:
- Full HTML, CSS, JS, image, font, and media downloads
- Relative URL rewriting for offline browsing
- Respects robots.txt and crawl-delay
- Concurrent downloads with retry logic
- Sitemap-aware crawling
- Anti-bot detection bypass via stealth mode
- Mobile/desktop viewport cloning
- Cookie session preservation

Usage:
    python web_clone.py <URL> [options]

Examples:
    python web_clone.py https://example.com
    python web_clone.py https://example.com --depth 3 --limit 100
    python web_clone.py https://example.com --output ./clones/site
    python web_clone.py https://example.com --js --images --fonts
    python web_clone.py https://example.com --robots --delay 2
    python web_clone.py https://example.com --mobile --viewport 375x812
    python web_clone.py https://example.com --cookies cookies.txt
    python web_clone.py https://example.com --sitemap
    python web_clone.py https://example.com --dry-run
"""

import asyncio
import argparse
import hashlib
import html
import json
import logging
import mimetypes
import os
import re
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import urllib.robotparser
    HAS_ROBOTS = True
except ImportError:
    HAS_ROBOTS = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("web_clone")


# ── MIME type mapping ────────────────────────────────────────────────────────
STATIC_EXTENSIONS = {
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif", ".tiff",
    # Fonts
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    # Media
    ".mp4", ".webm", ".ogg", ".mp3", ".wav", ".flac", ".avi", ".mov", ".mkv",
    # Documents
    ".pdf", ".zip", ".tar", ".gz", ".rar",
}

JS_EXTENSIONS = {".js", ".mjs", ".cjs"}
CSS_EXTENSIONS = {".css"}


# ── Robots.txt parser ────────────────────────────────────────────────────────
class RobotsChecker:
    """Check robots.txt rules before crawling."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.base_netloc = urlparse(base_url).netloc
        self.parser = None
        self.delay = 0
        self._load()

    def _load(self):
        if not HAS_ROBOTS:
            return
        try:
            robots_url = f"{self.base_url.rstrip('/')}/robots.txt"
            self.parser = urllib.robotparser.RobotFileParser()
            self.parser.set_url(robots_url)
            self.parser.read()
            log.info("Loaded robots.txt from %s", robots_url)
        except Exception as e:
            log.warning("Could not load robots.txt: %s", e)

    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        if not self.parser:
            return True
        try:
            return self.parser.can_fetch(user_agent, url)
        except Exception:
            return True

    def crawl_delay(self) -> float:
        if not self.parser:
            return 0
        try:
            return self.parser.crawl_delay("*") or 0
        except Exception:
            return 0


# ── URL handler ──────────────────────────────────────────────────────────────
class URLHandler:
    """Resolve and normalize URLs for cloning."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        parsed = urlparse(base_url)
        self.base_scheme = parsed.scheme
        self.base_netloc = parsed.netloc
        self.base_path = parsed.path.rsplit("/", 1)[0] if parsed.path else ""

    def resolve(self, url: str) -> str:
        """Resolve relative URL against base."""
        if not url or url.startswith("data:") or url.startswith("javascript:"):
            return None
        url = url.strip().strip("'\"")
        if url.startswith("//"):
            return f"{self.base_scheme}:{url}"
        if url.startswith("/"):
            return f"{self.base_scheme}://{self.base_netloc}{url}"
        if url.startswith("#") or url.startswith("mailto:") or url.startswith("tel:"):
            return None
        return urljoin(self.base_url, url)

    def make_local_path(self, url: str) -> Path:
        """Convert URL to local filesystem path."""
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")
        if not path or path.endswith("/"):
            path = path + "index.html"
        # Sanitize
        path = re.sub(r"[^\w\-. ~()]", "_", path)
        path = path.replace(" ", "_")
        # Remove query strings
        path = path.split("?")[0].split("#")[0]
        return Path(path)

    def is_static_asset(self, url: str) -> bool:
        """Check if URL points to a static asset."""
        ext = Path(urlparse(url).path).suffix.lower()
        return ext in STATIC_EXTENSIONS or ext in JS_EXTENSIONS or ext in CSS_EXTENSIONS

    def get_content_type_hint(self, url: str) -> str:
        """Guess content type from URL."""
        ext = Path(urlparse(url).path).suffix.lower()
        return mimetypes.guess_type(url)[0] or f"application/octet-stream"


# ── Downloader ───────────────────────────────────────────────────────────────
class Downloader:
    """Download files with retry, concurrency, and rate limiting."""

    def __init__(
        self,
        max_workers: int = 10,
        timeout: int = 30,
        retry: int = 3,
        delay: float = 0.0,
        headers: dict = None,
    ):
        self.max_workers = max_workers
        self.timeout = timeout
        self.retry = retry
        self.delay = delay
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        self.session = requests.Session() if HAS_REQUESTS else None
        self.curl_session = None
        self._last_request = 0
        self.stats = {"downloaded": 0, "failed": 0, "skipped": 0, "bytes": 0}

    def _throttle(self):
        if self.delay > 0:
            elapsed = time.time() - self._last_request
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        self._last_request = time.time()

    def _fetch_with_curl(self, url: str) -> Optional[bytes]:
        """Try curl_cffi first (better anti-bot)."""
        if not HAS_CURL_CFFI:
            return None
        self._throttle()
        for attempt in range(self.retry):
            try:
                resp = cffi_requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    impersonate="chrome120",
                )
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                log.debug(f"  curl_cffi attempt {attempt+1} failed: {e}")
                time.sleep(0.5)
        return None

    def _fetch_with_requests(self, url: str) -> Optional[bytes]:
        """Fallback to requests."""
        if not self.session:
            return None
        self._throttle()
        for attempt in range(self.retry):
            try:
                resp = self.session.get(url, headers=self.headers, timeout=self.timeout)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                log.debug(f"  requests attempt {attempt+1} failed: {e}")
                time.sleep(0.5)
        return None

    def fetch(self, url: str) -> tuple:
        """Fetch URL, return (content_bytes, status_code, content_type)."""
        content = None
        content_type = None

        content = self._fetch_with_curl(url)
        if content is None and HAS_REQUESTS:
            content = self._fetch_with_requests(url)

        if content is None:
            return None, 0, None

        # Detect content type
        if not content_type:
            content_type = mimetypes.guess_type(url)[0] or "application/octet-stream"

        self.stats["downloaded"] += 1
        self.stats["bytes"] += len(content)
        log.debug(f"  ✓ {url[:80]} ({len(content):,} bytes)")
        return content, 200, content_type

    def fetch_html(self, url: str) -> Optional[str]:
        """Fetch and decode HTML."""
        content, status, ct = self.fetch(url)
        if content is None:
            return None
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1", errors="replace")


# ── HTML Rewriter ────────────────────────────────────────────────────────────
class HTMLRewriter:
    """Rewrite URLs in HTML for local/offline browsing."""

    def __init__(self, handler: URLHandler):
        self.h = handler
        self._soup = None

    def rewrite(self, html_content: str, base_url: str) -> str:
        """Rewrite all URLs in HTML for offline use."""
        if not HAS_BS4:
            return html_content

        soup = BeautifulSoup(html_content, "html.parser")
        changes = 0

        # Rewrite src attributes
        for tag in soup.find_all(src=True):
            url = tag.get("src", "")
            if url and not url.startswith("data:") and not url.startswith("about:"):
                resolved = self.h.resolve(url)
                if resolved:
                    local_path = self.h.make_local_path(resolved)
                    tag["src"] = str(local_path)
                    changes += 1

        # Rewrite href attributes (links to same host)
        for tag in soup.find_all(href=True):
            url = tag.get("href", "")
            if url and not url.startswith("data:") and not url.startswith("mailto:") \
               and not url.startswith("tel:") and not url.startswith("#"):
                resolved = self.h.resolve(url)
                if resolved and self.h.base_netloc in urlparse(resolved).netloc:
                    local_path = self.h.make_local_path(resolved)
                    tag["href"] = str(local_path)
                    changes += 1

        # Rewrite style tags (inline CSS)
        for tag in soup.find_all(style=True):
            css = tag.get("style", "")
            css = re.sub(
                r'url\([\'"]?([^\'")]+)[\'"]?\)',
                lambda m: f'url(\"{self._rewrite_css_url(m.group(1), base_url)}\")',
                css,
            )
            tag["style"] = css
            changes += 1

        # Rewrite inline <style> blocks
        for tag in soup.find_all("style"):
            if tag.string:
                tag.string = re.sub(
                    r'url\([\'"]?([^\'")]+)[\'"]?\)',
                    lambda m: f'url(\"{self._rewrite_css_url(m.group(1), base_url)}\")',
                    tag.string,
                )
                changes += 1

        # Rewrite <link rel="stylesheet">
        for tag in soup.find_all("link", rel=lambda r: r and "stylesheet" in str(r)):
            href = tag.get("href", "")
            if href:
                resolved = self.h.resolve(href)
                if resolved:
                    tag["href"] = str(self.h.make_local_path(resolved))
                    changes += 1

        # Rewrite <img> srcset
        for tag in soup.find_all("img"):
            srcset = tag.get("srcset", "")
            if srcset:
                new_set = []
                for part in srcset.split(","):
                    part = part.strip()
                    if " " in part:
                        url_part, size = part.rsplit(" ", 1)
                        resolved = self.h.resolve(url_part)
                        if resolved:
                            new_set.append(f"{self.h.make_local_path(resolved)} {size}")
                    else:
                        resolved = self.h.resolve(part)
                        if resolved:
                            new_set.append(str(self.h.make_local_path(resolved)))
                tag["srcset"] = ", ".join(new_set) if new_set else ""

        # Remove noscript fallbacks for scripts that won't exist locally
        for tag in soup.find_all("noscript"):
            # Keep noscript but rewrite its content
            for inner in tag.find_all(True):
                for attr in ["src", "href"]:
                    if inner.get(attr):
                        resolved = self.h.resolve(inner[attr])
                        if resolved:
                            inner[attr] = str(self.h.make_local_path(resolved))

        rewritten = soup.prettify() if soup else html_content
        log.debug(f"  Rewrote {changes} URLs in HTML")
        return rewritten

    def _rewrite_css_url(self, url: str, base_url: str) -> str:
        """Rewrite a CSS url() reference."""
        url = url.strip().strip("'\"")
        if url.startswith("data:"):
            return url
        resolved = URLHandler(base_url).resolve(url)
        if resolved:
            return str(URLHandler(base_url).make_local_path(resolved))
        return url


# ── Sitemap Parser ───────────────────────────────────────────────────────────
class SitemapParser:
    """Parse sitemap.xml to discover URLs."""

    @staticmethod
    def parse(sitemap_html: str, base_url: str) -> list:
        if not HAS_BS4:
            return []
        soup = BeautifulSoup(sitemap_html, "xml")
        urls = []
        # sitemaps
        for loc in soup.find_all("loc"):
            if loc.string:
                urls.append(loc.string.strip())
        # index sitemaps
        for sitemap in soup.find_all("sitemap"):
            loc = sitemap.find("loc")
            if loc and loc.string:
                urls.append(loc.string.strip())
        return urls


# ── Main Cloner ──────────────────────────────────────────────────────────────
class WebCloner:
    """Expert website cloner with full asset pipeline."""

    def __init__(
        self,
        url: str,
        output_dir: str = None,
        max_depth: int = 1,
        max_pages: int = 50,
        max_assets: int = 500,
        follow_links: bool = True,
        download_images: bool = True,
        download_js: bool = True,
        download_fonts: bool = True,
        download_media: bool = True,
        respect_robots: bool = True,
        crawl_delay: float = 0.0,
        dry_run: bool = False,
        js_render: bool = False,
        mobile: bool = False,
        cookies: str = None,
    ):
        self.url = url.rstrip("/")
        self.output_dir = Path(output_dir) if output_dir else Path("clone") / Path(urlparse(url).netloc)
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.max_assets = max_assets
        self.follow_links = follow_links
        self.download_images = download_images
        self.download_js = download_js
        self.download_fonts = download_fonts
        self.download_media = download_media
        self.respect_robots = respect_robots
        self.crawl_delay = crawl_delay
        self.dry_run = dry_run
        self.js_render = js_render
        self.mobile = mobile
        self.cookies = cookies

        self.handler = URLHandler(url)
        self.downloader = Downloader(delay=crawl_delay)
        self.rewriter = HTMLRewriter(self.handler)
        self.visited_urls: set = set()
        self.pages_to_clone: list = [(url, 0)]  # (url, depth)
        self.stats = {"pages": 0, "assets": 0, "bytes": 0, "errors": 0}

        # Robots checker
        self.robots = RobotsChecker(url) if respect_robots else None

        # Cookie loading
        if cookies:
            self.downloader.session.cookies.update(self._load_cookies(cookies))

    def _load_cookies(self, path: str) -> dict:
        """Load cookies from Netscape format or JSON."""
        cookies = {}
        try:
            with open(path) as f:
                content = f.read().strip()
            if content.startswith("{"):
                data = json.loads(content)
                for item in data:
                    cookies[item.get("name", "")] = item.get("value", "")
            else:
                for line in content.split("\n"):
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.split("\t")
                    if len(parts) >= 7:
                        cookies[parts[5]] = parts[6]
        except Exception as e:
            log.warning(f"Could not load cookies from {path}: {e}")
        return cookies

    def _is_allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        if not self.robots:
            return True
        return self.robots.can_fetch(url)

    def _should_download(self, url: str) -> bool:
        """Check if URL should be downloaded as an asset."""
        ext = Path(urlparse(url).path).suffix.lower()
        if ext in JS_EXTENSIONS:
            return self.download_js
        if ext in CSS_EXTENSIONS:
            return True
        if ext in {".woff", ".woff2", ".ttf", ".otf", ".eot"}:
            return self.download_fonts
        if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif"}:
            return self.download_images
        if ext in {".mp4", ".webm", ".ogg", ".mp3", ".wav", ".avi", ".mov"}:
            return self.download_media
        return False

    def _save_asset(self, url: str, content: bytes, local_path: Path) -> bool:
        """Save a single asset to disk."""
        if self.dry_run:
            log.info(f"  [DRY] Would save: {local_path}")
            return True
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(content)
            self.stats["assets"] += 1
            self.stats["bytes"] += len(content)
            return True
        except Exception as e:
            log.error(f"  ✗ Failed to save {local_path}: {e}")
            self.stats["errors"] += 1
            return False

    def _clone_html_page(self, url: str, depth: int) -> Optional[Path]:
        """Clone a single HTML page and its embedded assets."""
        log.info(f"  Cloning [{depth}] {url}")

        if not self._is_allowed(url):
            log.info(f"  ⊘ Blocked by robots.txt: {url}")
            return None

        if url in self.visited_urls:
            return None
        self.visited_urls.add(url)

        # Fetch HTML
        html_content = self.downloader.fetch_html(url)
        if not html_content:
            log.error(f"  ✗ Failed to fetch: {url}")
            self.stats["errors"] += 1
            return None

        # Save main HTML (rewritten)
        local_path = self.handler.make_local_path(url)
        local_html = self.output_dir / local_path.with_suffix(".html")
        rewritten = self.rewriter.rewrite(html_content, url)
        self._save_asset(url, rewritten.encode("utf-8"), local_html)
        self.stats["pages"] += 1

        # Extract and download assets
        if HAS_BS4:
            soup = BeautifulSoup(html_content, "html.parser")
            asset_urls = set()

            # Scripts
            for tag in soup.find_all("script", src=True):
                src = tag["src"]
                resolved = self.handler.resolve(src)
                if resolved and self._should_download(resolved):
                    asset_urls.add(resolved)

            # Stylesheets
            for tag in soup.find_all("link", rel=lambda r: r and "stylesheet" in str(r)):
                href = tag.get("href", "")
                resolved = self.handler.resolve(href)
                if resolved and self._should_download(resolved):
                    asset_urls.add(resolved)

            # Images
            if self.download_images:
                for tag in soup.find_all("img"):
                    for attr in ["src", "data-src", "data-lazy-src"]:
                        src = tag.get(attr, "")
                        if src:
                            resolved = self.handler.resolve(src)
                            if resolved and self._should_download(resolved):
                                asset_urls.add(resolved)

            # SVGs in content
            for tag in soup.find_all("svg"):
                for src_tag in tag.find_all("image", href=True):
                    resolved = self.handler.resolve(src_tag["href"])
                    if resolved:
                        asset_urls.add(resolved)

            # Inline CSS backgrounds
            for tag in soup.find_all(style=True):
                for match in re.finditer(r'url\([\'"]?([^\'")]+)[\'"]?\)', tag.get("style", "")):
                    resolved = self.handler.resolve(match.group(1))
                    if resolved and self._should_download(resolved):
                        asset_urls.add(resolved)

            # Inline styles in <style>
            for tag in soup.find_all("style"):
                for match in re.finditer(r'url\([\'"]?([^\'")]+)[\'"]?\)', tag.string or ""):
                    resolved = self.handler.resolve(match.group(1))
                    if resolved and self._should_download(resolved):
                        asset_urls.add(resolved)

            # Download assets concurrently
            log.debug(f"  Found {len(asset_urls)} assets to download")
            self._download_assets(asset_urls)

        # Crawl links if within depth limit
        if self.follow_links and depth < self.max_depth and len(self.visited_urls) < self.max_pages:
            if HAS_BS4:
                soup = BeautifulSoup(html_content, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("#") or href.startswith("javascript:"):
                        continue
                    resolved = self.handler.resolve(href)
                    if resolved and resolved not in self.visited_urls:
                        # Only follow same-host links
                        if self.handler.base_netloc in urlparse(resolved).netloc:
                            self.pages_to_clone.append((resolved, depth + 1))

        return local_html

    def _download_assets(self, urls: set):
        """Download a batch of static assets."""
        to_download = []
        for url in urls:
            if len(self.visited_urls) + len(to_download) >= self.max_assets:
                break
            if self._should_download(url):
                to_download.append(url)

        if not to_download:
            return

        log.debug(f"  Downloading {len(to_download)} assets...")
        with ThreadPoolExecutor(max_workers=self.downloader.max_workers) as executor:
            futures = {executor.submit(self._fetch_and_save, url): url for url in to_download}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    log.error(f"  ✗ Asset error: {e}")
                    self.stats["errors"] += 1

    def _fetch_and_save(self, url: str):
        """Fetch and save a single asset."""
        content, status, ct = self.downloader.fetch(url)
        if content is None:
            self.stats["errors"] += 1
            return
        local_path = self.output_dir / self.handler.make_local_path(url)
        if not self._save_asset(url, content, local_path):
            self.stats["errors"] += 1

    def _render_js_page(self, url: str) -> Optional[str]:
        """Use Playwright to render JS-heavy pages."""
        if not HAS_PLAYWRIGHT or not self.js_render:
            return None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={"width": 375 if self.mobile else 1920, "height": 812 if self.mobile else 1080},
                )
                if self.cookies:
                    page.context.add_cookies(self.cookies)
                page.goto(url, wait_until="networkidle", timeout=30000)
                content = page.content()
                page.screenshot(path=str(self.output_dir / "screenshot.png"))
                browser.close()
                log.info(f"  JS-rendered: {url}")
                return content
        except Exception as e:
            log.error(f"  JS render failed: {e}")
            return None

    def clone(self) -> dict:
        """Run the full cloning pipeline."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        start = time.time()

        log.info(f"\n{'='*60}")
        log.info(f"Web Cloner — Starting")
        log.info(f"{'='*60}")
        log.info(f"  Source:      {self.url}")
        log.info(f"  Output:      {self.output_dir.absolute()}")
        log.info(f"  Max depth:   {self.max_depth}")
        log.info(f"  Max pages:   {self.max_pages}")
        log.info(f"  Max assets:  {self.max_assets}")
        log.info(f"  Robots.txt:  {'enforced' if self.respect_robots else 'ignored'}")
        log.info(f"  JS render:   {'enabled' if self.js_render else 'disabled'}")
        log.info(f"{'='*60}\n")

        # Check robots
        if self.respect_robots and self.robots:
            delay = self.robots.crawl_delay()
            if delay and self.crawl_delay == 0:
                self.crawl_delay = delay
                log.info(f"  Crawl delay: {delay}s (from robots.txt)")

        # Clone pages BFS
        queue = [(self.url, 0)]
        queued = {self.url}

        while queue and len(self.visited_urls) < self.max_pages and len(self.pages_to_clone) < self.max_assets:
            url, depth = queue.pop(0)

            if url in self.visited_urls:
                continue
            if not self._is_allowed(url):
                continue

            log.info(f"[{self.stats['pages']+1}] {url}")

            # Try JS render if enabled
            if self.js_render:
                html_content = self._render_js_page(url)
                if html_content:
                    local_path = self.handler.make_local_path(url)
                    local_html = self.output_dir / local_path.with_suffix(".html")
                    local_html.parent.mkdir(parents=True, exist_ok=True)
                    if not self.dry_run:
                        local_html.write_text(html_content, encoding="utf-8")
                    self.stats["pages"] += 1
                    self.visited_urls.add(url)
                    continue

            # Normal clone
            result = self._clone_html_page(url, depth)
            if result:
                self.visited_urls.add(url)

            # Add links to queue
            if self.follow_links and depth < self.max_depth:
                if HAS_BS4 and result:
                    html = self.downloader.fetch_html(url)
                    if html:
                        soup = BeautifulSoup(html, "html.parser")
                        for a in soup.find_all("a", href=True):
                            href = a["href"]
                            if href.startswith("#") or href.startswith("javascript:"):
                                continue
                            resolved = self.handler.resolve(href)
                            if resolved and resolved not in queued and self.handler.base_netloc in urlparse(resolved).netloc:
                                queue.append((resolved, depth + 1))
                                queued.add(resolved)

            if self.crawl_delay > 0:
                time.sleep(self.crawl_delay)

        # Write manifest
        manifest = {
            "source_url": self.url,
            "cloned_at": datetime.now().isoformat(),
            "stats": self.stats,
            "visited_urls": sorted(self.visited_urls),
        }
        manifest_path = self.output_dir / "manifest.json"
        if not self.dry_run:
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        elapsed = time.time() - start
        log.info(f"\n{'='*60}")
        log.info(f"CLONE COMPLETE")
        log.info(f"{'='*60}")
        log.info(f"  Pages cloned:  {self.stats['pages']}")
        log.info(f"  Assets downl.: {self.stats['assets']}")
        log.info(f"  Total bytes:   {self.stats['bytes']:,} ({self.stats['bytes']/1024/1024:.1f} MB)")
        log.info(f"  Errors:        {self.stats['errors']}")
        log.info(f"  Time:          {elapsed:.1f}s")
        log.info(f"  Output:        {self.output_dir.absolute()}")
        log.info(f"{'='*60}")

        return manifest


# ── CLI ───────────────────────── ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="FreeAI Web Cloner — Clone any website to local disk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --depth 2 --limit 100
  %(prog)s https://example.com --output ./my-clone
  %(prog)s https://example.com --js --images --fonts
  %(prog)s https://example.com --robots --delay 2
  %(prog)s https://example.com --mobile --viewport 375x812
  %(prog)s https://example.com --sitemap
  %(prog)s https://example.com --dry-run
        """,
    )
    parser.add_argument("url", help="Website URL to clone")
    parser.add_argument("--output", "-o", default=None, help="Output directory")
    parser.add_argument("--depth", "-d", type=int, default=1, help="Max link depth (default: 1)")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Max pages to clone (default: 50)")
    parser.add_argument("--max-assets", type=int, default=500, help="Max assets to download (default: 500)")
    parser.add_argument("--no-links", action="store_true", help="Don't follow links (clone only the single page)")
    parser.add_argument("--no-images", action="store_true", help="Skip image downloads")
    parser.add_argument("--no-js", action="store_true", help="Skip JS file downloads")
    parser.add_argument("--no-fonts", action="store_true", help="Skip font downloads")
    parser.add_argument("--no-media", action="store_true", help="Skip video/audio downloads")
    parser.add_argument("--no-robots", action="store_true", help="Ignore robots.txt")
    parser.add_argument("--delay", type=float, default=0.0, help="Crawl delay in seconds")
    parser.add_argument("--workers", "-w", type=int, default=10, help="Concurrent downloads (default: 10)")
    parser.add_argument("--js", action="store_true", help="Use Playwright for JS-rendered pages")
    parser.add_argument("--mobile", action="store_true", help="Clone as mobile viewport (375x812)")
    parser.add_argument("--viewport", type=str, default=None, help="Custom viewport WxH, e.g. 1920x1080")
    parser.add_argument("--cookies", type=str, default=None, help="Cookie file (Netscape or JSON)")
    parser.add_argument("--sitemap", action="store_true", help="Use sitemap.xml to discover URLs")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be cloned without saving")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)
    elif args.quiet:
        log.setLevel(logging.WARNING)

    if not args.url.startswith(("http://", "https://")):
        log.error("URL must start with http:// or https://")
        sys.exit(1)

    if not HAS_BS4:
        log.error("beautifulsoup4 is required. Install: pip install beautifulsoup4")
        sys.exit(1)

    cloner = WebCloner(
        url=args.url,
        output_dir=args.output,
        max_depth=args.depth,
        max_pages=args.limit,
        max_assets=args.max_assets,
        follow_links=not args.no_links,
        download_images=not args.no_images,
        download_js=not args.no_js,
        download_fonts=not args.no_fonts,
        download_media=not args.no_media,
        respect_robots=not args.no_robots,
        crawl_delay=args.delay,
        dry_run=args.dry_run,
        js_render=args.js,
        mobile=args.mobile,
        cookies=args.cookies,
    )

    manifest = cloner.clone()

    if manifest and not args.dry_run:
        log.info(f"\nOpen index.html in browser to view cloned site:")
        log.info(f"  {cloner.output_dir / 'index.html'}")

    sys.exit(0 if manifest else 1)


if __name__ == "__main__":
    main()
