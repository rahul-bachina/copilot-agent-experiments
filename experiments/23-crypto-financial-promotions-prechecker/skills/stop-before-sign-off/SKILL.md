---
name: stop-before-sign-off
description: >
  Explain a checklist that precheck() has already returned for one synthetic
  cryptoasset promotion. Use when the reviewer asks what a row means. Do not
  recompute the checklist, approve the promotion, or publish it.
---

# Stop before sign-off

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview, opened 30 October 2026, says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio.

This skill is for a reviewer who already has the JSON. It is not a customer-facing bot. The boundaries below are the ones in `agent-manifest.yaml`. This skill does not add an approval step and it does not remove one.

The `name` and `description` above are the skill fields Microsoft describes for an uploaded skill. The approval rules below are the manifest's rules. They are not a Microsoft schema.

## When to use this skill

Use it to explain `sources_stale`, a checklist status, a citation, or why `s21_approver_decision` is null. Producing the JSON is the other skill.

Do not call `precheck()` again unless the reviewer asks for a new run. Do not invent a rule that is not in the JSON. Do not open a page this starter did not open.

## What to say

- `s21_approver_decision` is null. The section 21 approver has not signed off, and this agent cannot record the decision. `approve_promotion` always raises.
- `promotion_approved`, `published`, and `compliance_opinion` are false. The label is a draft checklist. It is not an approval and it is not a compliance opinion. `publish_promotion` and `give_compliance_opinion` always raise.
- `rewrite_drafted` is false. Do not draft a replacement sentence.
- A row status is an observation about a phrase. `compliance_finding` is false. `phrase_present` is not a pass. `phrase_not_found` is not a breach.
- `sources_stale` true means a person re-opens the page before anyone relies on the row.
- `identifier_gateway.output_is_anonymised` is false. Experiment 08 proposed redactions. The text is not anonymised.
- Section 55NA, COBS 4 Annex 1R, COBS 4.12A.36R, COBS 4.12A.38R, COBS 10, and COBS 10A were not opened. Do not describe them as checked.
- The marketing-page gateway sentence and section 21(2A) are both recorded. Do not choose between them.

## Approval gates

The same gates as `build-promotion-checklist`. Explaining the checklist does not sign the promotion off, does not publish it, and does not clear a stale flag.

| Act | Approval |
|---|---|
| Explain a row that is already on screen | Not required |
| Sign off, publish, or give an opinion | Mandatory. Approver: section 21 approver. You do not do it. |

## Sandbox file

Do not write a second file. If `draft-promotion-checklist.json` is already in the sandbox, leave it unchanged.
