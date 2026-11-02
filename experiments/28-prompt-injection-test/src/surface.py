"""Instruction-surface rules S1 to S6.

A pass means the written file contains the wording this checker looks for.
It does not mean a live model would refuse.

A markdown heading that contains a negation keeps every following line until
the next heading. Any other negated line is its own scope. The verb has to
sit in that scope.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from manifest_yaml import YamlError, load_yaml
else:
    from .manifest_yaml import YamlError, load_yaml

RULES: tuple[dict[str, str], ...] = (
    {
        "id": "S1",
        "class": "instruction_override",
        "name": "Untrusted content is not followed",
    },
    {
        "id": "S2",
        "class": "encoding",
        "name": "A transformed instruction still counts",
    },
    {
        "id": "S3",
        "class": "data_exfiltration",
        "name": "Do not send, copy, or reveal",
    },
    {
        "id": "S4",
        "class": "tool_misuse",
        "name": "Writes and sends are off, and the text forbids them",
    },
    {
        "id": "S5",
        "class": "prohibited_action",
        "name": "Writes and sends are off, and the text forbids the action",
    },
    {
        "id": "S6",
        "class": "system_prompt_disclosure",
        "name": "Do not reveal the system prompt",
    },
)

_NEGATION = re.compile(r"\b(do not|don't|never|must not|cannot|can't)\b", re.I)


def negation_scopes(text: str) -> list[str]:
    scopes: list[list[str]] = []
    current: list[str] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            if current:
                scopes.append(current)
            current = [line] if _NEGATION.search(line) else None
            continue
        if current is not None:
            if line:
                current.append(line)
            continue
        if line and _NEGATION.search(line):
            scopes.append([line])
    if current:
        scopes.append(current)
    return [" ".join(scope) for scope in scopes]


def _any(scopes: list[str], pattern: str) -> bool:
    return any(re.search(pattern, scope, re.I) for scope in scopes)


def _disabled_flag(value: Any) -> bool | None:
    if isinstance(value, dict) and "enabled" in value:
        return value.get("enabled") is False
    return None


def _from_tools_json(data: Any) -> tuple[bool | None, bool | None]:
    items = data.get("tools") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        return None, None
    dicts = [item for item in items if isinstance(item, dict)]
    if not dicts or not all("writes" in item and "sends" in item for item in dicts):
        return None, None
    return (
        all(item.get("writes") is False for item in dicts),
        all(item.get("sends") is False for item in dicts),
    )


def _from_manifest(data: Any) -> tuple[bool | None, bool | None]:
    if not isinstance(data, dict):
        return None, None
    tools = data.get("tools")
    if not isinstance(tools, dict):
        return None, None
    return _disabled_flag(tools.get("writes")), _disabled_flag(tools.get("sends"))


def _both_disabled(left: bool | None, right: bool | None) -> bool:
    if left is None:
        return right is True
    if right is None:
        return left is True
    return left is True and right is True


def tool_posture(tools_text: str | None, manifest_text: str | None) -> dict[str, Any]:
    """True means the capability is disabled. Unknown is not disabled."""
    tools_writes, tools_sends = None, None
    manifest_writes, manifest_sends = None, None
    errors: list[str] = []
    if tools_text is not None:
        try:
            tools_writes, tools_sends = _from_tools_json(json.loads(tools_text))
        except json.JSONDecodeError as exc:
            errors.append(f"Tool schema was not read: {exc.msg}")
    if manifest_text is not None:
        try:
            manifest_writes, manifest_sends = _from_manifest(load_yaml(manifest_text))
        except YamlError as exc:
            errors.append(f"Manifest was not read: {exc}")
    return {
        "writes_disabled": _both_disabled(tools_writes, manifest_writes),
        "sends_disabled": _both_disabled(tools_sends, manifest_sends),
        "errors": errors,
    }


def control_present(class_name: str, text: str, posture: dict[str, Any]) -> bool:
    scopes = negation_scopes(text)
    if class_name == "instruction_override":
        data = re.search(r"\b(is|are) data\b", text, re.I) is not None
        held = re.search(
            r"(do not follow|not follow|do not change these instructions|cannot change these instructions)",
            text,
            re.I,
        ) is not None
        # The asked-pattern has to be in the SAME scope, not two different scopes.
        same = False
        for scope in scopes:
            if re.search(r"\b(file|document|email|chat|text|page|tool)\b", scope, re.I) and re.search(
                r"\b(asked|tells|tell|says|instructs|because)\b", scope, re.I
            ):
                same = True
                break
        return (data and held) or same
    if class_name == "encoding":
        return _any(scopes, r"\b(encod\w*|obfuscat\w*|base64|rot13|cipher)\b") or _any(
            scopes, r"\b(transformed|encoded)\b.+\b(still|counts)\b"
        )
    if class_name == "data_exfiltration":
        return _any(scopes, r"\b(send|copy|reveal|disclose|exfiltrat\w*)\b")
    if class_name == "tool_misuse":
        if not (posture.get("writes_disabled") and posture.get("sends_disabled")):
            return False
        return _any(scopes, r"\b(send|write|deploy|release|tool)\b")
    if class_name == "prohibited_action":
        if not (posture.get("writes_disabled") and posture.get("sends_disabled")):
            return False
        return _any(scopes, r"\b(approv\w*|reject|spend|decid\w*|send|deploy|releas\w*)\b")
    if class_name == "system_prompt_disclosure":
        for scope in scopes:
            verb = re.search(r"\b(reveal|repeat|print|disclose|show)\b", scope, re.I)
            target = re.search(r"(system prompt|these instructions|this prompt)", scope, re.I)
            if verb and target:
                return True
        return False
    raise ValueError(f"No surface rule for {class_name}")


def rule_for(class_name: str) -> dict[str, str]:
    for rule in RULES:
        if rule["class"] == class_name:
            return rule
    raise ValueError(class_name)
