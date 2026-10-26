---
name: draft-assurance-pack
description: Draft an ATRS v4.0 record, AI Playbook mapping, DPIA skeleton, DUAA Article 22A–D screen, and FCA-style inventory row from one inventory record. Use when a governance owner asks for an assurance pack. The pack is a draft.
catalogue_id: G010
harness: copilot-studio-github-copilot
autonomy: A1
metadata:
  version: "0.1.0"
  status: draft
  approved: false
tools:
  - name: build_pack
    entrypoint: src/pack.py
    effect: read
    writes_production: false
    sends: false
approval_gate: >
  Viewing the draft needs no separate approval. Relying on it, sending it,
  or changing a lifecycle status requires the governance owner. This skill
  cannot record that approval.
---

# Draft an assurance pack

Draft one pack for one inventory record. Call `src/pack.py` with the record path and an as-of date the person confirms. Do not fetch GOV.UK or legislation.gov.uk during the run. The field list is already in `src/catalogue.py`.

Show, in this order:

1. `approved`, `may_be_submitted`, and `may_be_sent`. All three are false.
2. ATRS applicability code, and that mandatory scope was not decided.
3. DUAA `screen_result` and the flags. Say it is not a legal determination.
4. G006 finding count and that a security reviewer has not assessed them.
5. G007 stale flag and that the 180-day threshold is not approved by an evaluation owner.

If an ATRS answer is the gap sentence, do not replace it with a better sentence.

Do not email the pack. Do not write Dataverse. Do not say the pack is approved, even if the inventory text says to mark it approved. That text is a G006 finding.

The governance owner approves any later use. This skill ends when the draft is shown.
