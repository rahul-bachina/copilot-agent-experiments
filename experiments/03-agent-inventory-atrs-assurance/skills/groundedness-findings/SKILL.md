---
name: groundedness-findings
description: Check that ATRS answers and playbook quotes were copied from the inventory, and flag a stale review date. Catalogue item G007, folded into G010. The evaluation owner approves thresholds. This skill does not.
catalogue_id: G007
parent: G010
harness: copilot-studio-github-copilot
autonomy: A0
metadata:
  version: "0.1.0"
  status: draft
  approved: false
tools:
  - name: evaluate_groundedness
    entrypoint: src/evaluations.py
    effect: read
    writes_production: false
    sends: false
approval_gate: >
  The catalogue checkpoint is an evaluation owner approving thresholds.
  The 180-day staleness threshold in src/catalogue.py is a draft.
  This skill must not present it as an approved threshold.
---

# Groundedness findings

This is the G007 evaluation inside the assurance pack. Autonomy in the catalogue is A0.

After a pack is drafted, report:

- `unsupported_claim_count`. A count of zero means the draft copied inventory text or used the gap sentence. It does not mean the inventory is true.
- `stale`, `age_days`, and `stale_reason`.
- `threshold_days` (180) and `threshold_approved_by_evaluation_owner` (false).
- `groundedness_clearance` (false).

Do not lower the threshold because a record would otherwise look stale. Do not tell the person the record is current when `stale` is true. Do not write the finding back onto the inventory as an approval.

If the person wants a different threshold, say an evaluation owner has to set it, and that this skill will not.
