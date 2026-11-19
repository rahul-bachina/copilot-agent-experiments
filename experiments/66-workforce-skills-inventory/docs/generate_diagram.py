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
        "Workforce skills inventory — the employee confirms each skill",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 66. Autonomy A0. Catalogue H010. The agent does not write to an HR system or rate performance.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 3.15, 2.6,
        "1. Evidence",
        "CV extracts, learning\nrecords, project summaries\nthe employee supplied.\nApproval text is not approval.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.85, 4.2, 2.6,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe Python core.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.0, 3.85, 4.5, 2.6,
        "3. Proposals",
        "Snippet, confidence band,\nneeds confirmation.\nExperiments 08, 61, 62\nare read-only where used.",
        "#fff6e8", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.3, 3.15,
        "4. Human approval",
        "The employee confirms, rejects, or corrects each skill, on that hash.\n"
        "HR validates only after that step. The employee can still reject.\n"
        "Distress, an objection, or a pay, promotion, redundancy, or\n"
        "disciplinary use is a route to HR. Nothing is written to HR.",
        "#fde8e8", "#8f1d1d",
    )
    box(
        ax, 8.75, 0.35, 3.75, 3.15,
        "Not a tool",
        "Write to an HR system.\nRate performance.\nSet pay or promotion.\nSelect for redundancy.\nDrop a legal hold.",
        "#f4f4f4", "#555555",
    )

    fig.tight_layout()
    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
