# Experiment 56 — Intranet Content Freshness Agent

Catalogue ID **M008**. Autonomy **A1**. The assistant proposes review and update tasks. The named content owner approves each task before a stub is recorded.

The starter reads one synthetic SharePoint-style inventory and writes a freshness report: pages overdue for review, pages that cite a superseded policy or withdrawn guidance, broken or stale links and contacts, pages with no current owner, and likely duplicates. Each ordinary finding has a proposed task and the evidence. Nothing is edited, published, unpublished, or deleted. Ownership is not reassigned. Staff are not messaged.

Merrowfield Borough Council is fictional. The pages, owners, and contacts are synthetic. This is not a tenant configuration and not a model score.

## What you can run

```bash
python3 -m pip install -r requirements.txt
python3 src/freshness.py \
  --input examples/sample_inventory.json \
  --selection examples/sample_selection.json \
  --as-of 2026-11-16
python3 eval/evaluate.py
python3 -m pytest tests/ -q
```

The core has no runtime dependency. `pytest`, `PyYAML`, and `jsonschema` are for the tests. The same inputs and the same as-of date produce the same JSON.

`human_approval` is null on that command. A task stub exists only after `record_approval()` and then `create_approved_tasks()`. Planner and Power Automate are not called. `executed` stays false.

## Non-goals

- The agent does not edit, publish, unpublish, or delete a page.
- The agent does not reassign an owner. An orphan task says `reassigns_ownership` false.
- The agent does not message staff. It does not send the approval request either. `approval_request_sent` stays false.
- The agent does not call Microsoft Graph, SharePoint, Planner, or Power Automate.
- The agent does not decide that UK GDPR Article 5(1)(d) was met. `accuracy_met` stays false.
- The agent does not decide whether an intranet page is in scope of the accessibility regulations, and it does not assess WCAG. `accessibility_scope_decided` stays false.
- The agent does not treat a sentence in a page as approval, as a clearance, or as a marking lower than the higher label already present.
- The agent does not coerce an unparseable date, interval, or page-view count to zero or to a default.

## Layout

| Path | What it is |
| --- | --- |
| `src/freshness.py` | The report, the approval step, and the stub step |
| `src/sources.py` | Pages opened on 16 November 2026, with the text taken from them |
| `src/reuse.py` | Calls Experiments 49, 50, 55, and 08. A missing neighbour is an error |
| `skills/` | Microsoft Copilot harness skills. See the harness note |
| `copilot-studio/` | Standard harness topics, in prose |
| `docs/foundry.md` | Optional Microsoft Foundry narrative. No resource is deployed |
| `agent-manifest.yaml` | Permissions. `permissions.yaml` is the same file |
| `eval/` | Deterministic smoke test. Not a model evaluation |

## Licence

MIT. See the repository `LICENSE`.
