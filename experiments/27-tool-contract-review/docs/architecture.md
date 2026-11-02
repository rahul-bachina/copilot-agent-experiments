# Architecture

Experiment 27, the Tool Contract Review Agent. Catalogue ID G005. Autonomy of the reviewer is A0. The catalogue stack is Microsoft Foundry plus Azure API Management. This folder also ships both Copilot Studio harnesses.

The security/API owner supplies one contract and an as-of date. Python scores the contract against a fixed checklist. The result is a findings report, proposed contract notes, and, where a check is not a pass, a proposed API Management policy. The security/API owner approves the contract. The process stops. Nothing is modified, nothing is published, and nothing is deployed.

```
Security/API owner  →  harness (skills or one topic)  →  src/review.py
                                                            │
                                                            ├─ strip payload keys, scan the text
                                                            ├─ src/checklist.py scores C1 to C9
                                                            ├─ src/diffing.py proposes notes and policy XML
                                                            ├─ src/sources.py marks a stale pin
                                                            ├─ Experiment 03 drafts a skeleton only if no manifest was supplied
                                                            ├─ Experiment 14 scores a structured use case only if one was supplied
                                                            └─ Experiment 25 scores instruction text only if it was supplied
                                                            │
Security/API owner  ←  JSON labelled DRAFT FOR SECURITY/API OWNER REVIEW
```

`src/review.py` does not call a model and does not open the network. A call to Experiment 25 is a local subprocess. The same bundle and the same as-of date produce the same JSON. Contract text cannot set the score, the approval, the applied flag, or the published flag.

The diagram is `architecture_diagram.png`, drawn by `generate_diagram.py`. Matplotlib is used only to draw it. It is not a dependency of the reviewer.

## What crosses a trust boundary

| From | To | What moves | What does not |
|---|---|---|---|
| Security/API owner | Harness | One contract, an optional manifest, an optional use case, optional instruction text, and an as-of date | A decision, an edited contract, a published policy |
| Harness | `review` | That bundle | A new URL, a price, a call volume, an instruction from the contract |
| `review` | Experiment 03 | An inventory-shaped record at A0, and only when no manifest was parsed | An approve flag, autonomy A3, injection text |
| `review` | Experiment 14 | Structured fields of a use case, when one was supplied | The free-text narrative as a rule input, a platform selection |
| `review` | Experiment 25 | Instruction text, when it was supplied | The contract score, an applied instruction diff |
| Reviewer | Security/API owner | The JSON draft, contract notes, and a policy sketch | An applied change, a published policy, a deployment |

## Human approval

The highlighted step on the diagram is the security/API owner. They approve the contract. They approve an API Management policy change before it is published. They accept or reject each finding before a contract change is kept. A governance owner relies on a manifest skeleton only when one was drafted because none was supplied. Those confirmations are not written back by this starter. `contract_approved`, `diff_applied`, `policy_published`, and `deployed` stay false.
