# Architecture

The runnable core is `src/inventory.py`. The same inputs and the same as-of date produce the same JSON. Copilot Studio, on either harness, calls that core. It does not reimplement the phrase checks, the negation rule, the markings, or the hash binding.

```
Employee-supplied evidence + example framework + directory + Article 13 record
        |
        v
propose_inventory()
        |
        +-- Experiment 08 propose() on each cited sentence
        |
        +-- optional, later: Experiment 61 only after the employee confirms a skill
        |
        +-- optional: Experiment 62 only from stated experience, not from inferred skills
        |
        v
JSON proposals, each state "needs employee confirmation"
        |
        v
record_employee_decision()  -- employee, inventory hash, skill hash
        |
        v
record_hr_validation()      -- HR, same hash or the correction hash
        |
        v
JSON only. No HR write. No performance rating.
```

A distress cue, an objection, or a request to use the inventory for pay, promotion, redundancy, or discipline stops before proposals. `record_route_seen()` can record that HR has seen the reason code. It does not decide the case.

The team view counts distinct people only when the cell and its complement are both at or above the threshold. It does not list references. Suppression is not anonymisation.

The diagram is `docs/architecture_diagram.png`, drawn by `docs/generate_diagram.py`.
