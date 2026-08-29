#!/usr/bin/env python3
"""Security Scanner Agent — secrets detection, vulnerability scanning, CVE checks."""
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Regex patterns for common secrets
SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key": re.compile(r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?"),
    "github_token": re.compile(r"(?i)gh[pousr]_[A-Za-z0-9_]{36,}"),
    "generic_api_key": re.compile(r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([A-Za-z0-9_\-]{20,})['\"]?"),
    "password_assignment": re.compile(r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?([^'\"`\s]{8,})['\"]?"),
    "private_key": re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    "jwt_token": re.compile(r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+"),
    "slack_token": re.compile(r"xox[baprs]-[0-9a-zA-Z-]+"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z-_]{35}"),
    "stripe_key": re.compile(r"(?i)(sk|pk)_(live|test)_[0-9A-Za-z]{24,}"),
}

# Vulnerability patterns
VULN_PATTERNS = {
    "sql_injection": {
        "regex": re.compile(r"""(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\s+.*?(FROM|INTO|TABLE|WHERE)|(['\"]);\s*(SELECT|INSERT|UPDATE|DELETE)|(\bexec\s*\(|\bexecute\s*\()"""),
        "severity": "critical",
        "category": "injection",
    },
    "xss_reflected": {
        "regex": re.compile(r"""(?i)(document\.cookie|window\.location|location\.href)\s*=|<\s*script\b|javascript\s*:|on(error|load|click|mouseover)\s*="""),
        "severity": "high",
        "category": "xss",
    },
    "command_injection": {
        "regex": re.compile(r"""(?i)\bsubprocess\.(call|run|Popen)\s*\(.*?shell\s*=\s*True|\bexec\s*\(|\beval\s*\(|\bpopen\s*\([^)]*['\"`]"""),
        "severity": "critical",
        "category": "injection",
    },
    "hardcoded_secret": {
        "regex": re.compile(r"""(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{16,}['\"]?"""),
        "severity": "high",
        "category": "secrets",
    },
    "insecure_https": {
        "regex": re.compile(r"""(?i)https?://(?:127\.0\.0\.1|localhost)(?::\d+)?/?(?:[^'\"]*)"""),
        "severity": "low",
        "category": "config",
    },
    "deserialization": {
        "regex": re.compile(r"""(?i)\b(pickle\.load|yaml\.load\s*\([^)]*Loader|shelve\.open|marshal\.loads)\s*\("""),
        "severity": "high",
        "category": "injection",
    },
    "path_traversal": {
        "regex": re.compile(r"""(?i)\.\./|\.\.\\|%2e%2e"""),
        "severity": "medium",
        "category": "injection",
    },
}

# Exclusion patterns
DEFAULT_EXCLUSIONS = [
    ".git/",
    "__pycache__/",
    "*.pyc",
    "node_modules/",
    ".venv/",
    "venv/",
    "env/",
    ".env",
    "tests/",
    "test_",
    "_test.py",
    ".pytest_cache/",
    ".mimocode/",
    ".codex/",
    ".claude/",
    "logs/",
    "reports/",
    "data/",
]


class SecurityScanner:
    """Scans codebase for secrets, vulnerabilities, and dependency CVEs."""

    def __init__(self, config_path=None):
        self.findings = []
        self.scan_dirs = []
        self.include_tests = False
        self.config = self._load_config(config_path)
        self.exclude_patterns = self.config.get("exclusions", DEFAULT_EXCLUSIONS)
        self.severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    def _load_config(self, config_path):
        path = Path(config_path) if config_path else ROOT.parent / "config" / "security.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "rules": {},
            "exclusions": DEFAULT_EXCLUSIONS,
            "scan_dirs": ["config", "scripts", "agents", "router", "browser"],
        }

    def describe(self):
        return {
            "name": "security_scanner",
            "description": "Scans codebase for secrets, SQLi, XSS, command injection, and dependency CVEs",
            "category": "security",
            "capabilities": ["secrets_scan", "vuln_scan", "cve_scan", "report"],
        }

    def set_dirs(self, dirs):
        self.scan_dirs = [Path(d) if isinstance(d, str) else d for d in dirs]
        return self

    def set_include_tests(self, value):
        self.include_tests = value
        return self

    def _should_exclude(self, path_str):
        for pattern in self.exclude_patterns:
            if pattern.startswith("*"):
                if path_str.endswith(pattern):
                    return True
            elif pattern in path_str:
                return True
        return False

    def scan_secrets(self, directory):
        """Scan a directory for leaked secrets."""
        findings = []
        if not directory.exists():
            return findings
        for fp in sorted(directory.rglob("*")):
            if fp.is_dir():
                continue
            rel = str(fp.relative_to(directory.parent))
            if self._should_exclude(rel):
                continue
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore")[:50000]
            except OSError:
                continue
            for name, pattern in SECRET_PATTERNS.items():
                matches = pattern.findall(text)
                if matches:
                    for i, line in enumerate(text.split("\n"), 1):
                        if pattern.search(line):
                            findings.append({
                                "type": "secret",
                                "subtype": name,
                                "file": str(fp),
                                "line": i,
                                "severity": "critical" if name in ("aws_access_key", "private_key", "github_token") else "high",
                                "category": "secrets",
                                "snippet": line.strip()[:200],
                            })
                            break
        return findings

    def scan_vulnerabilities(self, directory):
        """Scan source files for common vulnerability patterns."""
        findings = []
        if not directory.exists():
            return findings
        code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java", ".c", ".cpp", ".rb", ".php", ".html", ".vue", ".svelte"}
        for fp in sorted(directory.rglob("*")):
            if fp.is_dir():
                continue
            if fp.suffix not in code_exts:
                continue
            rel = str(fp.relative_to(directory.parent))
            if not self.include_tests and ("test" in rel.lower() or "_test." in rel):
                continue
            if self._should_exclude(rel):
                continue
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore")[:100000]
            except OSError:
                continue
            for vuln_name, vuln_info in VULN_PATTERNS.items():
                for i, line in enumerate(text.split("\n"), 1):
                    if vuln_info["regex"].search(line):
                        findings.append({
                            "type": "vulnerability",
                            "subtype": vuln_name,
                            "file": str(fp),
                            "line": i,
                            "severity": vuln_info["severity"],
                            "category": vuln_info["category"],
                            "snippet": line.strip()[:200],
                        })
                        break
        return findings

    def scan_dependencies(self):
        """Scan Python dependencies for known CVEs using pip-audit."""
        findings = []
        try:
            result = subprocess.run(
                ["pip-audit", "--json"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                for item in data.get("vulns", []):
                    pkg = item.get("package", {})
                    vuln = item.get("vuln", {})
                    findings.append({
                        "type": "cve",
                        "subtype": vuln.get("id", "unknown"),
                        "file": f"pkg:{pkg.get('name', 'unknown')}=={pkg.get('version', 'unknown')}",
                        "line": 0,
                        "severity": vuln.get("severity", "medium").lower(),
                        "category": "dependency",
                        "snippet": vuln.get("description", "")[:200],
                        "fix_available": vuln.get("fix_available", False),
                    })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return findings

    def run_scan(self, scan_dirs=None, include_tests=False):
        """Run full security scan across configured directories."""
        self.findings = []
        dirs = scan_dirs or self.scan_dirs
        self.include_tests = include_tests or self.include_tests

        for dir_name in dirs:
            dir_path = ROOT / dir_name
            self.findings.extend(self.scan_secrets(dir_path))
            self.findings.extend(self.scan_vulnerabilities(dir_path))

        self.findings.extend(self.scan_dependencies())

        # Deduplicate by file+line+subtype
        seen = set()
        unique = []
        for f in self.findings:
            key = (f["file"], f["line"], f["subtype"])
            if key not in seen:
                seen.add(key)
                unique.append(f)
        self.findings = unique

        return self.get_report()

    def get_report(self):
        """Return structured security report."""
        critical = [f for f in self.findings if f["severity"] == "critical"]
        high = [f for f in self.findings if f["severity"] == "high"]
        medium = [f for f in self.findings if f["severity"] == "medium"]
        low = [f for f in self.findings if f["severity"] == "low"]

        sorted_findings = sorted(
            self.findings,
            key=lambda f: self.severity_order.get(f["severity"], 99),
        )

        return {
            "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_findings": len(self.findings),
            "summary": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
            },
            "findings": sorted_findings,
            "by_category": {
                "secrets": len([f for f in self.findings if f["category"] == "secrets"]),
                "injection": len([f for f in self.findings if f["category"] == "injection"]),
                "xss": len([f for f in self.findings if f["category"] == "xss"]),
                "dependency": len([f for f in self.findings if f["category"] == "dependency"]),
                "config": len([f for f in self.findings if f["category"] == "config"]),
            },
        }


if __name__ == "__main__":
    scanner = SecurityScanner()
    report = scanner.run_scan()
    print(json.dumps(report, indent=2))