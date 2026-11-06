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
    ax.text(x + 0.16, y + h - 0.55, body, ha="left", va="top", fontsize=8.0, color="#333333", linespacing=1.35)


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
    fig, ax = plt.subplots(figsize=(12.8, 8.2))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3,
        7.85,
        "Credit memo drafting — copy the lines, do not decide the credit",
        fontsize=14,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        0.3,
        7.48,
        "Experiment 39. Catalogue B009. Autonomy A1. The credit officer owns the recommendation and every approval.",
        fontsize=9,
        color="#444444",
    )

    box(
        ax, 0.25, 4.35, 3.05, 2.85,
        "1. Credit officer",
        "Supplies one synthetic pack\nand an as-of date.\nMereholt Components Ltd\nis fictional.\nDoes not paste a live facility.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.55, 4.35, 4.15, 2.85,
        "2. Either harness",
        "GitHub Copilot harness:\nthree skills, then stop.\nStandard harness: one topic.\nBoth call the same Python.\nNeither is the Copilot service.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.95, 4.35, 4.55, 2.85,
        "3. Python draft",
        "Experiment 12 inventories files.\nCopies current contiguous lines.\nA missing section is not stated.\nExperiment 36 compares listed fields.\nFoundry and Fabric are not called.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.15, 3.55,
        "4. People, outside the agent",
        "Credit officer reviews every cited fact before any use.\n"
        "Credit officer owns the recommendation, any approval or decline, and any limit.\n"
        "MLRO decides any SAR. No customer text is produced.\n"
        "Customer or bureau contact, and any core or CRM post, stay outside.\n"
        "Data protection officer confirms a lawful basis before live processing.\n"
        "A stale pin is re-opened by the credit officer before the note is relied on.\n"
        "draft_approved_for_use stays false. The agent marks none of these done.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 8.65, 0.35, 3.85, 3.55,
        "Not done here",
        "No credit decision.\nNo limit.\nNo customer or bureau contact.\nNo core banking or CRM post.\nNo SAR.\nNo Foundry call.\nNo Fabric write.\nNo autonomy A3.",
        "#fdecea", "#8a1c1c",
    )

    arrow(ax, 3.3, 5.75, 3.55, 5.75)
    arrow(ax, 7.7, 5.75, 7.95, 5.75)
    arrow(ax, 10.2, 4.35, 10.2, 3.9)

    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
