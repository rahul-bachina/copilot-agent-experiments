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
    patch = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.1,
        color="#444444",
    )
    ax.add_patch(patch)


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 8.2))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3,
        7.9,
        "Claims document triage — quote the file, do not decide the claim",
        fontsize=14,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        0.3,
        7.52,
        "Experiment 35. Catalogue B007. Autonomy A1. The claims handler approves the class.",
        fontsize=9,
        color="#444444",
    )

    box(
        ax, 0.25, 4.35, 3.05, 2.9,
        "1. Claims handler",
        "Supplies a synthetic pack\nand the as-of date.\nFNOL, invoice, report,\npolicy extract.\nNo claims system.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.55, 4.35, 4.15, 2.9,
        "2. Either harness",
        "GitHub Copilot harness:\nthree skills, then stop.\nStandard harness: one topic.\nBoth call the same Python.\nNeither is the Copilot service.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.95, 4.35, 4.55, 2.9,
        "3. Python triage",
        "Experiment 12, then 08.\nQuoted lines and a pointer.\nPrompts, not findings.\nExperiment 29 scores.\nNo model. No network.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.15, 3.6,
        "4. Human approval",
        "The handler checks each prompt. A prompt is not a finding.\n"
        "If a draft threshold is missed, the handler reviews the score.\n"
        "That review does not decline the claim.\n"
        "The handler approves or changes the class.\n"
        "If a date is not current, the handler reviews it before relying on a line.\n"
        "Recording the class still does not accept, settle, or write.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 8.65, 0.35, 3.85, 3.6,
        "5. Not a tool",
        "No accept.\nNo decline.\nNo settlement.\nNo message to the customer.\nNo write to the claims system.\nNo fraud label.",
        "#fde8e8", "#8a1f1f",
    )
    arrow(ax, 3.3, 5.8, 3.55, 5.8)
    arrow(ax, 7.7, 5.8, 7.95, 5.8)
    arrow(ax, 10.2, 4.35, 4.3, 3.95)

    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(out)


if __name__ == "__main__":
    main()
