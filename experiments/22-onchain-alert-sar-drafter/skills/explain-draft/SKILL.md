---
name: explain-draft
description: >
  Explain a draft that investigate() has already returned for one synthetic
  on-chain alert. Use when the analyst asks what a flag, a timeline row, or
  a quoted statutory line means. Do not recompute the draft, file, or write
  anything a customer could read.
---

# Explain a draft that is already on screen

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview, opened 29 October 2026, says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio.

This skill is for an analyst who already has the JSON. It is not a customer-facing bot. The boundaries below are the ones in `agent-manifest.yaml`. This skill does not add an approval step and it does not remove one.

The `name` and `description` above are the skill fields Microsoft describes on the harness overview as skills. The exact upload schema was not opened on 29 October 2026. The approval rules below are the manifest's rules. They are not a Microsoft schema.

## When to use this skill

Use it to explain `sources_stale`, `alert_context_stale`, a future hop, an omitted identifier, a Travel Rule category, a KYC missing-item id, or why the narrative quotes section 330(2) without deciding it. Producing the JSON is the other skill.

Do not call `investigate()` again unless the analyst asks for a new run. Do not invent a hop, a price, or a glossary code that is not in the JSON.

## What to say

- `mlro_decision` is null. The nominated officer has not decided, and this agent cannot record the decision. `record_mlro_decision` always raises.
- `sar_filed` is false. The draft is labelled for the nominated officer. It is not a disclosure and it has not been submitted. `file_with_nca` always raises.
- `customer_facing.text` is null. Nothing in the draft is for the customer. Section 333A was opened. Sections 333B, 333C, and 333D were not. Do not draft a holding reply. `contact_customer` always raises.
- A row with `future` true was not treated as having happened.
- An omitted identifier was not a `SYNTH-ADDR-` or `SYNTH-TX-` token. The raw value is not in the JSON. Do not reconstruct it.
- `identifier_gateway.output_is_anonymised` is false. Experiment 08 proposed redactions. The note is not anonymised.
- `marc_sentence_applied` is false. The MARC sentence on the 30 June 2026 overview is not this AML alert.
- `glossary_codes_assigned` is false. The glossary was not opened. `assign_glossary_code` always raises.

## Approval gates

The same gates as `investigate-alert`. Explaining the draft does not decide the section 330 or section 331 test, does not file, and does not clear a stale flag.

| Act | Approval |
|---|---|
| Explain the JSON that is already on screen | Not required |
| Decide whether the section 330 or section 331 test is met | Mandatory. Approver: Nominated officer. |
| File or not file | Mandatory. Approver: Nominated officer. `file_with_nca` always raises. |
| Request a defence | Mandatory. Approver: Nominated officer. `request_daml` always raises. |
| Rely on a stale source, a stale alert, or a future-dated event | Mandatory. Approver: Nominated officer. |
| Use any customer-facing wording | Mandatory. Approver: Nominated officer. `contact_customer` always raises. |

## Sandbox file

You may write `draft-investigation-note.json` only as a copy of the tool JSON the analyst already has. Do not add a sentence. Do not name a file `filed`.
