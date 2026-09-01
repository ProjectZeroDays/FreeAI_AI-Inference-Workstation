# DarkWebScanner Agent
import json
import re
import socket
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent

class DarkWebScanner:
    """Dark web (.onion) content scanner via Tor proxy.

    Safely crawls and indexes .onion services through Tor.
    Returns structured results for display in the dark web browser UI.
    """

    TOR_SOCKS_PORT = 9050
    TOR_HTTP_PORT = 9051
    DEFAULT_TIMEOUT = 30
    MAX_DEPTH = 3
    MAX_PAGES = 50

    def __init__(self, tor_socks_port=None, tor_http_port=None, timeout=None):
        self.tor_socks_port = tor_socks_port or self.TOR_SOCKS_PORT
        self.tor_http_port = tor_http_port or self.TOR_HTTP_PORT
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.crawled = []
        self.findings = []
        self.stats = {}

    def describe(self):
        return {
            'name': 'darkweb_scanner',
            'description': 'Dark web (.onion) content scanner via Tor proxy -- safe read-only crawling, indexing, and structured result export for display in the dark web browser.',
            'category': 'red_teaming',
            'triggers': ['darkweb', 'onion', 'tor', 'dark web crawler', 'DARKWEB_SCANNER'],
            'capabilities': ['onion_scan', 'index_build', 'content_extract', 'safety_check', 'result_export'],
            'safety': 'read-only, no exploitation, Tor-isolated',
        }

    def is_tor_available(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect(('127.0.0.1', self.tor_socks_port))
            sock.close()
            return True
        except (socket.error, OSError):
            return False

    def _tor_opener(self):
        import urllib.request
        proxy = urllib.request.ProxyHandler({
            'http': f'socks5://127.0.0.1:{self.tor_socks_port}',
            'https': f'socks5://127.0.0.1:{self.tor_socks_port}',
        })
        return urllib.request.build_opener(proxy)

    def fetch_onion(self, url, max_content=50000):
        if not url.endswith('.onion'):
            return {'error': 'not an .onion URL', 'url': url}
        try:
            opener = self._tor_opener()
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.5',
            })
            with opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read(max_content)
                try:
                    text = raw.decode('utf-8', errors='replace')
                except Exception:
                    text = raw.decode('latin-1', errors='replace')
                links = re.findall(r'href=["\'][^"\'>]*\.onion[^"\'>]*["\']', text)
                title = ''
                m = re.search(r'<title[^>]*>([^<]+)</title>', text, re.IGNORECASE)
                if m:
                    title = m.group(1).strip()
                return {
                    'url': url,
                    'status': resp.status,
                    'title': title,
                    'content_length': len(text),
                    'onion_links': list(set(links))[:20],
                    'preview': text[:2000],
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                }
        except Exception as e:
            return {'url': url, 'error': str(e), 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}

    def crawl(self, start_url, max_depth=None, max_pages=None):
        max_depth = self.MAX_DEPTH if max_depth is None else max_depth
        max_pages = self.MAX_PAGES if max_pages is None else max_pages
        visited = set()
        queue = [(start_url, 0)]
        results = []

        while queue and len(visited) < max_pages:
            url, depth = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            result = self.fetch_onion(url)
            result['depth'] = depth
            results.append(result)
            self.crawled.append(result)

            if 'error' not in result and depth < max_depth:
                for link in result.get('onion_links', []):
                    if link not in visited:
                        queue.append((link, depth + 1))

        self.stats = {
            'start_url': start_url,
            'depth': max_depth,
            'pages_crawled': len(visited),
            'pages_with_content': len([r for r in results if 'error' not in r]),
            'pages_with_errors': len([r for r in results if 'error' in r]),
            'total_onion_links_found': len([l for r in results for l in r.get('onion_links', [])]),
        }
        return {'stats': self.stats, 'results': results}

    def quick_lookup(self, onion_host):
        if not onion_host.endswith('.onion'):
            onion_host = onion_host + '.onion'
        url = f'http://{onion_host}'
        return self.fetch_onion(url)

    def generate_report(self, format='json'):
        report = {
            'scan_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': self.stats,
            'pages': self.crawled,
            'summary': {
                'total_pages': len(self.crawled),
                'success': len([p for p in self.crawled if 'error' not in p]),
                'failed': len([p for p in self.crawled if 'error' in p]),
                'avg_content_length': int(sum(p.get('content_length', 0) for p in self.crawled) / max(len(self.crawled), 1)),
            },
        }
        if format == 'json':
            return json.dumps(report, indent=2, ensure_ascii=False)
        return report

    def export_csv(self):
        import csv, io
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(['url', 'title', 'status', 'content_length', 'onion_links_count', 'timestamp', 'error'])
        for p in self.crawled:
            writer.writerow([
                p.get('url', ''),
                p.get('title', ''),
                p.get('status', ''),
                p.get('content_length', 0),
                len(p.get('onion_links', [])),
                p.get('timestamp', ''),
                p.get('error', ''),
            ])
        return buf.getvalue()


if __name__ == '__main__':
    scanner = DarkWebScanner()
    info = scanner.describe()
    print(json.dumps(info, indent=2))
    print(f'Tor available: {scanner.is_tor_available()}')
