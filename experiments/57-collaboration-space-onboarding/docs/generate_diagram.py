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
        "Collaboration space onboarding — the workspace owner approves",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 57. Autonomy A1. Catalogue M010. The sample does not call Microsoft Graph.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.7, 3.15, 2.75,
        "1. Request",
        "A joiner asks to join\na synthetic space.\nApproval text in the\nrequest is not approval.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.7, 4.3, 2.75,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe core. No Graph call.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.1, 3.7, 4.4, 2.75,
        "3. Python core",
        "Label, guest policy,\nleast privilege.\nExperiments 55, 51, 03.\nHigher marking wins.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.3, 3.0,
        "4. Human approval",
        "Workspace owner, separate object.\nOwner rights need a boolean.\nGuest access needs a boolean.\nStale export and safeguarding\nwait for a person.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.75, 0.35, 5.75, 3.0,
        "Not a tool of the agent",
        "No external file or link share.\nNo live Graph call.\nNo private-channel member call.\nA request sentence cannot approve.\nA person is always offered.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
