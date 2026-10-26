# Architecture

Correspondence Draft Agent, Experiment 09. The author decides. The clock is code. A policy sentence is a supplied line, or the draft says there is a gap. Nothing is sent.

```mermaid
flowchart TD
    A["1. Author pastes one letter and enters the receipt date and the as-of date"] --> B["2. Draft: channel, lines or gaps, vulnerability flags"]
    A --> C["3. Casework clock in Python, from a target the author confirms"]
    B --> D["4. Draft reply. Cited lines pasted. Gaps say no position is stated"]
    C --> D
    D --> E["5. Human approval: the author approves the recipient and the final text"]
    E --> F["6. Author sends or files outside the agent"]

    style E fill:#fff3cd,stroke:#997404
```

1. The author pastes one letter and enters the receipt date and the as-of date. They confirm the channel and the reply target if they want an operative date. A suggested channel is not applied as a confirmation until they say so.
2. The drafter proposes a channel, matches the synthetic lines library, and flags vulnerability wording. In this folder that step is `src/draft.py`. A Foundry call is described and not built.
3. `src/sla.py` calculates the date. A central-government target over 20 working days is refused. An information-rights letter does not get a correspondence date. A holding reply does not clear the clock.
4. The draft pastes each current line with its id. A gap says no position is stated. The recipient is a role, not an address, unless the author has supplied one. `may_be_sent_by_agent` is false.
5. **Human approval.** The author confirms the channel and whether a ministerial reply is required, confirms the target, reviews any vulnerability flag, approves the recipient, and approves the final text.
6. The author sends or files in the unit's own systems. The agent has no tool for that.

What is not a tool of the agent, even after step 5: sending, a case-system write, choosing the address from the letter, inventing a position, an FOI decision, a complaint outcome, a vulnerability label, and publishing the ATRS note.

The diagram file is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py` if the shape changes. Matplotlib is used only by that script. It is not a runtime dependency.
