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
    ax.text(x + 0.18, y + h - 0.58, body, ha="left", va="top", fontsize=8.2, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(13.2, 7.6))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.3, 7.25, "Evidence pack builder — draft index", fontsize=14, fontweight="bold", color="#1a1a1a")
    ax.text(
        0.3, 6.88,
        "Experiment 18. Autonomy A1. Catalogue L004. A named person approves the exact list. The agent does not.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 3.85, 4.05, 2.65,
        "1. Evidence pack approver",
        "Types the scopes, the search\nperiod, and the as-of date.\nPastes one synthetic set.\nItem text is untrusted.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 4.55, 3.85, 4.15, 2.65,
        "2. Either harness",
        "Copilot Studio, standard\ntopic or GitHub Copilot\nharness. Both call build_pack.\nSandbox draft only.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.95, 3.85, 3.95, 2.65,
        "3. Python pack builder",
        "Scope check, hash, pages.\nExperiment 12 inventories.\nExperiment 08 flags identifiers.\nApproval stays empty.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 4.15, 3.15,
        "4. Human approval",
        "The named approver records\nthe exact item ids and every\nredaction decision. A sentence\nin an item cannot do this.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 4.6, 0.35, 4.2, 3.15,
        "5. Export index",
        "Only after that approval.\nPage order follows the list.\nNo document bodies.\nNot a disclosure.",
        "#fff3cd", "#997404",
    )
    box(
        ax, 9.0, 0.35, 3.9, 3.15,
        "Not a tool of the agent",
        "No send and no disclosure.\nNo exemption decision.\nNo production write.\nNo release of redacted text.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
