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
    ax.text(x + 0.18, y + h - 0.55, body, ha="left", va="top", fontsize=8.5, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.3, 6.85, "Complaint intake — Consumer Duty / DISP", fontsize=15, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.5, "Experiment 02. The handler decides. The clock is code. Nothing is sent.", fontsize=9, color="#444444")

    box(
        ax, 0.3, 3.5, 3.3, 2.6,
        "1. Handler",
        "Pastes one complaint.\nEnters the receipt date.\nConfirms the route\nbefore a PSD or EMD\nclock is used.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 4.3, 3.5, 3.6, 2.6,
        "2. Draft",
        "Extraction proposes\nclassification, product,\nroot cause, severity,\nvulnerability drivers,\nConsumer Duty outcome.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.6, 3.5, 3.6, 2.6,
        "3. DISP clock",
        "Python. Not the model.\n3 business days.\n8 weeks.\n15 / 35 only if the\nhandler supplies the\nPSP calendar.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.3, 0.35, 5.5, 2.5,
        "4. Handler validates",
        "Accepts or changes every classification\nand the severity. Edits the draft\nacknowledgement. Sends and files it\nthemselves, in the firm's own systems.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.4, 0.35, 5.8, 2.5,
        "Not a tool of the agent",
        "No send.\nNo Dynamics 365 write, resolve, or close.\nNo uphold, reject, or redress.\nNo vulnerability label on the customer.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
