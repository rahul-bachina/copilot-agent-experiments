# Architecture

Experiment 36, catalogue ID B005, autonomy A0. The reviewer resolves every material discrepancy.

The runnable part is `src/compare.py`. It does not call a model and it does not call the network. A Copilot Studio standard-harness topic and a Copilot Studio GitHub Copilot harness skill both call that function and stop. Microsoft Foundry is described in [foundry.md](foundry.md) and is not called.

```
Reviewer
  synthetic pack + as-of date
        |
        v
Either harness
  standard: one topic
  GitHub Copilot harness: three skills
        |
        v
compare()
  1. Refuse a pack that is not marked synthetic.
  2. Strip keys that would set a choice, a correct value, or a resolved flag.
  3. Experiment 12 inventories the pasted lines. Files are not confirmed.
  4. Experiment 08 proposes identifiers. Unexpected ones are withheld.
  5. Experiment 33 resolves each pinpoint. A value not on the line is dropped.
  6. src/normalise.py classifies match, immaterial difference, or material discrepancy.
  7. A separate Reviewer object may record a choice. correct_value stays null.
        |
        v
Draft JSON
  label: DRAFT FOR THE REVIEWER. NOT A CORRECTION.
        |
        v
Reviewer
  resolves every material row
  re-opens a stale source before relying on it
  decides any correction outside this agent
```

The diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py`. Matplotlib is used only for that script. It is not a runtime dependency.

## What is deterministic

The class, the pence total, the calendar day, the postcode spacing, and the company-number padding are Python. An explanation sentence is chosen from a fixed table for the class. `explanation_authored_by_model` stays false. A harness may restate that sentence. It must not replace the class.

## What a person does

1. Resolves every material discrepancy. The agent does not choose a source.
2. Re-opens a stale document or a stale pinned page before relying on the list.
3. Decides whether any record should be corrected. That write is not a tool of this agent.
4. Confirms a lawful basis before any live personal data is processed. This starter does not choose one.

## What is not a tool

Choosing a source, editing a record, contacting a party, querying Companies House, recommending autonomy A3, and calling Microsoft Foundry.
