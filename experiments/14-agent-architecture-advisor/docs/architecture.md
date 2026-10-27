# Architecture

Experiment 14, the Agent Architecture Advisor. Catalogue ID G002. Autonomy of the advisor is A0.

The architect describes one proposed use case. Python scores structured fields against a fixed table. The result is a draft of five options, a catalogue autonomy level from A0 to A2, approval points, and a permissions-manifest skeleton. The architect confirms every option. The process stops. Nothing is selected and nothing is deployed.

```
Architect  →  harness (skills or one topic)  →  src/advise.py
                                                      │
                                                      ├─ strip payload keys, scan free text
                                                      ├─ src/rules.py scores the structured fields
                                                      ├─ src/sources.py marks a stale pin
                                                      └─ Experiment 03 generator drafts the skeleton
                                                      │
Architect  ←  JSON labelled DRAFT FOR ARCHITECT REVIEW
```

`src/advise.py` does not call a model and does not open the network. The same use case and the same as-of date produce the same JSON. Free text is not an input to the rules.

The diagram is `architecture_diagram.png`, drawn by `generate_diagram.py`. Matplotlib is used only to draw it. It is not a dependency of the advisor.

## What crosses a trust boundary

| From | To | What moves | What does not |
|---|---|---|---|
| Architect | Harness | One use-case file and an as-of date | A decision, a licence lookup |
| Harness | `advise` | That file | A new URL, a price, an instruction from the narrative |
| `advise` | Experiment 03 | An inventory-shaped record at A0, A1, or A2 | An approve flag, autonomy A3, injection text |
| Advisor | Architect | The JSON draft | A selected platform, a deployment |

## Human approval

The highlighted step on the diagram is the architect. They confirm each option, including no agent, and they confirm the autonomy level. A governance owner approves the skeleton before anyone relies on it. Those confirmations are not written back by this starter. `architect_confirmed` and `manifest_approved` stay false.
