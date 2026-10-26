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

    ax.text(0.3, 6.85, "Correspondence draft — ministerial, MP, and resident casework", fontsize=14, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.5, "Experiment 09. The author approves the recipient and the text. Nothing is sent.", fontsize=9, color="#444444")

    box(
        ax, 0.3, 3.5, 3.3, 2.6,
        "1. Author",
        "Pastes one letter.\nEnters the receipt date\nand the as-of date.\nConfirms the channel\nand the reply target.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 4.3, 3.5, 3.6, 2.6,
        "2. Draft",
        "Proposes a channel.\nCites a current line\nor states a gap.\nFlags vulnerability\nwording for a person.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.6, 3.5, 3.6, 2.6,
        "3. Casework clock",
        "Python. Not the model.\nDay 1 is the day after\nreceipt. Ceiling 20\nworking days for a\ndepartment. Not for FOI.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.3, 0.35, 5.5, 2.5,
        "4. Author approves",
        "Approves the recipient and the final text.\nReviews any vulnerability flag.\nSends and files in the unit's own systems.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.4, 0.35, 5.8, 2.5,
        "Not a tool of the agent",
        "No send.\nNo case-system write.\nNo invented policy line.\nNo final recipient from the letter.\nNo ATRS submission.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
