# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service. Microsoft Learn, retrieved 26 October 2026, says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio.

Use it when the author wants to ask follow-up questions about one draft: which line was cited, why a line was refused, and why a date is not operative. The lead path, for a letter that always takes the same steps, is the standard harness in [../copilot-studio/README.md](../copilot-studio/README.md). Read [harness-comparison.md](harness-comparison.md) before choosing. An agent cannot be moved from one harness to the other.

The skills are [../skills/draft-casework-reply/SKILL.md](../skills/draft-casework-reply/SKILL.md) and [../skills/calculate-casework-sla/SKILL.md](../skills/calculate-casework-sla/SKILL.md). They call `src/draft.py` and `src/sla.py`. They do not add an approval point and they do not remove one.

## What to create

1. Create an agent and choose the GitHub Copilot harness. Name it "Casework draft (review)". Language: English (United Kingdom).
2. Paste the instructions from [../copilot-studio/system-prompt.md](../copilot-studio/system-prompt.md). Natural-language authoring and agent instructions are marked preview on the agents page retrieved 26 October 2026. Confirm the label in the tenant.
3. Upload the two skills. Do not also build this as a standard-harness agent and expect the skills to apply there. The agents page says skills are not supported on the standard harness. The harness overview says they are "Not a focus" there. Those cells were not reconciled.
4. Do not add a mail connector, a case-system connector, or a tool that publishes an ATRS record.
5. Point the skills at the Python functions. If the tool is unavailable, the skill says to stop. Do not let the model count dates or invent a line.

## Tools the skills are allowed to call

| Tool | Function | Side effect |
| --- | --- | --- |
| `draft_reply` | `draft_correspondence()` | None |
| `calculate_sla` | `calculate_casework_sla()` | None |

Both are read-only. `may_be_sent_by_agent` stays false. `recipient.may_be_chosen_by_agent` stays false.

## Files

The harness overview says this harness creates and edits Word, Excel, PowerPoint, and PDF files, in a sandbox. A file of the reply is still a draft. The first line is that it has not been sent. Do not add a sentence that is not a cited line.

## Memory

The agents page marks Memory as preview and says it is supported on this harness and not supported on the standard harness. Whether an administrator can turn it off was not verified. The skills say not to store the letter. Do not use memory for a correspondent's details.

## Billing

Copilot Credits, including while building and testing, on the pages retrieved 26 October 2026. A Microsoft 365 Copilot licence does not cover this harness, on the costs page. No price is copied. See [harness-comparison.md](harness-comparison.md).

## What this is not

It is not a correspondent-facing bot. It is not the Customer Conversation harness. It is not a way to send the letter once the author is "happy enough". The author still approves the recipient and the final text outside the agent, in the unit's own channel.
