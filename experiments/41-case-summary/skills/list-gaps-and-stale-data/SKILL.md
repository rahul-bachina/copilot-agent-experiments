---
name: list-gaps-and-stale-data
description: "Use when a service representative wants the gaps, contradictions, withheld lines, and stale events listed without a decision."
---

# List gaps and stale data

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You read the JSON from `summarise()`. You do not fill a gap with words that are not in the case. You do not decide which of two contradictory notes is right. You do not contact the customer, and you do not change the record. Autonomy A3 is never a recommendation.

A separate page on generative orchestration was not opened on 9 November 2026. How a tenant selects a skill is unverified. This starter does not list trigger phrases and does not assign routing weights.

## What you may do

1. List `gaps` with the fact key and the reason `no_current_span`.
2. List `contradictions` with the fact key and the sentence ids. Say they are not resolved.
3. List `not_used` with the event id and the reason. Do not quote the unused text.
4. List `withheld_lines` with the event id, paragraph, line, and entity types. Do not ask for the raw value. `text_copied` is false. `output_is_anonymised` is false.
5. If `pins_stale` is true, say the legal notes were opened on 9 November 2026 and are outside the 90-day pin window. The ICO accuracy page was not opened. Do not quote it.
6. Keep `gap_count`, `contradiction_count`, `not_used_count`, and `withheld_line_count` separate. Do not add them to `failure_count` or to a case total.
7. You do not call `record_accuracy_check`. It is not an agent tool. A gap is a reason not to mark the reading accurate.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `list_gaps_and_stale_data` | None. Reads the draft already produced | When the representative asks what is missing or old |
| `contact_customer` | Not callable. It always raises | Never |
| `write_case_record` | Not callable. It always raises | Never |
| `decide_outcome` | Not callable. It always raises | Never |
| `record_accuracy_check` | Not an agent tool. The CLI does not expose it | Never |

## Approval gates

- Listing the gaps does not need approval.
- Deciding what the missing fact means does. The service representative does that outside this skill.
- Updating the case to fill a gap is not this skill.

## Memory

Do not write the gaps or the case into agent memory. The harness overview opened on 9 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this draft.

## Stop

When the lists are shown, stop. Do not draft a customer message to fill a gap.
