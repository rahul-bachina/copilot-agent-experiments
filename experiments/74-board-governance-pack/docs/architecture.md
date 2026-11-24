# Architecture

The deterministic core is `src/pack.py`. Both Copilot Studio harnesses call it. Microsoft Foundry, if used, only narrates JSON the core has already produced.

```text
Pinned agenda, terms, papers, directory, register, minutes, ledger
        |
        v
assemble_pack  ---- caller agenda or terms are diffed and not applied
        |
        +--> Experiment 12 intake (files not confirmed)
        +--> Experiment 70 supplier mention (conflict_exists stays null)
        +--> Experiment 08 identifier count (not described as anonymised)
        |
        v
Draft agenda, pack index, flags, action log, content hash
        |
        +--> distress? record_route_seen by the named company secretary
        |
        v
record_secretary_approval (exact hash, directory role)
        |
        v
Synthetic staging row. Not circulated. Minutes not approved.
```

The prohibited functions `circulate`, `publish`, `file_pack`, `send`, `record_decision`, and `approve_minutes` raise. They are not tools.

Sponsor approval is a row in `fixtures/approvals.json` bound to the paper hash. The secretary's approval is a separate object bound to the pack hash. A sentence in a paper is neither.

The diagram is [architecture_diagram.png](architecture_diagram.png).
