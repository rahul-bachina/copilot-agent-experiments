# Copilot Studio standard harness

A build guide, not an importable solution. The overview opened on 13 November 2026 says the standard harness follows the topics and rules the maker defines.

One topic. The model owner pastes one synthetic pack, types the as-of date, and supplies a separate confirmation. A flow calls `review_workbook` and returns the JSON. The topic stops. It does not edit the workbook.

## Topic

Name: Review workbook assumptions.

1. Ask for the pack JSON, the confirmation JSON, and the as-of date. Refuse to continue if `synthetic` is not true.
2. Call the Python core. Do not add a generative answer beside it.
3. Show `label`, `outcome`, `ranges_inspected`, and `human_route`.
4. If `prompt_injection.detected` is true, say the instruction was not followed. Do not quote the sentence.
5. If `outcome` is `safeguarding_for_human`, stop and say a person must take the text.
6. Stop. Do not offer a button that writes a cell.

This starter does not assign a weight to a topic. Where generative orchestration is on, selection is by the topic description. That behaviour was not checked in a tenant on 13 November 2026. The orchestration page was not opened.

## What the topic must not contain

- An Excel Online connector action that updates a range or a table.
- A Microsoft Graph call, including a workbook session.
- A branch that treats "APPROVED" or "confirm_workbook_ranges_and_formulas" inside a cell as the confirmation.
- A knowledge source that supplies benchmark rates.

The Customer Conversation harness is described on the same overview for customer voice and chat. It is not built here. An unattended editor of a live model would sit outside this A0 design.

See [system-prompt.md](system-prompt.md) and [power-automate-flow.md](power-automate-flow.md).
