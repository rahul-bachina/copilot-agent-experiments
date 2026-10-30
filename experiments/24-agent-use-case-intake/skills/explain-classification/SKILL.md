---
name: explain-classification
description: >
  Explain an intake classification that is already on screen, using only
  fields in that JSON. Use when a governance team asks why a suggested
  autonomy, a DPIA flag, an ATRS flag, or a stale flag is what it is.
  Do not re-run the classifier, approve the use case, or fill a gap.
---

# Explain a classification

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview, opened 30 October 2026, says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio.

This skill reads a draft that `classify()` already produced. It does not call `classify()` again, and it does not call Experiments 14, 19, or 03 again. It does not approve the use case.

The `name` and `description` above are the skill fields Microsoft describes on the harness overview as skills. The exact upload schema was not opened on 30 October 2026. The approval rules below are the manifest's rules.

## When to use this skill

Use it when the governance team asks what a code means, which recorded field produced it, or why a field is still a gap. If there is no draft yet, use `draft-classification` instead.

## What you may say

Tie every sentence to a field that is already in the JSON.

- `suggested_autonomy` and `autonomy_wanted`. A difference is the draft. You do not resolve it. The suggested level is A0, A1, or A2. `a3_recommended` is false. `a3_out_of_scope` means the team asked for A3 and this catalogue does not suggest it.
- `risk_tier` and the rules named beside it. Say the tier is a queue heuristic. It is not an Article 35 finding.
- `dpia_likely_needed` and the Experiment 19 screen result. `dpia_required` is null on every code. A recorded no on every screen answer is not a finding that Article 35(1) does not apply.
- `atrs_likely_needed` and its basis. `recommended_for_the_wider_public_sector` is the guidance's recommendation. It is not a finding that the body is in the mandatory organisation list. `tool_tests_recorded_as_not_met` is not a clearance. Mandatory scope stays undecided.
- `resembles` and `candidates`. Two matches are a list, not a ranking.
- `sources_stale` and `prompt_injection.followed` (must be false).
- `approved`, `provisioned`, and `governance_decision`. They stay false or null. You do not change them.

## What you must not do

- Invent a yes where the JSON says unknown or null.
- Fill a gap from the original narrative. If the narrative is not in the JSON, do not fetch it.
- Recompute autonomy, the risk tier, the DPIA screen, or the ATRS line.
- Suggest autonomy A3.
- Approve or change the intake classification. Approver: Governance team. You do not record that decision.
- Say a DPIA is required, or that an ATRS record has been submitted.
- Provision an agent, send a message, or write a production record.
- Add a URL that is not in the JSON.
- Store the proposal or the classification in memory. The harness supports memory. Do not use it for this explanation.

## Approval gates

| Act | Approval |
|---|---|
| Explain the draft | Not required |
| Approve or change the intake classification | Mandatory. Approver: Governance team. This skill does not record it. |
| Treat a DPIA indication as a reason to start a DPIA | Mandatory. Approver: Privacy officer. |
| Treat an ATRS indication as a reason to draft a record | Mandatory. Approver: Governance team. |
| Re-open a pinned page after it is marked stale | Mandatory. Approver: Governance team. |

## Stop

When the explanation is given, stop. Say that nothing has been approved or provisioned, and that the governance team still has to approve or change the classification.
