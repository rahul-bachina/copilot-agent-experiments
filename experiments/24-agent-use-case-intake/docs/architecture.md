# Architecture

Experiment 24, the agent use-case intake. Catalogue ID G001. Autonomy of this intake agent is A1.

A business team describes one proposed agent. Python reads structured fields and calls three earlier experiments. The result is a draft classification: a suggested autonomy of A0, A1, or A2, a risk tier for the queue, a DPIA indication, an ATRS indication, and a resemblance to a catalogue pattern already in this repository. The governance team approves the classification or changes it. The process stops. Nothing is approved and nothing is provisioned.

```
Team  →  harness (skills or one topic)  →  src/classify.py
                                                │
                                                ├─ strip payload keys, scan free text
                                                ├─ Experiment 14 rules.score (autonomy A0–A2)
                                                ├─ Experiment 19 screen() (DPIA indication)
                                                ├─ Experiment 03 draft_atrs (applicability note)
                                                └─ src/sources.py marks a stale pin
                                                │
Governance team  ←  JSON labelled DRAFT FOR THE GOVERNANCE TEAM
```

`src/classify.py` does not call a model and does not open the network. The same proposal and the same as-of date produce the same JSON. Free text is not an input to the rules. A request for autonomy A3 is flagged out of scope. The suggested level is never A3.

The diagram is `architecture_diagram.png`, drawn by `generate_diagram.py`. Matplotlib is used only to draw it. It is not a dependency of the classifier.

## What crosses a trust boundary

| From | To | What moves | What does not |
|---|---|---|---|
| Team | Harness | One proposal file and an as-of date | An approval, a provisioned agent |
| Harness | `classify` | That file | A new URL, a price, an instruction from the narrative |
| `classify` | Experiments 14, 19, and 03 | Structured fields only | An approve flag, autonomy A3, a call to the manifest generator |
| Intake | Governance team | The JSON draft | An approved use case, a deployment, an ATRS email |

## Human approval

The highlighted step on the diagram is the governance team. They approve the intake classification or they change it. A privacy officer decides whether a DPIA indication is a reason to start a DPIA. Those decisions are not written back by this starter. `approved`, `use_case_approved`, and `governance_decision` stay false or null.
