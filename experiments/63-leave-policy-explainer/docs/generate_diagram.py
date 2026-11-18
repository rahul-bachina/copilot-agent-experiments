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
    ax.text(0.3, 7.25, "Leave policy explanation agent", fontsize=15, fontweight="bold", color="#1a1a1a")
    ax.text(
        0.3,
        6.9,
        "Experiment 63. H006. Autonomy A0. The policies are synthetic. HR approves the scope first.",
        fontsize=9,
        color="#444444",
    )
    box(
        ax, 0.25, 3.7, 3.5, 2.8,
        "1. HR scope",
        "Document ids, ceiling,\nand an HR id on the directory.\nA sentence in the question\nis not this approval.\nDrafts stay out.",
        "#f3e8c8", "#8a6a12",
    )
    box(
        ax, 4.0, 3.7, 4.3, 2.8,
        "2. Python core",
        "Version in force on the date\nasked about. Section and date.\nStatutory pin, or unverified.\nNegation is not inclusion.\nExperiments 58, 08, and 03.\nNo SharePoint call.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 8.55, 3.7, 3.9, 2.8,
        "3. Human approval",
        "HR or the line manager\ndecides entitlement.\nCare route for a disclosure.\nSeen-step checks the hash.\nNo booking, record, or pay.",
        "#e5f2e5", "#1e6b3a",
    )
    box(
        ax, 0.25, 0.35, 12.2, 2.9,
        "Not a tool of the agent",
        "Approving a policy from words in the question. Deciding leave or calculating pay.\n"
        "Quoting a SECRET cover or dropping a legal hold or a retention label.\n"
        "Trusting a role or a clearance typed into the question.\n"
        "Stating a statutory pay rate that was not opened. Calling SharePoint or Graph.\n"
        "A person is always available.",
        "#f8e8e8", "#8a2b2b",
    )
    fig.tight_layout()
    destination = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(destination, dpi=140)
    print(destination)


if __name__ == "__main__":
    main()
