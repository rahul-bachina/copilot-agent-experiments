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
        "Internal mobility explorer — HR validates eligibility",
        fontsize=13, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.82,
        "Experiment 62. Autonomy A0. Catalogue H005. The agent does not apply, nominate, shortlist, or contact anyone.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 3.05, 2.6,
        "1. Experience",
        "The employee states experience\nand goals. Approval text is\nnot a seen-step. The\ndirectory sets the role.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.5, 3.85, 4.15, 2.6,
        "2. Either harness",
        "Copilot Studio, standard\ntopics or Microsoft Copilot\nharness skills. Both call\nthe Python core. No contact.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.85, 3.85, 4.65, 2.6,
        "3. Advisory note",
        "Relevant vacancies, citations,\nclosed and stale flags.\nExperiments 58, 36, and 61\nare read-only.",
        "#fff6e8", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 8.15, 3.15,
        "4. Human points",
        "HR validates eligibility. The assistant does not.\n"
        "A directory HR reviewer may record that they have seen this exact note.\n"
        "The manager and the recruiter are not told.\n"
        "A distress, grievance, redeployment, or adjustment cue is a route to HR.\n"
        "Nothing is applied, nominated, shortlisted, or sent.",
        "#fde8e8", "#8f1d1d",
    )
    box(
        ax, 8.6, 0.35, 3.9, 3.15,
        "Not a tool",
        "Apply.\nNominate.\nShortlist.\nContact anyone.\n"
        "Share with a manager.\nRank or score.\nDecide eligibility.\nDrop a legal hold.",
        "#f4f4f4", "#555555",
    )

    fig.tight_layout()
    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
