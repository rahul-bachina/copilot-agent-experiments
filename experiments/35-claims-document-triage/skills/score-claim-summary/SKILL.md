---
name: score-claim-summary
description: Use when a claims handler or an evaluation owner wants a supplied claim summary scored for faithfulness, completeness, and unsupported coverage statements.
---

# Score a supplied summary

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `score_supplied_summary`. You do not reimplement Experiment 29. You do not approve a threshold. You do not call Microsoft Foundry. Autonomy A3 is never a recommendation. Do not use it.

## What you may do

1. Pass the pack, the candidate sentences, and the as-of date. Do not pass `--approve-thresholds`, `--decline-claim`, or a pass or fail release.
2. Show the label `DRAFT EVALUATION SCORECARD` before the three results.
3. Show faithfulness (Experiment 29 verdicts), completeness (the closed checklist), and unsupported coverage (the closed phrase list) as three results. Do not add them together. `stale_claim_count` is separate from the verdict total.
4. If `human_escalation_required` is true, say a person reviews the summary. `escalation_does_not_decline_the_claim` must be true. `claim_declined` must be false.
5. State `threshold_approved_by_evaluation_owner` is false, `llm_as_judge` is false, and `foundry_evaluator_called` is false.
6. Say this checker is not the LLM-as-a-judge in FCA case study K. Conciseness and adequacy of reasoning are not scored.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `score_supplied_summary` | None. Returns a scorecard | When a supplied summary needs a score |
| `approve_thresholds` | Always raises | Never |
| `call_foundry_evaluator` | Always raises | Never |
| `decline_from_score` | Always raises | Never |

## Approval gates

- Producing the scorecard does not need approval.
- Approving thresholds does. The evaluation owner does that outside this skill.
- The handler still reviews a miss. You do not decline the claim.

## Memory

Do not write the summary or the score into agent memory.

## Stop

When the scorecard is shown, stop.
