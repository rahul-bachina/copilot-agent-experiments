# Architecture

Experiment 41 is a local checker. A service representative pastes one synthetic case history. Either Copilot Studio harness calls `summarise()` in `src/summarise.py`. The function calls Experiment 08 `propose()`, copies current lines that are not instructions and not identifier hits, and checks every sentence against the event, paragraph, and line it cites. The draft stops. The representative checks accuracy outside the agent.

```
Service representative
        |
        | one synthetic case, one as-of date
        v
Either harness (standard topic, or three skills)
        |
        | no customer contact, no record write
        v
summarise()
        |
        +-- Experiment 08 propose()  (counts identifiers, does not release)
        +-- src/injection.py         (records instructions, strips output keys)
        +-- src/citations.py         (one verdict per sentence)
        |
        v
JSON draft. human_approval is null. accuracy_checked is false.
        |
        v
Service representative checks every cited sentence.
Contact, record change, closure, and redress stay outside the agent.
```

The rendered picture is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py`. Matplotlib is used only for that script. It is not a runtime dependency.

## What is deterministic

The same case and the same as-of date produce the same JSON. There is no model call and no network call. `foundry_called` is false. Support is a contiguous copy of the cited lines after case and whitespace are folded. That is the Experiment 33 rule, applied to events rather than document pages. This folder does not import Experiment 33.

## What the human approval is

Autonomy is A0. Producing the draft has no external effect and does not need an approval click inside the tool. Relying on it does. The catalogue checkpoint is that the service representative checks accuracy. `record_accuracy_check` can record that check only when the role and the name come from outside the agent, every sentence is marked, and the reading is complete and current. The record of that check is still not a write to the case system and not a message to the customer.

## Dynamics 365

The catalogue stack is Dynamics 365 and Copilot Studio. This starter does not connect to Dynamics 365 Customer Service. A later connector, if one is added, may read a case the representative has already chosen and must not update it. Product click-paths were not opened on 9 November 2026. That connector is unverified here.

## Microsoft Foundry

Described in [foundry.md](foundry.md). Not called. A product page was not opened on 9 November 2026.
