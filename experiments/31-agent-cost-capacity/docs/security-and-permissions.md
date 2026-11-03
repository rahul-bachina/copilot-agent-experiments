# Security and permissions

Agent Cost and Capacity Agent, Experiment 31. Catalogue ID G009.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a billing audit.

## Purpose

The agent reads one synthetic usage file and one rate card, and returns a draft of cost, unit cost, a forecast, headroom, and anomaly flags. Autonomy is A0. It has no action to take on the draft. The FinOps owner validates rates and the forecast. An administrator, outside this agent, is the only person who might change a quota, a budget, or a subscription. This agent does not.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Validate rates. `rates_validated` stays false.
- Validate the forecast. `forecast_validated` stays false.
- Change a quota, a budget, or a subscription.
- Purchase Copilot Credits or start a paid meter.
- Use a price that is not a string on the rate-card file. There is no built-in rate table.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This report stays at A0.
- Write a production record or send a message.
- Read an admin centre, Azure Cost Management, or a live tenant.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. `schema/tools.json` marks `record_rate_validation`, `record_forecast_validation`, `change_quota`, `change_budget`, and `change_subscription` as not callable. Tests in `tests/test_injection.py` and `tests/test_prohibited.py` check that fixture text and command flags do not become a validation or a quota change.

## Data

**Read, in this starter.** The telemetry file and the rate card for that run. The as-of date and the stale threshold. The static source list.

**Not read.** An admin centre, a billing subscription, a mailbox, a Teams chat, a production agent, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane.

The samples in this repository are synthetic. Northfen Borough Council is fictional. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms an Article 6 basis before any live processing. No Article 9 condition is asserted. Live usage exports are outside this starter.

The Python starter does not persist the files. A note that matches an instruction pattern is not copied into the JSON.

## Prompt injection and stale data

The report is itself a reader of untrusted notes. The scanner records a line that tells it to ignore instructions, set a price, validate the rates or the forecast, or change a quota, a budget, or a subscription. A sentence that already refuses the action, including "do not" and "must not", is not treated as an instruction. Payload keys that try to set the control flags are stripped and are not echoed. `followed` stays false.

A paraphrase can be missed. Residual risk R2 in the manifest is Low for the sentences the tests name. A missed paraphrase does not grant a tool the agent does not have.

The stale-data test compares the rate card `effective_date`, and `last_verified` on the Microsoft pages (3 November 2026), with the as-of date. Older than the threshold, default 90 days, is stale. The catalogue-boundary row is not a Microsoft page and is not stale-tested. The runner does not download the page and does not rewrite the review date. When a pin or the card is stale, `do_not_rely` is true. The draft is still produced. It is still not a validation. A card dated after the as-of date is not applied.

## Human approval

Autonomy A0 means this report cannot change a limit even after a person agrees. The person still has to make the change, somewhere else, with their own authority.

| Decision | Who |
|---|---|
| Validate the rates | FinOps owner |
| Validate the forecast | FinOps owner |
| Re-open a stale rate card or a stale page before relying on a citation | FinOps owner |
| Change a quota, a budget, or a subscription | An administrator, outside this agent |
| Confirm an Article 6 basis before any live export is processed | Data protection officer |
| Deploy or publish | Outside this agent |

Producing the draft and printing the sources table do not need a separate approval.

Assumption id A3 in the manifest is an assumption about disabled high-risk actions. It is not autonomy level A3.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 3 November 2026 for this experiment. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Power Platform admin centre capacity controls | Not called | The cost-management page was opened on 3 November 2026. It describes environment allocations, agent monthly limits, and pay-as-you-go. Azure budgets and alerts notify and do not stop Copilot Studio consumption. An agent limit can stop usage when that control is turned on. This starter does not turn it on. |
| Microsoft Foundry prompt shields | Not called | Unverified. The page was not opened for this experiment. The local scan is not a shield result. |
| Microsoft Entra Agent ID | Not configured | Unverified. Not opened for this experiment. |
| Conditional Access | Not configured | Unverified. Not opened for this experiment. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this experiment. A later connector that can send, write, or change a subscription would need a policy the organisation writes. |
| Key Vault | Not provisioned | Unverified. Not opened. The report has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of any later report is the organisation's. |
| Application Insights | Not configured | Unverified. Not opened. This starter writes no log. |

## Review

Last reviewed 3 November 2026. Next review 3 May 2027, and sooner if a pinned page is re-opened and has changed.
