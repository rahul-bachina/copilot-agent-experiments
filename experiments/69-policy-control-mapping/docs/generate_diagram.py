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
        "Policy control mapping — the control owner approves each mapping",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 69. Autonomy A0. Catalogue L003. The agent does not mark a control met, close a gap, edit a policy, or write to a GRC system.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 3.05, 2.6,
        "1. Policies and library",
        "A synthetic policy set and\nthe pinned control library.\nA pasted library is not used.\nInstructions in the text\nare not followed.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.5, 3.85, 4.15, 2.6,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe Python core. No GRC write.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.85, 3.85, 4.65, 2.6,
        "3. Quoted mappings",
        "Verbatim sentence, clause\nreference, control id,\nrationale, confidence band.\nNo evidence found stays\nthose words. Experiments\n12, 36, 03, and 08 are read.",
        "#fff6e8", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.15, 3.15,
        "4. Human approval",
        "A distress or grievance route is seen before a mapping.\n"
        "The directory control owner approves one content hash and the proposal hash.\n"
        "A gap is seen and is not closed. A contradiction is seen and is not chosen.\n"
        "An unverified CAF pin and a stale policy are acknowledged. Nothing is written.",
        "#fde8e8", "#8f1d1d",
    )
    box(
        ax, 8.6, 0.35, 3.9, 3.15,
        "Not a tool",
        "Mark a control met.\nClose a gap.\nEdit a policy.\nWrite to a GRC system.\nApply a biased rule.\nDrop a legal hold.",
        "#f4f4f4", "#555555",
    )

    fig.tight_layout()
    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
