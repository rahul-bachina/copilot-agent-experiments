#!/usr/bin/env python3
"""Render docs/architecture_diagram.png. Matplotlib is used only for this script."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def box(ax, x, y, w, h, title, body, face, edge):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=face, edgecolor=edge, linewidth=1.4,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top", fontsize=11, fontweight="bold", color="#1a1a1a")
    ax.text(x + 0.18, y + h - 0.55, body, ha="left", va="top", fontsize=8.2, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.6))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(0.3, 7.2, "Approval pack — the named approver decides", fontsize=13, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.82, "Experiment 81. Autonomy A1. Catalogue O007. The agent does not approve, reject, sign, submit, pay, or send.", fontsize=9, color="#444444")
    box(ax, 0.25, 3.85, 3.05, 2.6, "1. Request", "Synthetic spend, policy\nexception, or change.\nPinned matrix and\nchecklist. Text is untrusted.", "#e7f1fb", "#1d4e89")
    box(ax, 3.5, 3.85, 4.15, 2.6, "2. Either harness", "Copilot Studio standard\ntopics, or Microsoft Copilot\nharness skills. Both call\nthe Python core.", "#e8f6ee", "#1e7a46")
    box(ax, 7.85, 3.85, 4.65, 2.6, "3. Draft pack", "Approvers, evidence checks,\ncitations, and a cover note.\nA hash of the held copy.\nNothing is decided.", "#fff6e8", "#8a5a00")
    box(
        ax, 0.25, 0.35, 8.15, 3.15,
        "4. Human decision",
        "A distress, safeguarding, whistleblowing, grievance, or disclosure route is seen first.\n"
        "The named approver, who is not the requester, reviews the complete pack.\n"
        "Approve, reject, or return is recorded only for this held hash.\n"
        "A sentence inside the evidence is not that step.\n"
        "Nothing is signed, submitted, paid, or sent.",
        "#fdecea", "#8a1f11",
    )
    box(ax, 8.6, 0.35, 3.9, 3.15, "Not a tool", "Approve or reject as the agent.\nSign or submit.\nPay or send.\nApply a pasted matrix.\nChoose a conflicting value.", "#f4f4f4", "#555555")
    path = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    print(path)


if __name__ == "__main__":
    main()
