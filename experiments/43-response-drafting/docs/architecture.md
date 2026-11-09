# Architecture

The representative pastes one synthetic case and types the as-of date. Either Copilot Studio harness calls `src/response.py`. The core calls Experiment 08 to count identifiers and Experiment 09 to decide whether a snippet may be cited. It then runs the tone screen and the plain-English screen. `human_approval` comes back empty.

The representative reviews the draft. They may record approval for their own channel, ask for a revision, or reject it. Approval does not send. The representative sends, if they send, outside the agent.

```text
Representative
    |
    v
Copilot Studio (standard topic, or GitHub Copilot harness skills)
    |
    v
src/response.py
    |-- Experiment 08 propose()     counts identifiers, does not release
    |-- Experiment 09 line_applicability()
    |-- tone screen and plain-English screen
    v
JSON draft, human_approval null
    |
    v
Representative reviews and sends on their own channel
    (not a tool of this agent)
```

No model is required for the draft. Microsoft Foundry, if used later, may only restate fields already in the JSON. Dynamics 365 and the mailbox are out of scope. See [dynamics-365-and-microsoft-365.md](dynamics-365-and-microsoft-365.md) and [foundry.md](foundry.md).

The diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py` if the boxes change. Matplotlib is used only by that script. It is not a runtime dependency.
