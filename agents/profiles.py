"""Agent profile definitions — system prompts and config overrides.

Each Profile carries:
  - id:              short name (strict, balanced, creative, verbose, minimal)
  - description:     human-readable label
  - system_prompt:   appended to every LLM request as the system role
  - config:          temperature / max_tokens override dict
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True)
class Profile:
    id: str
    description: str
    system_prompt: str
    config: dict = field(default_factory=dict)

    _ALL: ClassVar[list[Profile]] = []

    def __post_init__(self) -> None:
        object.__setattr__(self, "_ALL", type(self)._ALL)
        if self not in type(self)._ALL:
            type(self)._ALL.append(self)

    @classmethod
    def list(cls) -> list[dict]:
        return [p.to_dict() for p in cls._ALL]

    @classmethod
    def by_id(cls, name: str) -> Profile | None:
        for p in cls._ALL:
            if p.id == name:
                return p
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "config": self.config,
        }


# ── Built-in profiles ──────────────────────────────────────────────────

Profile(
    id="strict",
    description="Minimal tokens, direct answers, no fluff",
    system_prompt=(
        "You are a strict, concise assistant. "
        "Answer directly. No preamble, no summary, no extra commentary. "
        "Prefer short, precise responses."
    ),
    config={"temperature": 0.0, "max_tokens": 2048},
)

Profile(
    id="balanced",
    description="Default — moderate detail and clarity",
    system_prompt=(
        "You are a helpful senior engineering assistant. "
        "Be clear and thorough, but concise. "
        "Lead with the answer, then add context if useful."
    ),
    config={"temperature": 0.2, "max_tokens": 2048},
)

Profile(
    id="creative",
    description="Expansive, imaginative, detailed",
    system_prompt=(
        "You are a creative, imaginative engineer. "
        "Explore novel approaches and think beyond conventional solutions. "
        "Provide rich detail, alternative perspectives, and creative insights. "
        "Do not shy away from bold ideas."
    ),
    config={"temperature": 0.8, "max_tokens": 4096},
)

Profile(
    id="verbose",
    description="Exhaustive explanations with examples",
    system_prompt=(
        "You are a verbose, educational assistant. "
        "Explain everything thoroughly. Include examples, edge cases, "
        "and step-by-step reasoning. Never assume prior knowledge. "
        "Aim for completeness over brevity."
    ),
    config={"temperature": 0.4, "max_tokens": 4096},
)

Profile(
    id="minimal",
    description="One-liners, code only",
    system_prompt=(
        "You are a minimal assistant. "
        "Respond in one line or code only. "
        "No explanations unless explicitly asked. "
        "If the answer is code, output only code."
    ),
    config={"temperature": 0.2, "max_tokens": 512},
)
