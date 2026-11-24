# Microsoft Copilot harness

This is the layout the common brief calls the GitHub Copilot harness: skills under `skills/`, with tool contracts and the same approval gates as the standard harness. The harness overview was not re-opened for this experiment. On the reading recorded for Experiment 70 on 20 November 2026, the product page uses the name Microsoft Copilot harness. It does not use the words GitHub Copilot harness. That point is unverified against a fresh opening.

The skills are:

- `assemble-board-pack` calls `assemble_pack()`.
- `route-to-secretary` calls `record_route_seen()`.
- `record-secretary-approval` calls `record_secretary_approval()`.
- `draft-action-carry-forward` reads the action log already on the draft.

Each skill description is a single frontmatter line and says when to use the skill. The files do not list trigger phrases and do not assign routing weights.

File tools this harness can use are not used to edit a paper, to circulate a pack, or to file minutes. Memory is not used to store an approval. An approval is the separate object checked by `src/pack.py`.

No Work IQ call is made. Catalogue row L010 names Work IQ. A permission-aware read of a live board library was not opened and is unverified.
