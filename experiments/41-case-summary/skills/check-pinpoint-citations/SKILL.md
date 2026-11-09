---
name: check-pinpoint-citations
description: "Use when a service representative wants a proposed sentence checked against the event, paragraph, and line it cites."
---

# Check a pinpoint citation

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You call `check_pinpoint_citations`, which runs `summarise()` with the representative's proposed sentences beside the synthetic case. You do not rewrite a failed sentence into a paraphrase that you then pass off as supported. You do not contact the customer, and you do not change the record. Autonomy A3 is never a recommendation.

A separate page on generative orchestration was not opened on 9 November 2026. How a tenant selects a skill is unverified. This starter does not list trigger phrases and does not assign routing weights.

## What you may do

1. Pass the case, the as-of date, and the proposed sentences. Each sentence needs an event id, a paragraph, a line start, and a line end, or the checker will fail it.
2. Show one verdict per sentence, then `other_failures`. Do not add `other_failures` to `failure_count`.
3. If the verdict is `identifier_withheld`, show the placeholder. Do not restore the original words.
4. If the verdict is `span_does_not_support`, say the cited lines do not contain the sentence. Do not invent a closer sentence.
5. State that a passed sentence is still not a customer contact and not a record change. `accuracy_checked` stays false. You do not call `record_accuracy_check`. It is not an agent tool.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| `check_pinpoint_citations` | None. Reads the case and the proposed sentences | When a sentence needs a verdict |
| `contact_customer` | Not callable. It always raises | Never |
| `write_case_record` | Not callable. It always raises | Never |
| `accept_summary` | Not callable. It always raises | Never |
| `record_accuracy_check` | Not an agent tool. The CLI does not expose it | Never |

## Approval gates

- Running the check does not need approval.
- Relying on a supported sentence does. The service representative checks it outside this skill.
- Contacting the customer or changing the record does not become allowed because a sentence was supported.

## Memory

Do not write the case or the proposed sentences into agent memory. The harness overview opened on 9 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this draft.

## Stop

When the verdicts are shown, stop. Do not send the sentences to the customer.
