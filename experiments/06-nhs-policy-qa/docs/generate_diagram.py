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
        "Policy Q&A — NHS corporate services",
        fontsize=15,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        0.3,
        6.68,
        "Experiment 06. Approved policies only. The policy owner approves sources. Clinical questions are refused.",
        fontsize=9,
        color="#444444",
    )

    box(
        ax,
        0.3,
        3.55,
        3.7,
        2.75,
        "1. Staff question",
        "One question.\nHR, finance, procurement,\nIT, or estates.\nThe as-of date is typed.\nClinical questions stop here.",
        "#e7f1fb",
        "#1d4e89",
    )
    box(
        ax,
        4.25,
        3.55,
        3.9,
        2.75,
        "2. Approved register",
        "Python. Not the model.\nOwner-approved and in date.\nQuote, version, review date.\nI don't know if nothing matches.\nStale text is withheld.",
        "#e8f6ee",
        "#1e7a46",
    )
    box(
        ax,
        8.4,
        3.55,
        3.8,
        2.75,
        "3. Policy owner",
        "Approves each source.\nSees coverage, conflicts,\nand stale policies.\nA change note is a draft.\nThe owner accepts it outside.",
        "#fff6e0",
        "#8a5a00",
    )
    box(
        ax,
        0.3,
        0.35,
        6.3,
        2.7,
        "4. Person decides",
        "A quotation can be relied on\nonly when the register says so.\nA conflict is not resolved.\nA refusal is the whole answer.\nNothing is sent.",
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
        "No clinical advice.\nNo entitlement decision.\nNo publish and no SharePoint write.\nNo send.\nNo spend and no contract award.",
        "#fdecea",
        "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
