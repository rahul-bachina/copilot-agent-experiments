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

    ax.text(0.3, 7.05, "FCA cryptoasset readiness — draft observation register", fontsize=14, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.68, "Experiment 04. Autonomy A0. The Compliance Officer or MLRO decides. The checker does not.", fontsize=9, color="#444444")

    box(
        ax, 0.25, 3.55, 3.15, 2.75,
        "1. Reviewer",
        "Supplies one synthetic\npolicy pack. Types the\nas-of date. Confirms\nthe pack is theirs\nto review.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.55, 4.3, 2.75,
        "2. Lead harness",
        "Copilot Studio on the\nGitHub Copilot harness.\nSkills classify the files,\nthen call the checker.\nSandbox draft only.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.1, 3.55, 4.4, 2.75,
        "3. Python checker",
        "Pinned FCA pages.\nPhrase check. Injection\ndropped. Stale pin flagged.\nNo model. No network.\nReadiness stays empty.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.3, 2.85,
        "4. Human review",
        "Compliance Officer or MLRO reads every row.\nThey accept or reject it as a gap.\nThey re-open fca.org.uk if a source is stale.\nThey file nothing until they decide to, outside the agent.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.75, 0.35, 5.75, 2.85,
        "Not a tool of the agent",
        "No readiness finding.\nNo regulatory or legal advice.\nNo Connect submission. No SAR.\nNo financial-promotion approval.\nNo production write and no send.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
