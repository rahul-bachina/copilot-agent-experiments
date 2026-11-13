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
        "Excel assumption review — the model owner confirms the workbook",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 54. Autonomy A0. Catalogue M006. The agent reports. It does not edit.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.7, 3.15, 2.75,
        "1. Model owner",
        "Confirms the workbook,\nthe ranges, and the\nformulas. Types the\nas-of date.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 3.6, 3.7, 4.3, 2.75,
        "2. Either harness",
        "Copilot Studio, standard\ntopic or skills layout.\nBoth call the core.\nNo Graph session.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.1, 3.7, 4.4, 2.75,
        "3. Python core",
        "Closed formula reader.\nExperiment 36 compares.\nExperiment 08 types only.\n1 percent shock, no benchmark.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.3, 3.0,
        "4. Human approval",
        "The owner reads the report.\nFindings stay unaccepted.\nDistress text goes to a person.\nThe workbook is not edited.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 6.75, 0.35, 5.75, 3.0,
        "Not a tool of the agent",
        "No cell write and no Graph.\nNo right or wrong judgement.\nNo invented benchmark.\nMarkings and legal hold stay.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
