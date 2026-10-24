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
    ax.text(
        x + w / 2,
        y + h - 0.28,
        title,
        ha="center",
        va="top",
        fontsize=11,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        x + 0.18,
        y + h - 0.55,
        body,
        ha="left",
        va="top",
        fontsize=8.5,
        color="#333333",
        linespacing=1.35,
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.5, 7.4))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 7.4)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3,
        7.05,
        "Hazard triage — Awaab's Law",
        fontsize=15,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        0.3,
        6.68,
        "Experiment 05. The officer approves the category, the clock, and every summary. Nothing is sent.",
        fontsize=9,
        color="#444444",
    )

    box(
        ax,
        0.3,
        3.55,
        3.5,
        2.75,
        "1. Officer",
        "Pastes one report.\nEnters the awareness time.\nConfirms a social home\nin England before any\ndate is relied on.",
        "#e7f1fb",
        "#1d4e89",
    )
    box(
        ax,
        4.15,
        3.55,
        3.9,
        2.75,
        "2. Draft",
        "Proposes a hazard family\nand category. Flags\ncharacteristics with quotes.\nDoes not label the tenant.\nPhase 2 and 3 stay flagged.",
        "#e8f6ee",
        "#1e7a46",
    )
    box(
        ax,
        8.35,
        3.55,
        3.85,
        2.75,
        "3. Statutory clock",
        "Python. Not the model.\n24 hours for an emergency.\n10, 3 and 5 working days.\n12 weeks only if an officer\nrecords the long-stop.",
        "#fff6e0",
        "#8a5a00",
    )
    box(
        ax,
        0.3,
        0.35,
        6.3,
        2.7,
        "4. Officer approves",
        "Approves the category and the clock.\nEdits the written summary.\nSends and files it themselves,\nin the landlord's own systems.\nThe endeavours record is a draft.",
        "#fff8e6",
        "#8a5a00",
    )
    box(
        ax,
        6.9,
        0.35,
        5.3,
        2.7,
        "Not a tool of the agent",
        "No send to the tenant.\nNo housing-system write.\nNo finding that endeavours are made out.\nNo Ombudsman referral.\nNo decant booking and no spend.",
        "#fdecea",
        "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
