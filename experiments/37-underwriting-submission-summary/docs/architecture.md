# Architecture

Experiment 37, catalogue ID B006, autonomy A0.

The underwriter supplies one synthetic submission and an as-of date. Either Copilot Studio harness calls `summarise()`. That function calls Experiment 12 to inventory the files, with no purpose and no hand-off, and calls Experiment 29 only for the number and date boundary check. It copies current contiguous lines into the closed field list. A missing field is `not stated`. Microsoft Foundry is described and not called.

The underwriter reviews every cited fact. Coverage, price, any message to the broker, and any write to the underwriting system stay outside the agent.

```
Underwriter
    |
    v
Either harness (standard topic, or three skills)
    |
    v
summarise()
    |-- Experiment 12 intake (no purpose, no queue, no send)
    |-- Experiment 29 number and date check (not its token verdict)
    |-- contiguous-span checker (Experiment 33's rule, not imported)
    v
JSON draft
    |
    v
Underwriter reviews every cited fact
    |
    v
Coverage, price, broker contact, and the underwriting system
    stay outside this agent
```

Experiment 35 is not imported. The smoke test in `eval/evaluate.py` is a separate scorer over labelled cases. It does not release a pass.

The diagram is `docs/architecture_diagram.png`, drawn by `docs/generate_diagram.py`.
