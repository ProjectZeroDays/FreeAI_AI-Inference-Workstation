#!/usr/bin/env python3
"""Tests for DarkWebScanner agent."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from darkweb_scanner_agent import DarkWebScanner


def test_describe():
    scanner = DarkWebScanner()
    result = scanner.describe()
    assert result['name'] == 'darkweb_scanner'
    assert 'description' in result
    assert result['category'] == 'red_teaming'
    assert 'DARKWEB_SCANNER' in result['triggers']
    assert result['safety'] == 'read-only, no exploitation, Tor-isolated'


def test_capabilities():
    scanner = DarkWebScanner()
    desc = scanner.describe()
    assert 'capabilities' in desc
    caps = desc['capabilities']
    assert 'onion_scan' in caps
    assert 'index_build' in caps
    assert 'safety_check' in caps


def test_tor_availability_offline():
    scanner = DarkWebScanner(tor_socks_port=19999)
    assert scanner.is_tor_available() is False


def test_fetch_non_onion():
    scanner = DarkWebScanner()
    result = scanner.fetch_onion('https://example.com')
    assert 'error' in result
    assert 'not an .onion URL' in result['error']


def test_quick_lookup_non_onion():
    scanner = DarkWebScanner()
    result = scanner.quick_lookup('example.com')
    assert 'error' in result


def test_generate_report_empty():
    scanner = DarkWebScanner()
    report = scanner.generate_report('dict')
    assert 'scan_time' in report
    assert 'stats' in report
    assert 'pages' in report
    assert report['summary']['total_pages'] == 0


def test_export_csv_empty():
    scanner = DarkWebScanner()
    csv_out = scanner.export_csv()
    assert 'url' in csv_out
    assert 'title' in csv_out
    assert 'status' in csv_out


def test_crawl_zero_pages():
    scanner = DarkWebScanner()
    result = scanner.crawl('http://nonexistent123onion.onion/', max_depth=0, max_pages=0)
    assert result['stats']['pages_crawled'] == 0
    assert result['stats']['pages_with_content'] == 0
    assert result['stats']['pages_with_errors'] == 0


def test_default_config():
    scanner = DarkWebScanner()
    assert scanner.tor_socks_port == 9050
    assert scanner.tor_http_port == 9051
    assert scanner.timeout == 30
    assert scanner.MAX_DEPTH == 3
    assert scanner.MAX_PAGES == 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
