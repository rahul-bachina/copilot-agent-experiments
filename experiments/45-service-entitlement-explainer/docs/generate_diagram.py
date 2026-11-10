#!/usr/bin/env python3
"""Render docs/architecture_diagram.png. Matplotlib is used only for this script."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


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
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="top", fontsize=11, fontweight="bold", color="#1a1a1a")
    ax.text(x + 0.16, y + h - 0.58, body, ha="left", va="top", fontsize=8.2, color="#333333", linespacing=1.35)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.1,
            color="#444444",
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.8))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.8)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3,
        7.45,
        "Service entitlement explainer — quote the clause, do not decide the cover",
        fontsize=13,
        fontweight="bold",
        color="#1a1a1a",
    )
    ax.text(
        0.3,
        7.08,
        "Experiment 45. Catalogue C007. Autonomy A0. A human decides a disputed entitlement.",
        fontsize=9,
        color="#444444",
    )

    box(
        ax, 0.25, 3.85, 3.15, 2.9,
        "1. Adviser",
        "Supplies one synthetic plan,\nan approved rules table,\na question, and an as-of date.\nAldermere is fictional.\nDoes not paste a live record.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 3.6, 3.85, 4.05, 2.9,
        "2. Either harness",
        "GitHub Copilot harness:\nfour skills, then stop.\nStandard harness: one topic.\nBoth call the same Python.\nNeither is the Copilot service.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 7.85, 3.85, 4.7, 2.9,
        "3. Python explanation",
        "Instruction spans are removed.\nThe rest of the question stays.\nOne rule, or a route.\nExperiment 38 checks the clause.\nExperiment 40 is not imported.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 7.7, 3.15,
        "4. Human approval",
        "human_approval stays empty on the draft.\nA person is offered on every explanation.\nThe entitlement owner decides a dispute,\nan ambiguity, a conflict, or a stale rule.\nA recorded code is not applied to a record.\nThe agent still does not send the explanation.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 8.15, 0.35, 4.4, 3.15,
        "Not a tool of this agent",
        "No grant.\nNo refusal.\nNo change to the entitlement.\nNo section 69 choice.\nNo unfair-term finding.\nNo Dynamics 365 write.\nNo message.",
        "#fdecea", "#9b2c2c",
    )
    arrow(ax, 3.4, 5.3, 3.6, 5.3)
    arrow(ax, 7.65, 5.3, 7.85, 5.3)
    arrow(ax, 10.1, 3.85, 4.1, 3.5)

    path = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    print(path)


if __name__ == "__main__":
    main()
