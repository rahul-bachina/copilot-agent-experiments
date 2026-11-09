# Architecture

One case in. One JSON proposal out. The same inputs produce the same JSON.

```
Adviser or queue owner
        |
        v
Copilot Studio standard harness          Copilot Studio GitHub Copilot harness
(one topic, no skill)                    (four skills, same core)
        \                                /
         v                              v
              src/routing.py
              |-- Experiment 15 scan() --> Experiment 08 propose()
              |-- src/rules.py current / stale / unapproved
              |-- src/fairness.py characteristic instructions
              |-- src/clocks.py citations; Experiment 05 only for an Awaab illustration
              |-- human_approval left null
              v
        Proposal JSON
              |
              v
        record_review() on a separate object
              |
              +-- adviser confirms a proposed route (does not reroute)
              +-- adviser accepts a human queue (does not escalate)
              +-- queue owner records a rule approval (does not edit the file)
              v
        The person acts in their own system, outside the agent
```

There is no tool after the review. Reroute, close, escalate, send, and rule edit are not implemented. They raise `RoutingForbidden` if called directly.

The diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py` if the boxes change. Matplotlib is used only by that script. It is not a runtime dependency.

## Why the core is deterministic

A language model can explain a JSON document. It must not choose the queue. Vulnerability categories come from Experiment 15. Statutory dates, where this starter cites them, are either not calculated or are Experiment 05's result with officer approval forced off. Classification names follow Experiment 01. That model is not called.

## Human approval points

1. The adviser confirms a proposed service route. The case is not moved.
2. The adviser accepts a human queue for vulnerability, a statutory clock, fairness, an adjustment, a complaint, or an entitlement question. The case is not escalated or closed.
3. The queue owner approves a material rule change. The rule file is not edited. A protected characteristic cannot be the feature.
4. A stale rule is not proposed. Using the organisation's current rule is the owner's own step, outside this starter.
