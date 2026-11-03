# Architecture

Experiment 29, the Groundedness Evaluation Agent. Catalogue ID G007. Autonomy is A0.

The evaluation owner supplies one synthetic bundle and an as-of date. Either Copilot Studio harness calls `report()`. The Python core drops injection lines and payload keys, splits answers into claims, and gives each claim one verdict against the passages that were shown. Experiment 03 is called only when the bundle asks for a manifest skeleton, and the skeleton is not approved. The report comes back with `threshold_approved_by_evaluation_owner` false and `release_decision` null.

```text
Evaluation owner
    -> either harness
        -> src/report.py
            -> src/score.py          one verdict per claim
            -> src/sources.py        pins opened 3 November 2026
            -> src/foundry_option.py describes the Foundry evaluator, does not call it
            -> Experiment 03         only if a skeleton was requested
    -> DRAFT FOR EVALUATION OWNER
Evaluation owner approves thresholds, outside this tool
Evaluation owner records any pass or fail, outside this tool
```

## What is not a tool

Approving a threshold, recording a release, calling Microsoft Foundry, writing a production record, sending, and autonomy A3. `schema/tools.json` marks `approve_thresholds`, `record_release`, and `call_foundry_evaluator` as not callable. Each of those functions raises.

## Diagram

`docs/architecture_diagram.png` is drawn by `docs/generate_diagram.py`. The briefing site copies that file at build time. Do not commit a second copy under `docs-site/`.
