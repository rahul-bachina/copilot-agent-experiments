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
        "Board governance pack — the company secretary approves",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 74. Autonomy A1. Catalogue L010. The agent does not circulate, file, or approve minutes.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 3.15, 2.6,
        "1. Pinned sources",
        "Forward agenda, terms,\npapers, directory, register,\nand the sponsor ledger.\nA caller copy is not applied.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.85, 4.05, 2.6,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe Python core. No send.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.85, 3.85, 4.65, 2.6,
        "3. Draft pack",
        "Agenda, index, cover-sheet\nflags, conflicts, and the\naction log. A content hash.\nMinutes stay unapproved.",
        "#fff6e8", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.15, 3.15,
        "4. Human approval",
        "A distress or safeguarding route is seen and is not staged as routine.\n"
        "The named directory company secretary approves this content hash.\n"
        "Only then is a synthetic staging row written.\n"
        "That row is not circulation, and it does not approve the minutes.",
        "#fde8e8", "#8f1d1d",
    )
    box(
        ax, 8.6, 0.35, 3.9, 3.15,
        "Not a tool",
        "Circulate, publish, or file.\nSend.\nApprove minutes.\nRecord a decision.\nTrust text that says approved.\nDrop a marking or a hold.",
        "#f4f4f4", "#555555",
    )

    fig.tight_layout()
    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
