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
    ax.text(x + 0.16, y + h - 0.55, body, ha="left", va="top", fontsize=8.0, color="#333333", linespacing=1.35)


def main() -> None:
    fig, ax = plt.subplots(figsize=(12.8, 7.6))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(0.3, 7.2, "Subject access request — the officer approves the bundle", fontsize=13, fontweight="bold", color="#1a1a1a")
    ax.text(0.3, 6.82, "Experiment 83. Autonomy A1. Catalogue UK11. The agent does not send, delete, edit, or decide an exemption.", fontsize=9, color="#444444")
    box(ax, 0.25, 3.7, 3.0, 2.75, "1. Synthetic request", "Letter, email, or web form.\nRecords export.\nPinned directory only.\nQuestion date, not today.", "#f4f1ea", "#8a8175")
    box(ax, 3.5, 3.7, 3.15, 2.75, "2. Either harness", "Standard topic, or the\nMicrosoft Copilot harness.\nBoth call scope().\nNo model on this path.", "#e7f0f4", "#3d6d82")
    box(ax, 6.9, 3.7, 3.15, 2.75, "3. Draft and hash", "Both deadline readings.\nRedactions and candidates.\nAgent-held copy.\nNothing is sent.", "#eef6ea", "#3f6b45")
    box(ax, 10.2, 3.7, 2.35, 2.75, "4. Officer", "Sees a sensitive route.\nAccepts or rejects\neach redaction.\nApproves this hash.", "#f8efe4", "#8a5a2a")
    ax.annotate("", xy=(3.45, 5.05), xytext=(3.25, 5.05), arrowprops=dict(arrowstyle="->", color="#333333"))
    ax.annotate("", xy=(6.85, 5.05), xytext=(6.65, 5.05), arrowprops=dict(arrowstyle="->", color="#333333"))
    ax.annotate("", xy=(10.15, 5.05), xytext=(10.05, 5.05), arrowprops=dict(arrowstyle="->", color="#333333"))
    box(ax, 0.25, 0.35, 12.3, 2.9, "Not a tool", "Sending the response, deleting a record, editing a record, and deciding an exemption raise.\nA sentence in the request is not the approval. A re-hashed edit is rejected.\nExperiment 08 proposes UK identifiers. Experiment 12 returns an unconfirmed inventory.\nExperiment 01 is not called. FOI section 40(1) is a route, not a disclosure.", "#f7f7f7", "#666666")
    out = Path(__file__).resolve().parent / "architecture_diagram.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    main()
