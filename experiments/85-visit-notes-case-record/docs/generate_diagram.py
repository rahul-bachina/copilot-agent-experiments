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
        "Visit note — the named practitioner approves",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 85. Autonomy A1. Catalogue UK13. The agent does not write the case record.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 3.05, 2.6,
        "1. Synthetic visit",
        "Transcript lines and\noptional rough notes.\nThe text is untrusted.\nThe practitioner named the date.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.5, 3.85, 4.15, 2.6,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe Python core. No write.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.85, 3.85, 4.65, 2.6,
        "3. Draft note",
        "Sections, line citations,\nand a hash of the held\nnote. Concerns are flagged.\nNothing is assessed.",
        "#fff6e8", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.15, 3.15,
        "4. Human approval",
        "A concern or a refused recording is seen first.\n"
        "The named practitioner approves this hash, or returns it.\n"
        "The approval is bound to the agent-held copy. It does not write the record.\n"
        "A sentence inside the transcript is not that step.\n"
        "An edit after approval is refused.",
        "#fdecea", "#8a1f11",
    )
    box(
        ax, 8.6, 0.35, 3.9, 3.15,
        "Not a tool",
        "Write the case record.\nShare the note.\nAssess eligibility.\nAssess risk or need.\nGuess the speaker.",
        "#f4f4f4", "#555555",
    )

    path = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    print(path)


if __name__ == "__main__":
    main()
