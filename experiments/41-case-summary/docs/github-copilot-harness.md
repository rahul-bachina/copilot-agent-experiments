# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness: an authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 9 November 2026 says the harness can take a goal, break it into steps, call tools, and supports skills and memory. It runs each task in a sandbox governed by Copilot Studio. Agents and workflows on this harness use Copilot Credits. The linked billing page was not opened. No price is copied. The overview did not mark the harness as preview.

This starter uses the harness only to explain one JSON draft. It does not create files. It does not write the case into memory. The overview says the harness supports memory. An administrator control to turn memory off was not on that page. Do not use memory for this draft.

## Skills

Generative orchestration, if the tenant uses it, was not documented from a page opened on 9 November 2026. How a description selects a skill is unverified. This starter does not list trigger phrases and does not assign routing weights.

| Skill | Use when |
|---|---|
| `extract-cited-case-summary` | A service representative wants an extractive reading of one synthetic case, with a pinpoint on every sentence. |
| `check-pinpoint-citations` | A service representative wants a proposed sentence checked against the event, paragraph, and line it cites. |
| `list-gaps-and-stale-data` | A service representative wants the gaps, contradictions, withheld lines, and stale events listed, without a decision. |

Each skill calls `summarise()` or reads the JSON it already returned. None of them calls `record_accuracy_check`, `contact_customer`, `write_case_record`, `close_complaint`, `offer_redress`, `decide_outcome`, or `send_external`.

## Approval

Producing the draft does not need an approval click. Checking accuracy does. The service representative does that outside the skill. Contacting the customer and changing the record are not skills. They are not available after the representative has checked the draft either.

## Stop

When the JSON is shown, stop. The representative has not checked the sentences, and the customer has not been contacted.
