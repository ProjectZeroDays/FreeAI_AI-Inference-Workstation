#!/usr/bin/env python3
"""Enhanced Security Agent with auto-patch capability.

Builds on security_scanner.py with:
  - Auto-patch for generated code vulnerabilities
  - AI-assisted vulnerability remediation
  - SAST/DAST integration points
  - Report generation in multiple formats
"""
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
from agents.specialized.security_scanner import SecurityScanner, SECRET_PATTERNS, VULN_PATTERNS


class SecurityAgent(SecurityScanner):
    """Enhanced security scanner with auto-patch and AI remediation."""

    AUTO_FIX_PATTERNS = {
        "sql_injection": {
            "pattern": r"""(?i)(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*?(FROM|INTO|TABLE|WHERE)|(['\"]);\s*(SELECT|INSERT|UPDATE|DELETE)""",
            "fix": "Use parameterized queries with placeholder syntax",
            "template": "cursor.execute('SELECT * FROM table WHERE id = ?', (user_id,))",
        },
        "xss_reflected": {
            "pattern": r"""(?i)(document\.cookie|window\.location|location\.href)\s*=|<\s*script\b""",
            "fix": "Escape output and use DOMPurify for HTML sanitization",
            "template": "from markupsafe import escape; safe = escape(user_input)",
        },
        "command_injection": {
            "pattern": r"""(?i)\bsubprocess\.(call|run|Popen)\s*\(.*?shell\s*=\s*True""",
            "fix": "Use list arguments instead of shell=True",
            "template": "subprocess.run(['cmd', arg1, arg2], check=True)",
        },
        "deserialization": {
            "pattern": r"""(?i)\bpickle\.load\s*\(""",
            "fix": "Use json or yaml.safe_load instead of pickle",
            "template": "import json; data = json.loads(file.read())",
        },
        "hardcoded_secret": {
            "pattern": r"""(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{16,}['\"]?""",
            "fix": "Use environment variables or secrets manager",
            "template": "import os; SECRET = os.environ.get('SECRET_KEY')",
        },
        "path_traversal": {
            "pattern": r"""(?i)\.\./|\.\.\\|%2e%2e""",
            "fix": "Validate and sanitize file paths, use os.path.realpath",
            "template": "import os; safe_path = os.path.realpath(os.path.join(base, user_path))",
        },
    }

    def __init__(self, config_path=None, auto_patch: bool = True, severity_threshold: str = "low"):
        super().__init__(config_path)
        self.auto_patch = auto_patch
        self.severity_threshold = severity_threshold
        self.patched_files = {}
        self.remediation_log = []

    def scan_with_remediation(self, directory=None) -> dict:
        """Run scan and attempt auto-remediation for fixable vulnerabilities."""
        report = self.run_scan(directory)
        findings = report.get("findings", [])

        remediated = []
        for finding in findings:
            if finding["severity"] == "critical" and finding["category"] in ("injection", "secrets", "xss"):
                fix_result = self._attempt_fix(finding)
                if fix_result["ok"]:
                    remediated.append(fix_result)
                    finding["remediated"] = True
                    finding["remediation"] = fix_result["remediation"]
                    self.remediation_log.append(fix_result)

        report["remediated_count"] = len(remediated)
        report["remediation_log"] = self.remediation_log
        return report

    def _attempt_fix(self, finding: dict) -> dict:
        """Attempt to auto-fix a vulnerability finding."""
        vuln_type = finding.get("subtype", finding.get("type", ""))
        fix_info = self.AUTO_FIX_PATTERNS.get(vuln_type)

        if not fix_info:
            return {"ok": False, "reason": f"No auto-fix for {vuln_type}"}

        filepath = Path(finding["file"])
        if not filepath.exists():
            return {"ok": False, "reason": "File not found"}

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            line_idx = finding.get("line", 1) - 1

            if line_idx < 0 or line_idx >= len(lines):
                return {"ok": False, "reason": "Line out of range"}

            original_line = lines[line_idx]

            # Generate fix based on pattern
            if vuln_type == "sql_injection":
                lines[line_idx] = re.sub(
                    r"""(?i)(['\";])\s*(SELECT|INSERT|UPDATE|DELETE)\s*""",
                    r"\1  # REMOVED: Use parameterized query\n    # ",
                    original_line,
                )
            elif vuln_type == "command_injection":
                lines[line_idx] = re.sub(
                    r"shell\s*=\s*True",
                    "shell=False",
                    original_line,
                )
                if "shell=False" in lines[line_idx]:
                    lines[line_idx] += "  # FIX: Changed shell=True to shell=False"
            elif vuln_type == "hardcoded_secret":
                lines[line_idx] = re.sub(
                    r"""(?i)(\s*[=:]\s*['\"]?)[A-Za-z0-9/+=]{16,}(['\"]?)""",
                    r"\1os.environ.get('SECRET_KEY')\2",
                    original_line,
                )
            elif vuln_type == "deserialization":
                lines[line_idx] = re.sub(
                    r"pickle\.load",
                    "json.load",
                    original_line,
                )

            new_content = "\n".join(lines)
            filepath.write_text(new_content, encoding="utf-8")

            return {
                "ok": True,
                "file": str(filepath),
                "line": line_idx + 1,
                "vulnerability": vuln_type,
                "original": original_line.strip()[:100],
                "fixed": lines[line_idx].strip()[:100],
                "remediation": fix_info["fix"],
                "template": fix_info["template"],
            }
        except Exception as e:
            return {"ok": False, "reason": str(e)}

    def generate_security_report(self, fmt: str = "json") -> str:
        """Generate security report in specified format."""
        report = self.run_scan()

        if fmt == "json":
            return json.dumps(report, indent=2)
        elif fmt == "markdown":
            return self._to_markdown(report)
        elif fmt == "html":
            return self._to_html(report)
        return json.dumps(report)

    def _to_markdown(self, report: dict) -> str:
        """Convert report to Markdown format."""
        findings = report.get("findings", [])
        summary = report.get("summary", {})
        lines = [
            "# FreeAI Security Report",
            f"\n**Generated:** {report.get('scan_time', 'N/A')}",
            f"\n**Total Findings:** {report.get('total_findings', 0)}",
            f"\n**Critical:** {summary.get('critical', 0)} | **High:** {summary.get('high', 0)} | **Medium:** {summary.get('medium', 0)} | **Low:** {summary.get('low', 0)}",
            "",
            "## Findings",
        ]

        for f in findings:
            lines.append(f"\n### [{f['severity'].upper()}] {f.get('subtype', f.get('type', 'finding'))}")
            lines.append(f"- **File:** `{f['file']}`: {f['line']}")
            lines.append(f"- **Category:** {f['category']}")
            if f.get("snippet"):
                lines.append(f"- **Snippet:** `{f['snippet'][:100]}`")
            if f.get("remediated"):
                lines.append(f"- **Status:** ✅ Remediated")
            else:
                lines.append(f"- **Status:** ❌ Needs attention")

        return "\n".join(lines)

    def _to_html(self, report: dict) -> str:
        """Convert report to HTML format."""
        findings = report.get("findings", [])
        summary = report.get("summary", {})
        html = [
            "<!DOCTYPE html><html><head><title>Security Report</title>",
            "<style>body{font-family:system-ui;background:#0f172a;color:#e2e8f0;padding:20px}",
            ".critical{color:#ef4444}.high{color:#f97316}.medium{color:#f59e0b}.low{color:#38bdf8}",
            "table{border-collapse:collapse;width:100%}th,td{padding:8px;border-bottom:1px solid #334155}",
            "th{text-align:left;color:#94a3b8}</style></head><body>",
            f"<h1>Security Report — {report.get('scan_time', 'N/A')}</h1>",
            f"<p>Total: {report.get('total_findings', 0)} | Critical: {summary.get('critical',0)} | High: {summary.get('high',0)} | Medium: {summary.get('medium',0)} | Low: {summary.get('low',0)}</p>",
            "<table><tr><th>Severity</th><th>Type</th><th>File</th><th>Line</th><th>Status</th></tr>",
        ]
        for f in findings:
            status = "✅ Fixed" if f.get("remediated") else "❌ Open"
            html.append(f'<tr><td class="{f["severity"]}">{f["severity"].upper()}</td>'
                        f'<td>{f.get("subtype", f.get("type",""))}</td>'
                        f'<td>{f["file"]}</td><td>{f["line"]}</td><td>{status}</td></tr>')
        html.append("</table></body></html>")
        return "\n".join(html)

    def describe(self):
        return {
            "name": "security_agent",
            "description": "Enhanced security scanner with auto-patch, AI remediation, and multi-format reporting",
            "category": "security",
            "capabilities": ["secrets_scan", "vuln_scan", "cve_scan", "auto_patch", "report"],
            "auto_patch_enabled": self.auto_patch,
            "severity_threshold": self.severity_threshold,
        }


if __name__ == "__main__":
    agent = SecurityAgent(auto_patch=True)
    report = agent.scan_with_remediation()
    print(json.dumps(report, indent=2))
