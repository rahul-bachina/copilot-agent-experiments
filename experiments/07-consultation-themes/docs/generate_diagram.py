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
    fig, ax = plt.subplots(figsize=(12.6, 7.6))
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3,
        7.25,
        "Consultation themes — essay to data",
        fontsize=15,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        0.3,
        6.88,
        "Experiment 07. The analyst approves the framework and every sampled row. Nothing is published.",
        fontsize=9,
        color="#444444",
    )

    box(
        ax,
        0.25,
        3.7,
        3.7,
        2.85,
        "1. Standard harness",
        "Intake and status only.\nRedact known identifiers.\nFlag instructions.\nCluster campaign copies.\nNo theme codes.",
        "#e7f1fb",
        "#1d4e89",
    )
    box(
        ax,
        4.2,
        3.7,
        4.15,
        2.85,
        "2. GitHub Copilot harness",
        "Lead analyst workflow.\nPropose a framework, then code.\nWilson interval on unique voices.\nMinority codes kept.\nEvery theme lists response IDs.",
        "#e8f6ef",
        "#1e6b45",
    )
    box(
        ax,
        8.6,
        3.7,
        3.7,
        2.85,
        "3. Human approval",
        "Analyst approves the codebook.\nAnalyst decides every sampled row.\nStale exports stay blocked\nuntil that is acknowledged.",
        "#fde8c8",
        "#8a4b08",
    )
    box(
        ax,
        0.25,
        0.35,
        8.1,
        3.0,
        "Deterministic core — same code for both harnesses",
        "Python codebook. Optional ThemeFinder adapter, MIT, not vendored.\n"
        "Falls back if the package is missing. Does not call the rule that drops small themes.\n"
        "Campaign copies count once in the proportion and stay in the audit.\n"
        "A response cannot approve the framework or publish the draft.",
        "#f4f4f4",
        "#444444",
    )
    box(
        ax,
        8.6,
        0.35,
        3.7,
        3.0,
        "Not a tool of the agent",
        "No publication.\nNo email.\nNo consultation-system write.\nNo policy recommendation.\nNo self-approved framework.",
        "#fdecec",
        "#8a1f1f",
    )

    fig.tight_layout()
    destination = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(destination, dpi=140)
    print(destination)


if __name__ == "__main__":
    main()
