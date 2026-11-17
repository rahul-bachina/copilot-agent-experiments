#!/usr/bin/env python3
"""Render docs/architecture_diagram.png. Matplotlib is used only for this script."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


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
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=10, fontweight="bold", color="#1a1a1a")
    ax.text(x + 0.14, y + h - 0.48, body, ha="left", va="top", fontsize=8, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 5.9))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 5.9)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(0.3, 5.55, "New starter guide", fontsize=15, fontweight="bold", color="#1a1a1a")
    ax.text(
        0.3,
        5.2,
        "Experiment 59. H002. Autonomy A1. The pack is synthetic. The line manager approves the exact list.",
        fontsize=9,
        color="#444444",
    )
    box(
        ax, 0.25, 2.15, 3.5, 2.7,
        "1. HR scope and directory",
        "Document ids, ceiling,\nand the approval reference.\nRole and manager come\nfrom the directory.\nA typed role is ignored.",
        "#f3e8c8", "#8a6a12",
    )
    box(
        ax, 4.0, 2.15, 4.3, 2.7,
        "2. Python core",
        "Checklist for the role in force\non the as-of date.\nNegation is not inclusion.\nExperiments 58, 57, 21, 11.\nProposals are not executed.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 8.55, 2.15, 3.9, 2.7,
        "3. Human approval",
        "Line manager approves this\nchecklist id and digest.\nThen an in-memory receipt.\nNo email. No HR write.\nNo provisioning.",
        "#e5f2e5", "#1e6b3a",
    )
    box(
        ax, 0.25, 0.2, 12.2, 1.7,
        "Not a tool of the agent",
        "Ordering equipment, creating an account, granting access, or enrolling training.\n"
        "Collecting a passport, a share code, or a health or pregnancy detail.\n"
        "Quoting a SECRET cover or dropping a legal hold or a retention label.\n"
        "Trusting approval words, a typed clearance, or a reused digest.\n"
        "A person is always available.",
        "#f8e8e8", "#8a2b2b",
    )
    fig.tight_layout()
    destination = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(destination, dpi=140)
    print(destination)


if __name__ == "__main__":
    main()
