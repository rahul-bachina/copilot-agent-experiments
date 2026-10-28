---
name: explain-screening
description: >
  Explain a DPIA draft that is already on screen, using only fields in that
  JSON. Use when a privacy officer asks why a screen result, a stale flag,
  or a consultation flag is what it is. Do not re-run the screen, approve
  the assessment, or fill a gap.
---

# Explain a screening result

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview, opened 28 October 2026, says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio.

This skill reads a draft that `assess()` already produced. It does not call `assess()` again, and it does not call Experiment 08 again. It does not approve the assessment.

The `name` and `description` above are the skill fields Microsoft describes on the harness overview as skills. The exact upload schema was not opened on 28 October 2026. The approval rules below are the manifest's rules.

## When to use this skill

Use it when the privacy officer asks what a code means, which recorded answer produced it, or why a field is still a gap. If there is no draft yet, use `draft-dpia` instead.

## What you may say

Tie every sentence to a field that is already in the JSON.

- `screening.screen_result` and `screening.reading`. `dpia_required` is null on every code, including `recorded_answers_do_not_indicate`.
- `article_35_3_recorded` means a recorded yes on Article 35(3)(a), (b), or (c). A controller view of "no" does not clear it.
- `ico_list_recorded` means a standalone ICO type is yes, or a combination type is yes and another European criterion is also yes. Innovative technology does not count its own twin as that other criterion.
- `ico_list_combination_not_shown` means a combination type is yes and the other criterion is not shown.
- `wp248_two_factors_recorded` means two or more of the nine criteria on the ICO when-page are yes, and no stronger code applied. The ICO page says two factors usually indicate a DPIA and that this is not a strict rule. WP248 itself was not opened.
- `exception_not_decided` means the genetic-data direct-care exception was claimed. The tool does not apply it.
- `automated_decision_screen.screen_result`. `restriction_may_apply` is not a finding that processing is unlawful. `safeguards_recorded_not_a_clearance` is not a clearance. `saving_provision_may_apply` means the tool has not interpreted S.I. 2026/82 regulation 5.
- `prior_consultation.code`. `high_residual_recorded` is not a decision that Article 36(1) is met. The statutory addressee in the revised text is the Commission. The ICO page still says to consult the ICO. The draft does not reconcile those sentences.
- `sources_stale`, `prompt_injection.followed` (must be false), and `output_is_anonymised` (must be false).
- Fields whose `prefilled_from` is set. Say they were copied, and that a person has not yet treated them as the team's answer.

## What you must not do

- Invent a yes where the JSON says unknown.
- Fill a gap. The gap text is "Not recorded in the project brief. This draft does not fill the gap."
- Set `approved`, `signed_off`, `residual_risk_accepted`, or `dpia_required`.
- Call `record_external_attestation`. The agent must not call it.
- Call `approve_assessment`, `reject_assessment`, `sign_off_assessment`, `accept_residual_risk`, `send_prior_consultation`, or `write_production_record`. Each of those raises `AssessmentForbidden`.
- Describe the text as anonymised.

## Approval gates

Explaining the JSON does not need a separate approval. Relying on it does.

| Act | Approval |
|---|---|
| Read the explanation | Not required |
| Approve the assessment | Mandatory. Approver: Privacy officer. Not this skill. |
| Accept residual risk | Mandatory. Approver: Project owner. Not this skill. |
| Decide any Article 36 consultation | Mandatory. Approver: Privacy officer. Not this skill. |
| Rely on stale sources | Mandatory. Approver: Privacy officer. |
| Treat pre-filled text as the team's own answer | Mandatory. Approver: Project owner. |
