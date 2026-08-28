#!/usr/bin/env python3
"""Dependency Agent API routes — integrated into dashboard backend.

This module provides the /api/dependency/* endpoints used by the
Dependency Agent dashboard page and the main backend.
"""
import json
import re
import threading
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent


class DependencyAgentAPI:
    """API handler for dependency analysis and patching."""

    def __init__(self, app):
        self.app = app
        self._config = {}
        self._lock = threading.Lock()
        self._register_routes()

    def _register_routes(self):
        """Register all dependency API routes."""

        @self.app.route("/api/dependency/analyze")
        def api_dependency_analyze():
            preset = self.app.request.args.get("preset", "balanced")
            try:
                from agents.specialized.dependency_agent import DependencyAgent
                agent = DependencyAgent(preset=preset)
                report = agent.analyze()
                with self._lock:
                    self._config["last_report"] = report
                return json.dumps(report, indent=2) if False else __import__("flask").jsonify(report)
            except Exception as e:
                import flask
                return flask.jsonify({"error": str(e), "total_packages": 0, "updates": [], "vulnerabilities": [], "updated_requirements": "# Error: " + str(e)}), 200

        @self.app.route("/api/dependency/fix", methods=["POST"])
        def api_dependency_fix():
            data = self.app.request.get_json(silent=True) or {}
            package = data.get("package", "")
            version = data.get("version", "")
            if not package or not version:
                import flask
                return flask.jsonify({"error": "package and version required"}), 400
            try:
                req_path = ROOT / "requirements.txt"
                if req_path.exists():
                    content = req_path.read_text(encoding="utf-8")
                    pattern = re.compile(rf"^{re.escape(package)}(?:[=~^<>!].*?)?$", re.MULTILINE)
                    new_line = f"{package}>={version}  # Auto-fixed by Dependency Agent"
                    new_content = pattern.sub(new_line, content)
                    if new_content != content:
                        req_path.write_text(new_content, encoding="utf-8")
                import flask
                return flask.jsonify({"ok": True, "package": package, "version": version, "message": f"Fixed {package} to >= {version}"})
            except Exception as e:
                import flask
                return flask.jsonify({"error": str(e)}), 500

        @self.app.route("/api/dependency/patch", methods=["POST"])
        def api_dependency_patch():
            preset = "balanced"
            try:
                from agents.specialized.dependency_agent import DependencyAgent
                agent = DependencyAgent(preset=preset)
                result = agent.auto_patch(backup=True)
                import flask
                return flask.jsonify(result)
            except Exception as e:
                import flask
                return flask.jsonify({"ok": False, "error": str(e)}), 500

        @self.app.route("/api/dependency/settings", methods=["GET", "POST"])
        def api_dependency_settings():
            import flask
            if self.app.request.method == "POST":
                data = self.app.request.get_json(silent=True) or {}
                with self._lock:
                    self._config.update(data)
                return flask.jsonify({"ok": True, "settings": self._config})
            with self._lock:
                return flask.jsonify(self._config)

        @self.app.route("/api/dependency/describe")
        def api_dependency_describe():
            try:
                from agents.specialized.dependency_agent import DependencyAgent
                agent = DependencyAgent()
                import flask
                return flask.jsonify(agent.describe())
            except Exception as e:
                import flask
                return flask.jsonify({"error": str(e)}), 500

        @self.app.route("/api/dependency/resources")
        def api_dependency_resources():
            try:
                from agents.specialized.intelligent_resources import get_all_resources
                catalog = get_all_resources()
                import flask
                return flask.jsonify(catalog)
            except Exception as e:
                import flask
                return flask.jsonify({"error": str(e)}), 500

        @self.app.route("/api/dependency/plugins")
        def api_dependency_plugins():
            try:
                from agents.specialized.intelligent_plugins import get_plugins
                plugins = get_plugins()
                import flask
                return flask.jsonify(plugins)
            except Exception as e:
                import flask
                return flask.jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Standalone test
    from flask import Flask
    app = Flask(__name__)
    api = DependencyAgentAPI(app)
    with app.test_client() as client:
        r = client.get("/api/dependency/describe")
        print(r.get_json())
