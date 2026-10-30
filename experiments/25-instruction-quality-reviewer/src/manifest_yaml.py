"""Read the subset of YAML used by agent-manifest.yaml in this repository.

The clean install does not include PyYAML. A file this reader cannot parse
raises YamlError. The reviewer reports that. It does not guess a pass.
"""

from __future__ import annotations

import re
from typing import Any


class YamlError(ValueError):
    """The manifest is not in the subset this reader accepts."""


def load_yaml(text: str) -> Any:
    lines = text.splitlines()
    value, index = _parse_block(lines, 0, 0)
    index = _next_content(lines, index)
    if index < len(lines):
        raise YamlError(f"Trailing content at line {index + 1}")
    return value


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _next_content(lines: list[str], index: int) -> int:
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return index
        index += 1
    return index


def _strip_comment(text: str) -> str:
    out: list[str] = []
    quote = ""
    for char in text:
        if quote:
            out.append(char)
            if char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            out.append(char)
            continue
        if char == "#":
            break
        out.append(char)
    return "".join(out).rstrip()


def _scalar(text: str) -> Any:
    text = text.strip()
    if text in {"", "~", "null", "Null", "NULL"}:
        return None
    if text in {"true", "True", "TRUE"}:
        return True
    if text in {"false", "False", "FALSE"}:
        return False
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        return text[1:-1]
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


def _parse_block(lines: list[str], index: int, min_indent: int) -> tuple[Any, int]:
    index = _next_content(lines, index)
    if index >= len(lines):
        return None, index
    indent = _indent(lines[index])
    if indent < min_indent:
        return None, index
    body = lines[index].lstrip()
    if body.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_map(lines, index, indent)


def _parse_map(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines):
        index = _next_content(lines, index)
        if index >= len(lines):
            break
        if _indent(lines[index]) < indent:
            break
        if _indent(lines[index]) > indent:
            raise YamlError(f"Unexpected indent at line {index + 1}")
        raw = _strip_comment(lines[index].strip())
        if raw.startswith("- "):
            break
        if ":" not in raw:
            raise YamlError(f"Expected a key at line {index + 1}")
        key, _, rest = raw.partition(":")
        key = key.strip()
        rest = rest.strip()
        if not key:
            raise YamlError(f"Empty key at line {index + 1}")
        if rest in {">", ">", "|", "|-", ">-", ">+", "|+"} or rest.startswith(">"):
            folded = rest.startswith(">")
            value, index = _block_scalar(lines, index + 1, indent, folded)
        elif rest == "":
            value, index = _parse_block(lines, index + 1, indent + 1)
            if value is None:
                value = {}
        else:
            value = _scalar(rest)
            index += 1
        mapping[key] = value
    return mapping, index


def _parse_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(lines):
        index = _next_content(lines, index)
        if index >= len(lines) or _indent(lines[index]) < indent:
            break
        if _indent(lines[index]) > indent:
            raise YamlError(f"Unexpected indent at line {index + 1}")
        raw = lines[index]
        body = raw.lstrip()
        if not body.startswith("- "):
            break
        rest = _strip_comment(body[2:].strip())
        item_indent = _indent(raw)
        if rest == "":
            value, index = _parse_block(lines, index + 1, item_indent + 2)
            items.append(value)
            continue
        if rest.startswith("- "):
            raise YamlError(f"Nested list marker was not understood at line {index + 1}")
        if ":" in rest and not _looks_like_scalar(rest):
            key, _, after = rest.partition(":")
            synthetic = (" " * (item_indent + 2)) + f"{key.strip()}:{after}"
            block_lines = [synthetic]
            cursor = index + 1
            while cursor < len(lines):
                if not lines[cursor].strip():
                    block_lines.append(lines[cursor])
                    cursor += 1
                    continue
                if _indent(lines[cursor]) <= item_indent:
                    break
                block_lines.append(lines[cursor])
                cursor += 1
            value, _ = _parse_map(block_lines, 0, item_indent + 2)
            items.append(value)
            index = cursor
            continue
        items.append(_scalar(rest))
        index += 1
    return items, index


def _looks_like_scalar(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        return True
    return False


def _block_scalar(lines: list[str], index: int, key_indent: int, folded: bool) -> tuple[str, int]:
    chunks: list[str] = []
    while index < len(lines):
        raw = lines[index]
        if not raw.strip():
            chunks.append("")
            index += 1
            continue
        if raw.lstrip().startswith("#") and _indent(raw) <= key_indent:
            break
        if _indent(raw) <= key_indent:
            break
        chunks.append(raw.strip())
        index += 1
    if folded:
        words: list[str] = []
        pieces: list[str] = []
        for chunk in chunks:
            if chunk == "":
                if words:
                    pieces.append(" ".join(words))
                    words = []
            else:
                words.append(chunk)
        if words:
            pieces.append(" ".join(words))
        return " ".join(pieces).strip(), index
    return "\n".join(chunk for chunk in chunks).strip(), index
