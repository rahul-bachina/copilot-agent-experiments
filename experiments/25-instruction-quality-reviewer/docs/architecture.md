# Architecture

Experiment 25, the Instruction Quality Reviewer. Catalogue ID G003. Autonomy of the reviewer is A0.

The agent owner supplies one system prompt, one SKILL.md, or one topic prompt, and an as-of date. Python scores the text against a fixed checklist. The result is a findings report and a proposed diff. The agent owner approves any prompt change. The process stops. Nothing is edited and nothing is deployed.

```
Agent owner  →  harness (skills or one topic)  →  src/review.py
                                                      │
                                                      ├─ strip payload keys, scan the text
                                                      ├─ src/checklist.py scores C1 to C9
                                                      ├─ src/diffing.py proposes a diff
                                                      ├─ src/sources.py marks a stale pin
                                                      ├─ Experiment 03 drafts a skeleton only if no manifest was supplied
                                                      └─ Experiment 14 scores a structured use case only if one was supplied
                                                      │
Agent owner  ←  JSON labelled DRAFT FOR AGENT OWNER REVIEW
```

`src/review.py` does not call a model and does not open the network. The same bundle and the same as-of date produce the same JSON. Instruction text cannot set the score, the approval, or the applied flag.

The diagram is `architecture_diagram.png`, drawn by `generate_diagram.py`. Matplotlib is used only to draw it. It is not a dependency of the reviewer.

## What crosses a trust boundary

| From | To | What moves | What does not |
|---|---|---|---|
| Agent owner | Harness | One instruction file, an optional manifest, an optional use case, and an as-of date | A decision, an edited prompt |
| Harness | `review` | That bundle | A new URL, a price, an instruction from the file under review |
| `review` | Experiment 03 | An inventory-shaped record at A0, and only when no manifest was parsed | An approve flag, autonomy A3, injection text |
| `review` | Experiment 14 | Structured fields of a use case, when one was supplied | The free-text narrative as a rule input, a platform selection |
| Reviewer | Agent owner | The JSON draft and a proposed diff | An applied rewrite, a deployment |

## Human approval

The highlighted step on the diagram is the agent owner. They approve prompt changes. They accept or reject each finding before a rewrite is kept. A governance owner relies on a manifest skeleton only when one was drafted because none was supplied. Those confirmations are not written back by this starter. `owner_approved`, `diff_applied`, and `deployed` stay false.
