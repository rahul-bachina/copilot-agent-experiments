"""Build a proposed unified diff. Do not write it anywhere."""

from __future__ import annotations

import difflib
from typing import Any


def propose(documents: list[dict[str, Any]], checks: list[dict[str, Any]]) -> dict[str, Any]:
    """Append suggested rewrites for checks that are not a pass.

    The original text is not otherwise changed. applied is false.
    """
    pending = [check for check in checks if check["result"] != "pass" and check.get("suggested_rewrite")]
    files = []
    chunks = []
    for document in documents:
        path = document.get("path") or "instructions.md"
        original = document.get("text") or ""
        if not original.endswith("\n"):
            original_for_diff = original + "\n"
        else:
            original_for_diff = original
        if pending:
            block = ["## Proposed rewrites (draft for the agent owner, not applied)", ""]
            for check in pending:
                block.append(f"### {check['id']} — {check['name']}")
                block.append("")
                block.append(check["suggested_rewrite"])
                block.append("")
            addition = "\n".join(block).rstrip() + "\n"
            proposed = original_for_diff.rstrip() + "\n\n" + addition
        else:
            proposed = original_for_diff
        diff = "".join(
            difflib.unified_diff(
                original_for_diff.splitlines(keepends=True),
                proposed.splitlines(keepends=True),
                fromfile="a/" + path,
                tofile="b/" + path,
            )
        )
        files.append({"path": path, "diff": diff, "applied": False})
        if diff:
            chunks.append(diff)
    return {
        "applied": False,
        "diff": "".join(chunks),
        "files": files,
    }
