# Architecture

Experiment 68, catalogue L002, autonomy A0. One Python core, two Copilot Studio harnesses, and an optional Microsoft Foundry note. The compliance owner owns applicability. The agent does not decide that a change applies, change a policy, a control, or a record, or send anything.

The core reads pinned synthetic snapshots in `fixtures/publications.json` and the pinned register in `fixtures/policy_register.json`. It does not fetch a live regulator page. A caller-supplied register, directory, or pasted notice is compared with the pin and is not the authority.

Dates are read from the notice or computed from a formula the notice states. A missing date is `not stated`. An unreadable date is not replaced. Topic overlap is a candidate list. `applies` stays null. Negation and a following qualification keep a topic out of that list.

Experiment 04 supplies currency for a related FCA source id. Experiment 12 inventories the notice and does not confirm the file. Experiment 20 supplies a pinned quotation when the snapshot names complaints, housing, or energy. Experiment 08 masks UK identifiers. None of those calls decides applicability.

`record_owner_seen()` is the only approval step. It requires a pinned-directory compliance owner and the publication hash, the briefing hash, and the questions hash. `verify_seen()` rejects a quote that changes after that step.

```
Pinned notice and register
        |
        v
draft_briefing()  ---- Experiment 04 currency
        |             Experiment 12 intake
        |             Experiment 20 quotation
        |             Experiment 08 mask
        v
JSON briefing (applies is null)
        |
        v
Compliance owner sees the hashes
        |
        v
Nothing is changed and nothing is sent
```

The rendered diagram is `architecture_diagram.png` in this folder.
