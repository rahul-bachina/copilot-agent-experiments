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
    fig, ax = plt.subplots(figsize=(13.2, 7.8))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 7.8)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.3, 7.45, "Complaints root-cause MI — draft for review", fontsize=14, fontweight="bold", color="#1a1a1a")
    ax.text(
        0.3, 7.08,
        "Experiment 20. Autonomy A0. Catalogue UK04. The complaints owner validates. The agent does not.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 4.05, 4.05, 2.7,
        "1. Complaints owner",
        "Supplies one synthetic\nbatch and the as-of date.\nText is untrusted.\nThe date is typed, not inferred.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 4.55, 4.05, 4.15, 2.7,
        "2. Either harness",
        "Copilot Studio, standard\ntopic or GitHub Copilot\nharness. Both call the draft.\nNot a public chat.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.95, 4.05, 3.95, 2.7,
        "3. Python draft",
        "Experiment 08 redacts.\nExperiment 02 analyse()\nfor financial services.\nFigures list record ids.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.35, 3.4,
        "4. Human approval",
        "Complaints owner validates\nthe clusters, then the narrative.\nCompliance and any submit or\npublish stay outside the agent.\nStale sources and a suggested\ncause need a person. Viewing does not.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 6.85, 0.35, 6.05, 3.4,
        "Not a tool of the agent",
        "No validation of clusters\nor narrative. No regulatory\nreturn. No publish and no send.\nNo production write. The draft\nis not anonymised.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
