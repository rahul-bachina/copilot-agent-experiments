"""Read skill and topic metadata from SKILL.md front matter or a JSON object.

The parser accepts the subset this repository uses: a name, a folded or
single-line description, and an optional triggers list. It does not import
PyYAML. A file it cannot read raises SkillParseError.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from .tokens import content_tokens, token_set
except ImportError:  # python src/report.py puts this directory on sys.path
    from tokens import content_tokens, token_set


class SkillParseError(ValueError):
    """A skill record could not be read."""


@dataclass
class Skill:
    id: str
    description: str
    triggers: list[str]
    negative_triggers: list[str]
    kind: str
    path: str
    text: str
    reviewed_on: str | None
    tokens: set[str] = field(default_factory=set)
    raw_description: str = ""

    def to_public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "path": self.path,
            "description": self.description,
            "triggers": list(self.triggers),
            "negative_triggers": list(self.negative_triggers),
            "reviewed_on": self.reviewed_on,
            "content_tokens": sorted(self.tokens),
            "description_characters": len(self.description.strip()),
        }


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split a SKILL.md into a small mapping and the body.

    Keys this reader keeps are name, description, triggers, negative_triggers,
    kind, and reviewed_on. Other keys are ignored. They are not routed on.
    """
    stripped = text.lstrip("\ufeff")
    if not stripped.startswith("---"):
        raise SkillParseError("A SKILL.md file needs front matter that starts with ---.")
    end = stripped.find("\n---", 3)
    if end < 0:
        raise SkillParseError("Front matter was not closed with ---.")
    front = stripped[3:end]
    body = stripped[end + 4 :]
    if body.startswith("\n"):
        body = body[1:]
    return _mapping(front), body


def skill_from_markdown(
    text: str,
    path: str,
    *,
    reviewed_on: str | None = None,
    kind: str | None = None,
) -> Skill:
    meta, body = parse_front_matter(text)
    name = str(meta.get("name") or "").strip()
    if not name:
        raise SkillParseError(f"{path} has no name in front matter.")
    if not _safe_id(name):
        raise SkillParseError(f"{path} name {name!r} is not a lowercase slug.")
    description = str(meta.get("description") or "").strip()
    triggers = _string_list(meta.get("triggers"))
    if not triggers:
        triggers = _triggers_from_body(body)
    negative = _string_list(meta.get("negative_triggers"))
    file_kind = kind or str(meta.get("kind") or "skill")
    if file_kind not in {"skill", "topic"}:
        file_kind = "skill"
    reviewed = reviewed_on or _optional_date(meta.get("reviewed_on"))
    skill = Skill(
        id=name,
        description=description,
        triggers=triggers,
        negative_triggers=negative,
        kind=file_kind,
        path=path,
        text=text if text.endswith("\n") else text + "\n",
        reviewed_on=reviewed,
        raw_description=description,
    )
    skill.tokens = token_set(description)
    return skill


def skill_from_object(item: dict[str, Any], fallback_path: str) -> Skill:
    """Build a skill from JSON. text, when present, is parsed as SKILL.md."""
    if not isinstance(item, dict):
        raise SkillParseError("Each skill must be an object.")
    if isinstance(item.get("text"), str):
        path = str(item.get("path") or item.get("repo_path") or fallback_path)
        return skill_from_markdown(
            item["text"],
            path,
            reviewed_on=_optional_date(item.get("reviewed_on")),
            kind=str(item["kind"]) if item.get("kind") else None,
        )
    name = str(item.get("id") or item.get("name") or "").strip()
    if not _safe_id(name):
        raise SkillParseError(f"Skill id {name!r} is not a lowercase slug.")
    description = str(item.get("description") or "").strip()
    triggers = _string_list(item.get("triggers"))
    negative = _string_list(item.get("negative_triggers"))
    kind = str(item.get("kind") or "skill")
    if kind not in {"skill", "topic"}:
        kind = "skill"
    text = _inline_text(name, description, triggers, negative, kind)
    skill = Skill(
        id=name,
        description=description,
        triggers=triggers,
        negative_triggers=negative,
        kind=kind,
        path=str(item.get("path") or fallback_path),
        text=text,
        reviewed_on=_optional_date(item.get("reviewed_on")),
        raw_description=description,
    )
    skill.tokens = token_set(description)
    return skill


def _inline_text(
    name: str,
    description: str,
    triggers: list[str],
    negative: list[str],
    kind: str,
) -> str:
    lines = ["---", f"name: {name}", "description: >", f"  {description}", f"kind: {kind}"]
    if triggers:
        lines.append("triggers:")
        lines.extend(f"  - {trigger}" for trigger in triggers)
    if negative:
        lines.append("negative_triggers:")
        lines.extend(f"  - {trigger}" for trigger in negative)
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _safe_id(name: str) -> bool:
    if not name:
        return False
    for char in name:
        if not (char.islower() or char.isdigit() or char == "-"):
            return False
    return True


def _optional_date(value: Any) -> str | None:
    if value is None or value == "":
        return None
    return str(value)


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        items = []
        for item in value:
            text = str(item).strip()
            if text:
                items.append(text)
        return items
    raise SkillParseError("triggers must be a string or a list of strings.")


def _triggers_from_body(body: str) -> list[str]:
    """Bullets under a 'Trigger phrases' heading, when front matter has none."""
    lines = body.splitlines()
    collecting = False
    found: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip().lower()
            collecting = title == "trigger phrases"
            continue
        if not collecting:
            continue
        if stripped.startswith("- "):
            phrase = stripped[2:].strip()
            if phrase and len(phrase) <= 160:
                found.append(phrase)
    return found


def _mapping(front: str) -> dict[str, Any]:
    """A small YAML subset: scalars, folded scalars, and lists of scalars."""
    lines = front.splitlines()
    data: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.strip().startswith("#"):
            index += 1
            continue
        if line.startswith((" ", "\t")):
            index += 1
            continue
        if ":" not in line:
            raise SkillParseError(f"Front matter line is not a key: {line}")
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "[]":
            data[key] = []
            index += 1
            continue
        if rest in {">", "|"}:
            index += 1
            block: list[str] = []
            while index < len(lines) and (
                lines[index].startswith((" ", "\t")) or not lines[index].strip()
            ):
                if lines[index].strip():
                    block.append(lines[index].strip())
                index += 1
            joiner = "\n" if rest == "|" else " "
            data[key] = joiner.join(block).strip()
            continue
        if rest == "":
            index += 1
            items: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(lines[index].strip()[2:].strip().strip("'\""))
                index += 1
            data[key] = items
            continue
        data[key] = rest.strip("'\"")
        index += 1
    return data


def description_token_count(description: str) -> int:
    return len(token_set(description))
