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
    ax.text(
        x + w / 2, y + h - 0.22, title,
        ha="center", va="top", fontsize=10, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        x + 0.14, y + h - 0.48, body,
        ha="left", va="top", fontsize=7.6, color="#333333", linespacing=1.32,
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.4))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.4)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        0.3, 7.05, "Agent inventory and ATRS assurance pack",
        fontsize=15, fontweight="bold", color="#1a1a1a",
    )
    ax.text(
        0.3, 6.72,
        "Experiment 03. Drafts only. The governance owner approves every status change.",
        fontsize=9, color="#444444",
    )

    box(
        ax, 0.25, 4.15, 3.9, 2.3,
        "1. Inventory record",
        "One row. Experiments 01, 02,\n04, and 05 are the worked\nexamples. Synthetic CSV stands\nin for Dataverse. No tenant.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 4.4, 4.15, 4.0, 2.3,
        "2. Deterministic drafts",
        "ATRS v4.0 fields copied or left\nas gaps. Playbook map. DPIA\nskeleton. DUAA screen.\nFCA-style row. Manifest.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.65, 4.15, 3.9, 2.3,
        "3. Findings",
        "G006 lists injection hits.\nG007 checks grounding and\na draft 180-day threshold.\nNeither evaluation clears.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.25, 0.35, 6.1, 3.4,
        "4. Governance owner",
        "Approves or refuses every lifecycle\nstatus change, outside this tool.\nThe core applies a change only when\nthat external decision is supplied.\nIt still does not mark the pack approved.\nSending and publishing stay with people.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.6, 0.35, 5.95, 3.4,
        "Not a tool of the agent",
        "No approval of a manifest, DPIA, or ATRS record.\nNo email to the ATRS team.\nNo Dataverse write.\nNo ATRS scope decision.\nNo DUAA or FCA determination.\nNo autonomy A3.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
