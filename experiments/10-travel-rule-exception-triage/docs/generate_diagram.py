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
    ax.text(x + 0.18, y + h - 0.55, body, ha="left", va="top", fontsize=8.4, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.4))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.4)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.3, 7.05, "Travel Rule exception triage — draft for an analyst", fontsize=14, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.68, "Experiment 10. Autonomy A1. Catalogue UK05. The analyst decides. The checklist does not.", fontsize=9, color="#444444")

    box(
        ax, 0.25, 3.55, 3.15, 2.75,
        "1. Analyst",
        "Supplies one synthetic\ntransfer. Types the\nas-of date. Harbourline\nis the invented firm\nfrom Experiment 04.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.55, 4.3, 2.75,
        "2. Either harness",
        "Copilot Studio, standard\ntopic or GitHub Copilot\nharness. Both call the\nchecklist. Sandbox draft\nonly. No send.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.1, 3.55, 4.4, 2.75,
        "3. Python checklist",
        "Pinned Part 7A text.\n£800, not 1,000 euros.\nInjection quarantined.\nStale pin flagged.\nDecision stays empty.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.3, 2.85,
        "4. Human approval",
        "The analyst reads the options.\nThey decide hold, return, or escalate.\nThey re-open a stale source before relying on it.\nThey act in the firm's own systems, outside the agent.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.75, 0.35, 5.75, 2.85,
        "Not a tool of the agent",
        "No hold, return, reject, or release.\nNo cryptoasset made available.\nNo counterparty contact.\nNo suspicious activity report.\nNo FCA report and no production write.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
