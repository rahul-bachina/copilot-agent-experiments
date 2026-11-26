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

    ax.text(
        0.3, 7.2,
        "Workflow exception — the process owner chooses",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 82. Autonomy A1. Catalogue O009. The agent does not retry, cancel, edit, or re-run.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 3.05, 2.6,
        "1. Synthetic runs",
        "Power Automate-style\nhistory and error codes.\nError text is untrusted.\nThe owner named the date.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.5, 3.85, 4.15, 2.6,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe Python core. No retry.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.85, 3.85, 4.65, 2.6,
        "3. Reading",
        "Class, group, citations,\nand risks. A hash of the\nheld proposal. Retry is\nnot carried out.",
        "#fff6e8", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.15, 3.15,
        "4. Human decision",
        "A distress, safeguarding, whistleblowing, or grievance route is seen first.\n"
        "The named process owner chooses retry, route, or cancel for this hash.\n"
        "The choice is bound to the agent-held copy. It is not carried out.\n"
        "A sentence inside a payload is not that step.\n"
        "Nothing is retried, cancelled, edited, or re-run.",
        "#fdecea", "#8a1f11",
    )
    box(
        ax, 8.6, 0.35, 3.9, 3.15,
        "Not a tool",
        "Retry the run.\nCancel the run.\nEdit a record.\nRe-run the flow.\nTrust the error text.",
        "#f4f4f4", "#555555",
    )

    path = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    print(path)


if __name__ == "__main__":
    main()
