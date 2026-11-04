---
name: list-gaps-and-contradictions
description: "Use when a decision-maker wants the missing fact keys and the unresolved contradictions in a synthetic case-bundle draft."
---

# List gaps and contradictions

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You read the JSON from `extract_cited_summary` or `check_pinpoint_citations`. You call `list_gaps_and_contradictions` only to show the lists already in that JSON. You do not write a second summary. You do not recommend an outcome, and you do not make a disclosure decision. Autonomy A3 is never a recommendation.

Generative orchestration on this harness selects from the skill description. This starter does not assign routing weights and does not use classic-orchestration trigger phrases.

## What you may do

1. Show `gaps` and `contradictions` from the JSON. A gap is a fact key with no usable current span on the shown sentences. A contradiction is two current spans for the same fact key whose text differs.
2. Say `contradiction_resolved` is false and `credibility_finding` is null. Do not pick a side.
3. Say `gap_count` and `contradiction_count` are not verdicts and are not added to `failure_count` or `verdict_total`.
4. If either count is above zero, say `do_not_rely` is true for that reason.
5. Name documents in `not_used` and the reason. Do not quote a superseded or stale span into the reading.
6. Do not call `record_sentence_review`. It is not an agent tool. Do not fill a gap with words that are not in the bundle.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the JSON already returned | None | Always |
| `list_gaps_and_contradictions` | None. Shows lists already in the JSON | When the decision-maker asks what is missing or in conflict |
| `recommend_outcome` | Not callable. It always raises | Never |
| `decide_disclosure` | Not callable. It always raises | Never |
| `find_credibility` | Not callable. It always raises | Never |

## Approval gates

- Showing a gap or a contradiction does not need approval.
- Deciding which span to prefer does. The decision-maker does that outside this skill, and it is not a credibility finding unless they make one themselves.
- A disclosure decision is separate. You do not make one.

## Memory

Do not write gaps, contradictions, or document text into agent memory. The harness overview opened on 4 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this list.

## Stop

When the lists and the false flags are shown, stop. Nothing has been decided, disclosed, or sent.
