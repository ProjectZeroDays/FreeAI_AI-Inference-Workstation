"""Skills Aggregator — aggregates skills from all sources into a unified registry.

Sources:
  - skills/ (local project skills)
  - .agents/skills/ (Agent Zero skills)
  - .mimocode/skills/ (MiMoCode skills)
  - .codex/skills/ (Codex skills)
  - config/skills.json (manual additions)

Each skill is normalized to a common schema with deduplication by name/path.

Usage:
    from services.skills_aggregator import SkillsAggregator
    agg = SkillsAggregator()
    skills = agg.aggregate()
"""
import json
import re
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"

SKILLS_SOURCES = [
    ROOT / "skills",
    ROOT / ".agents" / "skills",
    ROOT / ".mimocode" / "skills",
    ROOT / ".codex" / "skills",
]

AGGREGATED_CACHE_PATH = CONFIG_DIR / "skills_aggregated.json"
CACHE_TTL = 300  # 5 minutes


class SkillEntry:
    """Normalized skill entry."""

    def __init__(self, name: str, path: str, description: str = "",
                 triggers: List[str] = None, category: str = "general",
                 auto_generated: bool = False, enabled: bool = True,
                 source: str = "", content: str = "", file_count: int = 0):
        self.name = name
        self.path = path
        self.description = description
        self.triggers = triggers or []
        self.category = category
        self.auto_generated = auto_generated
        self.enabled = enabled
        self.source = source
        self.content = content
        self.file_count = file_count
        self.last_updated = time.time()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "triggers": self.triggers,
            "category": self.category,
            "auto_generated": self.auto_generated,
            "enabled": self.enabled,
            "source": self.source,
            "file_count": self.file_count,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillEntry":
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            description=data.get("description", ""),
            triggers=data.get("triggers", []),
            category=data.get("category", "general"),
            auto_generated=data.get("auto_generated", False),
            enabled=data.get("enabled", True),
            source=data.get("source", ""),
            file_count=data.get("file_count", 0),
        )


class SkillsAggregator:
    """Aggregates skills from all configured sources."""

    def __init__(self):
        self._lock = threading.Lock()
        self._skills: Dict[str, SkillEntry] = {}
        self._cache: Optional[List[SkillEntry]] = None
        self._cache_time = 0.0
        self._sources = list(SKILLS_SOURCES)
        self._manual_path = CONFIG_DIR / "skills.json"

    def add_source(self, path: str):
        p = Path(path)
        if p.exists() and p not in self._sources:
            self._sources.append(p)

    def remove_source(self, path: str):
        p = Path(path)
        if p in self._sources:
            self._sources.remove(p)

    def aggregate(self, force_refresh: bool = False) -> List[SkillEntry]:
        with self._lock:
            now = time.time()
            if self._cache is not None and not force_refresh and (now - self._cache_time) < CACHE_TTL:
                return self._cache
            self._cache = []
            self._cache_time = now
            seen_paths = set()
            for source_dir in self._sources:
                self._scan_directory(source_dir, seen_paths)
            self._load_manual_skills()
            # Sort by name
            self._cache = sorted(self._cache, key=lambda s: s.name.lower())
        return self._cache

    def _scan_directory(self, dir_path: Path, seen: set):
        if not dir_path.exists():
            return
        for d in sorted(dir_path.iterdir()):
            if not d.is_dir():
                continue
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                continue
            key = str(skill_md)
            if key in seen:
                continue
            seen.add(key)
            try:
                content = skill_md.read_text(encoding="utf-8", errors="ignore")
                entry = self._parse_skill_md(d.name, key, content, str(d.parent))
                with self._lock:
                    self._skills[key] = entry
                    if self._cache is not None:
                        self._cache.append(entry)
            except (OSError, json.JSONDecodeError):
                continue

    def _parse_skill_md(self, dir_name: str, path: str, content: str,
                        source: str) -> SkillEntry:
        name = dir_name
        description = ""
        triggers = []
        category = "general"
        auto_generated = False
        enabled = True
        fm = re.match(r"^---\n([\s\S]*?)\n---", content)
        if fm:
            fm_text = fm.group(1)
            for line in fm_text.split("\n"):
                if line.startswith("name:"):
                    val = line.split(":", 1)[1].strip().strip('"').strip("'")
                    if val and val not in (">", "|"):
                        name = val
                elif line.startswith("description:"):
                    val = line.split(":", 1)[1].strip().strip('"')
                    if val not in (">", "|"):
                        description = val
                elif line.startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                elif line.startswith("auto_generated:"):
                    auto_generated = line.split(":", 1)[1].strip().lower() == "true"
                elif line.startswith("enabled:"):
                    enabled = line.split(":", 1)[1].strip().lower() == "true"
                elif line.strip().startswith("- ") and "triggers" in fm_text[:fm_text.find(line) if line in fm_text else 0]:
                    triggers.append(line.strip()[2:].strip().strip('"'))
        if not triggers:
            trigger_matches = re.findall(r"^\s*-\s+(\S.+)$", content, re.MULTILINE)
            triggers = [t.strip().strip('"').strip("'") for t in trigger_matches[:10]]
        file_count = sum(1 for _ in d.iterdir()) if (Path(path).parent / dir_name).exists() else 0
        return SkillEntry(
            name=name, path=path, description=description[:200],
            triggers=triggers, category=category,
            auto_generated=auto_generated, enabled=enabled,
            source=source, content=content, file_count=file_count,
        )

    def _load_manual_skills(self):
        if not self._manual_path.exists():
            return
        try:
            data = json.loads(self._manual_path.read_text(encoding="utf-8"))
            for entry in data.get("skills", []):
                key = entry.get("path", entry.get("name", ""))
                if key and key not in self._skills:
                    skill = SkillEntry.from_dict(entry)
                    self._skills[key] = skill
                    if self._cache is not None:
                        self._cache.append(skill)
        except (json.JSONDecodeError, OSError):
            pass

    def get_skill(self, name_or_path: str) -> Optional[SkillEntry]:
        with self._lock:
            for skill in self._skills.values():
                if skill.name == name_or_path or skill.path == name_or_path:
                    return skill
        return None

    def toggle_skill(self, name_or_path: str, enabled: bool) -> dict:
        with self._lock:
            for skill in self._skills.values():
                if skill.name == name_or_path or skill.path == name_or_path:
                    skill.enabled = enabled
                    return {"ok": True, "name": skill.name, "enabled": enabled}
        return {"error": "Skill not found"}

    def delete_skill(self, name_or_path: str) -> dict:
        with self._lock:
            for key, skill in list(self._skills.items()):
                if skill.name == name_or_path or skill.path == name_or_path:
                    del self._skills[key]
                    if self._cache:
                        self._cache = [s for s in self._cache if s.path != key]
                    return {"ok": True, "name": skill.name}
        return {"error": "Skill not found"}

    def update_skill(self, name_or_path: str, updates: dict) -> dict:
        with self._lock:
            for skill in self._skills.values():
                if skill.name == name_or_path or skill.path == name_or_path:
                    for k, v in updates.items():
                        if hasattr(skill, k):
                            setattr(skill, k, v)
                    skill.last_updated = time.time()
                    return {"ok": True, "skill": skill.to_dict()}
        return {"error": "Skill not found"}

    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._skills)
            enabled = sum(1 for s in self._skills.values() if s.enabled)
            auto = sum(1 for s in self._skills.values() if s.auto_generated)
            categories = {}
            sources = {}
            for s in self._skills.values():
                categories[s.category] = categories.get(s.category, 0) + 1
                sources[s.source] = sources.get(s.source, 0) + 1
            return {
                "total": total,
                "enabled": enabled,
                "auto_generated": auto,
                "disabled": total - enabled,
                "categories": categories,
                "sources": sources,
                "source_count": len(sources),
            }

    def search(self, query: str, category: Optional[str] = None) -> List[SkillEntry]:
        results = []
        q = query.lower()
        with self._lock:
            for skill in self._skills.values():
                if not skill.enabled:
                    continue
                if category and skill.category != category:
                    continue
                if (q in skill.name.lower() or
                    q in skill.description.lower() or
                    any(q in t.lower() for t in skill.triggers)):
                    results.append(skill)
        return results

    def export_to_file(self, path: str):
        skills_data = []
        with self._lock:
            for skill in self._skills.values():
                skills_data.append(skill.to_dict())
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(skills_data, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(p), "count": len(skills_data)}

    def import_from_file(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": "File not found"}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                skills = data
            elif isinstance(data, dict):
                skills = data.get("skills", [])
            else:
                return {"error": "Invalid format"}
            imported = 0
            for sd in skills:
                entry = SkillEntry.from_dict(sd)
                key = entry.path or entry.name
                with self._lock:
                    if key not in self._skills:
                        self._skills[key] = entry
                        imported += 1
            self._cache = None
            return {"ok": True, "imported": imported, "total": len(self._skills)}
        except (json.JSONDecodeError, OSError) as e:
            return {"error": "An error occurred while importing skills"}


_aggregator: Optional[SkillsAggregator] = None
_aggregator_lock = threading.Lock()


def get_aggregator() -> SkillsAggregator:
    global _aggregator
    if _aggregator is None:
        with _aggregator_lock:
            if _aggregator is None:
                _aggregator = SkillsAggregator()
    return _aggregator


def reset_aggregator():
    global _aggregator
    with _aggregator_lock:
        _aggregator = SkillsAggregator()
