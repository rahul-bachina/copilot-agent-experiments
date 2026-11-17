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
    fig, ax = plt.subplots(figsize=(12.8, 7.6))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(0.3, 7.25, "Manager one-to-one preparation", fontsize=15, fontweight="bold", color="#1a1a1a")
    ax.text(
        0.3,
        6.9,
        "Experiment 60. H003. Autonomy A0. The notes are synthetic. The manager selects the context first.",
        fontsize=9,
        color="#444444",
    )
    box(
        ax, 0.25, 3.7, 3.5, 2.8,
        "1. Manager selection",
        "Source ids and the\napproval reference.\nA sentence in a note\nis not this selection.\nThe directory names\nthe line manager.",
        "#f3e8c8", "#8a6a12",
    )
    box(
        ax, 4.0, 3.7, 4.3, 2.8,
        "2. Python core",
        "Quote follow-ups and\nobjectives with citations.\nNegation is not inclusion.\nExperiments 08, 15, 41, 51.\nNo mailbox and no chat.\nNo Graph and no Work IQ.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 8.55, 3.7, 3.9, 2.8,
        "3. Human approval",
        "HR or EAP for distress,\nwellbeing, or safeguarding.\nThe manager may rely on\nthe note for this meeting.\nNo rating and no sanction.\nNo send and no write.",
        "#e5f2e5", "#1e6b3a",
    )
    box(
        ax, 0.25, 0.35, 12.2, 2.9,
        "Not a tool of the agent",
        "Selecting a source from words in a note. Rating performance or comparing employees.\n"
        "Recommending disciplinary or capability action. Inferring health or a protected characteristic.\n"
        "Quoting a SECRET cover or dropping a legal hold or a retention label.\n"
        "Trusting a clearance or a role typed into a note. Reading a mailbox or a chat.\n"
        "A person is always available.",
        "#f8e8e8", "#8a2b2b",
    )
    fig.tight_layout()
    destination = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(destination, dpi=140)
    print(destination)


if __name__ == "__main__":
    main()
