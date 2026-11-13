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
        "OneDrive document finder — the user confirms the locations",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 55. Autonomy A0. Catalogue M007. The agent lists. It does not change a file.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.7, 3.15, 2.75,
        "1. Requesting user",
        "Confirms location ids,\nprincipals, and clearance\non a separate object.\nMerrowfield is invented.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.7, 4.3, 2.75,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe core. No Graph call.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.1, 3.7, 4.4, 2.75,
        "3. Python core",
        "Confirmed locations only.\nExperiments 49, 50, and 08.\nAbove clearance is a count.\nLabels and holds are kept.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.3, 3.0,
        "4. Human approval",
        "Confirm the locations first.\nReview a safeguarding hit.\nAcknowledge a stale pin.\nAcknowledgement changes nothing.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.75, 0.35, 5.75, 3.0,
        "Not a tool of the agent",
        "No move, delete, or share.\nNo permission change.\nGraph, Search, and Work IQ\nare not called. A person\nis always offered.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
