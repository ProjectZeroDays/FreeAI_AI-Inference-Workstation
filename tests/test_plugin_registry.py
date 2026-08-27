"""MCP Registry unit tests — tests the PluginRegistry and SkillLoader classes directly."""
import sys
import os
import json
import tempfile
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents.plugin_registry import PluginRegistry, SkillLoader  # noqa: E402


class TestPluginRegistry:
    def test_list_empty(self, tmp_path):
        reg = PluginRegistry(tmp_path / "plugins.json")
        assert reg.list_plugins() == []

    def test_install_and_list(self, tmp_path):
        reg = PluginRegistry(tmp_path / "plugins.json")
        reg._plugins = {
            "p1": {"name": "p1", "category": "test", "enabled": True},
            "p2": {"name": "p2", "category": "web", "enabled": False},
        }
        result = reg.install_plugin("p1")
        assert result["status"] == "installed"
        assert result["plugin"] == "p1"
        installed = reg.list_plugins(enabled=True)
        assert len(installed) == 1
        assert installed[0]["name"] == "p1"

    def test_list_filtered_by_category(self, tmp_path):
        reg = PluginRegistry(tmp_path / "plugins.json")
        reg._plugins = {
            "p1": {"name": "p1", "category": "browser", "enabled": True},
            "p2": {"name": "p2", "category": "browser", "enabled": True},
            "p3": {"name": "p3", "category": "code", "enabled": True},
        }
        browsers = reg.list_plugins(category="browser")
        assert len(browsers) == 2
        all_enabled = reg.list_plugins(enabled=True)
        assert len(all_enabled) == 3
        all_disabled = reg.list_plugins(enabled=False)
        assert len(all_disabled) == 0

    def test_get_plugin_not_found(self, tmp_path):
        reg = PluginRegistry(tmp_path / "plugins.json")
        assert reg.get_plugin("nonexistent") is None

    def test_get_plugin_found(self, tmp_path):
        reg = PluginRegistry(tmp_path / "plugins.json")
        reg._plugins = {"p1": {"name": "p1"}}
        assert reg.get_plugin("p1")["name"] == "p1"

    def test_uninstall(self, tmp_path):
        reg = PluginRegistry(tmp_path / "plugins.json")
        reg._plugins = {"p1": {"name": "p1", "installed": True}}
        result = reg.uninstall_plugin("p1")
        assert result["status"] == "uninstalled"
        assert reg.get_plugin("p1").get("installed") is None

    def test_stats(self, tmp_path):
        reg = PluginRegistry(tmp_path / "plugins.json")
        reg._plugins = {
            "p1": {"name": "p1", "category": "a", "installed": True},
            "p2": {"name": "p2", "category": "b", "installed": False},
            "p3": {"name": "p3", "category": "a", "installed": True},
        }
        stats = reg.stats()
        assert stats["total"] == 3
        assert stats["installed"] == 2
        assert set(stats["categories"]) == {"a", "b"}


class TestSkillLoader:
    def test_discover_empty_dir(self, tmp_path):
        loader = SkillLoader([tmp_path])
        skills = loader.discover()
        assert skills == {}

    def test_discover_with_skill(self, tmp_path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: A test skill\ntriggers: test, debug\n---\nBody",
            encoding="utf-8")
        loader = SkillLoader([tmp_path])
        skills = loader.discover()
        assert "my-skill" in skills
        assert skills["my-skill"]["description"] == "A test skill"
        assert set(skills["my-skill"]["triggers"]) == {"test", "debug"}

    def test_discover_skips_dirs_without_skill_md(self, tmp_path):
        (tmp_path / "no-skill-file").mkdir()
        (tmp_path / "has-skill").mkdir()
        (tmp_path / "has-skill" / "SKILL.md").write_text(
            "---\nname: has-skill\n---\nBody")
        loader = SkillLoader([tmp_path])
        skills = loader.discover()
        assert list(skills.keys()) == ["has-skill"]

    def test_match_skills(self, tmp_path):
        skill_dir = tmp_path / "code-review"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: code-review\ndescription: Reviews code quality\ntriggers: review, refactor\n---\nBody")
        loader = SkillLoader([tmp_path])
        loader.discover()
        matches = loader.match_skills("review code")
        assert len(matches) == 1
        assert matches[0]["name"] == "code-review"

    def test_match_skills_no_match(self, tmp_path):
        skill_dir = tmp_path / "only-browser"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: browser\ndescription: Browser automation\n---\nBody")
        loader = SkillLoader([tmp_path])
        loader.discover()
        matches = loader.match_skills("quantum physics")
        assert matches == []

    def test_list_skills(self, tmp_path):
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ncategory: testing\n---\nBody")
        loader = SkillLoader([tmp_path])
        skills = loader.list_skills()
        assert len(skills) == 1
        assert skills[0]["name"] == "test-skill"

    def test_stats(self, tmp_path):
        (tmp_path / "s1").mkdir()
        (tmp_path / "s1" / "SKILL.md").write_text("---\nname: s1\n---\nx")
        loader = SkillLoader([tmp_path])
        loader.discover()
        stats = loader.stats()
        assert stats["total"] == 1
        assert stats["dirs_scanned"] == 1
