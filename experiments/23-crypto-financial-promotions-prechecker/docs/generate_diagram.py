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
    ax.text(x + 0.18, y + h - 0.58, body, ha="left", va="top", fontsize=8.2, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(13.2, 7.6))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3, 7.25,
        "Cryptoasset promotion checklist — for the section 21 approver",
        fontsize=14, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.88,
        "Experiment 23. Autonomy A0. Catalogue UK08. The approver signs off. The agent does not.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 4.05, 2.65,
        "1. Reviewer",
        "Supplies one synthetic\ndraft and types the\nas-of date. The draft\ntext is untrusted.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 4.55, 3.85, 4.15, 2.65,
        "2. Either harness",
        "Copilot Studio, standard\ntopic or GitHub Copilot\nharness. Both call\nprecheck(). Not a chat.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.95, 3.85, 3.95, 2.65,
        "3. Python checklist",
        "Pinned pages. Drops\ninjection. Flags stale.\nDecision stays null.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.2, 3.15,
        "4. Human approval",
        "The section 21 approver\nsigns off or refuses.\nA flagged phrase is their\nquestion, not a finding.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 6.7, 0.35, 6.15, 3.15,
        "Not a tool of the agent",
        "No approval and no publication.\nNo rewrite and no opinion.\nNo register lookup.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
