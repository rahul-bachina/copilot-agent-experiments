#!/usr/bin/env python3
"""Render docs/architecture_diagram.png. Matplotlib is used only for this script."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def box(ax, x, y, w, h, title, body, face, edge):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.4,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top", fontsize=11, fontweight="bold", color="#1a1a1a")
    ax.text(x + 0.16, y + h - 0.58, body, ha="left", va="top", fontsize=8.2, color="#333333", linespacing=1.35)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.1,
            color="#444444",
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.6))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3,
        7.25,
        "Underwriting submission summary — copy the lines, do not price the risk",
        fontsize=14,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        0.3,
        6.88,
        "Experiment 37. Catalogue B006. Autonomy A0. The underwriter owns coverage and price.",
        fontsize=9,
        color="#444444",
    )

    box(
        ax, 0.25, 3.7, 3.05, 2.85,
        "1. Underwriter",
        "Supplies one synthetic\nsubmission and an as-of date.\nDoes not paste a live risk.\nNorthfen Wharf Ltd is fictional.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.55, 3.7, 4.15, 2.85,
        "2. Either harness",
        "GitHub Copilot harness:\nthree skills, then stop.\nStandard harness: one topic.\nBoth call the same Python.\nNeither is the Copilot service.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.95, 3.7, 4.55, 2.85,
        "3. Python summary",
        "Experiment 12 inventories files.\nCopies current contiguous lines.\nA missing field is not stated.\nExperiment 29 checks numbers.\nFoundry is described, not called.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 7.55, 2.95,
        "4. Human approval",
        "The underwriter reviews every cited fact.\nThe underwriter decides coverage and price.\nAny message to the broker is outside this agent.\nAny write to the underwriting system is outside this agent.\nA stale pin is re-opened before the legal note is relied on.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 8.05, 0.35, 4.45, 2.95,
        "Not a tool",
        "No accept or decline.\nNo price and no terms.\nNo broker contact.\nNo underwriting-system write.\nNo bind. No autonomy A3.",
        "#fde8e8", "#8a1f1f",
    )
    arrow(ax, 3.3, 5.1, 3.55, 5.1)
    arrow(ax, 7.7, 5.1, 7.95, 5.1)
    arrow(ax, 9.5, 3.7, 4.0, 3.3)

    fig.tight_layout()
    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
