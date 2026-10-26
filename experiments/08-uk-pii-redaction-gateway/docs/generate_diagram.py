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
    ax.text(x + 0.18, y + h - 0.55, body, ha="left", va="top", fontsize=8.5, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.3, 6.85, "UK identifier PII gateway", fontsize=15, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.5, "Experiment 08. A privacy reviewer approves. Nothing is released.", fontsize=9, color="#444444")

    box(
        ax, 0.3, 3.55, 3.5, 2.55,
        "1. Caller",
        "Another experiment, or\na reviewer, passes\none text. Synthetic\nfixtures in this repo.\nNo register lookup.",
        "#e7f1fb", "#1d4e89",
    )
    box(
        ax, 4.15, 3.55, 4.0, 2.55,
        "2. Deterministic detectors",
        "NHS modulus 11.\nNINO prefix class.\nSort code, account,\npostcode, CRN, IBAN.\nPython. Not the model.",
        "#e8f6ee", "#1e7a46",
    )
    box(
        ax, 8.5, 3.55, 3.7, 2.55,
        "3. Proposal",
        "Placeholders and a\nDPO log with no raw\nvalues. A model\nsuggestion is off\nunless the caller opts in.",
        "#fff6e0", "#8a5a00",
    )
    box(
        ax, 0.3, 0.35, 5.7, 2.55,
        "4. Privacy reviewer",
        "Approves the redacted output\nbefore any release. Can reject\na model suggestion. Decides\nwhether a token map may be stored.",
        "#fff8e6", "#8a5a00",
    )
    box(
        ax, 6.3, 0.35, 5.9, 2.55,
        "Not a tool of the agent",
        "No release and no send.\nNo anonymisation claim.\nNo Key Vault write.\nNo Companies House or NHS lookup.",
        "#fdecea", "#8a1c13",
    )

    fig.tight_layout()
    out = Path(__file__).with_name("architecture_diagram.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
