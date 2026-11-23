# Architecture

The core is `src/register.py`. It is deterministic Python. It does not call a model and it does not open the network.

```
pinned extracts, register, controls, directory
        |
        v
propose_register(request, as_of)
        |
        +-- distress, grievance, disclosure, safeguarding --> route_to_human
        |
        +-- otherwise: one view per extract and per register row
                quote, applicability candidate, dates, controls, duplicates
                |
                v
        field diff, change hash, proposal hash
                |
                v
        human_approval stays null
                |
                v
stage_approved_change(proposal, approval)
        directory compliance owner
        decision "approve"
        both hashes recomputed
                |
                v
        one row in the in-memory staging store
        production_written false
        sent false
```

`as_of` is the date the question is about. A future extract stays not yet in force until that date. An ambiguous numeric date such as `01/02/2026` is not guessed.

Applicability values are candidates: `in_scope_candidate`, `out_of_scope_candidate`, `qualified_candidate`, `not_yet_in_force`, `superseded`, or `undecided`. `applicability_decided` stays false.

A proposed owner reference is the single compliance owner in the pinned directory, when there is exactly one. That is not an assignment. `accountability_assigned_by_agent` stays false.

The diagram is `architecture_diagram.png`, drawn by `generate_diagram.py`. Matplotlib is used only to draw it. It is not a test dependency.
