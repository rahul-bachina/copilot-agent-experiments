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

    ax.text(0.3, 7.05, "IT service desk — draft for a signed-in member of staff or an analyst", fontsize=13, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.68, "Experiment 21. Autonomy A1. Catalogue Q009. The person confirms. The desk does not execute.", fontsize=9, color="#444444")

    box(
        ax, 0.25, 3.55, 3.15, 2.75,
        "1. Person",
        "Supplies one synthetic\nticket. Types the\nas-of date. Aldermere\nis an invented council.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.55, 4.3, 2.75,
        "2. Either harness",
        "Copilot Studio, standard\ntopic or GitHub Copilot\nharness. Both call the\ndesk. No reset and no send.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.1, 3.55, 4.4, 2.75,
        "3. Python desk",
        "Experiment 08 counts\nidentifiers. Identity is a\nchannel object. Stale body\nnot quoted. Approval empty.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.3, 2.85,
        "4. Human approval",
        "The member of staff confirms a device change,\nor a standard fix they will try themselves.\nAn analyst takes a password, MFA, or access handover.\nThey act in the organisation's own systems.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.75, 0.35, 5.75, 2.85,
        "Not a tool of the agent",
        "No password reset and no MFA change.\nNo access grant and no remote wipe.\nNo device change is performed.\nNo ticket write and no message.\nNo licence purchase.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
