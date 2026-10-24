# Copilot Studio standard harness

A build guide, not a solution you can import. This is the lead intake for Experiment 05. The officer-side case review and the reasonable-endeavours record are the GitHub Copilot harness in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Both call the same Python clock.

The default is an officer pasting one report. Publishing a channel a tenant can open is a deployment decision. This repository does not publish one. A tenant-facing reply that states a deadline, a category, or a safety instruction is a send, and this agent does not send.

## What to create

1. In Copilot Studio, create an agent on the **standard harness**. Name it "Hazard triage (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, an SMS connector, a housing-system connector, or a Dataverse "create row" action. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs `src/statutory_clock.py` and returns JSON. The contract is below and in [../schema/clock_tool.schema.json](../schema/clock_tool.schema.json).
5. Turn off any generative action that can call every connector in the environment. Classic topics, with the clock as the only action, are easier to review.

The standard harness follows the topics you define. Microsoft Learn describes it as the harness for rule-based agents and structured conversations ([harnesses overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026). That is why it is the intake.

## Clock action

Inputs come from the officer or from a form. The model must not fill them from the report text.

| Input | Required | Notes |
| --- | --- | --- |
| `aware_at` | Yes | ISO-8601 with a timezone. Europe/London. A date with no time is refused. |
| `category` | Yes | `emergency`, `significant`, `not_in_scope`, or `uncertain`. |
| `hazard_family` | Yes | A family id from `statutory_clock.HAZARD_FAMILIES`. |
| `social_home_in_england` | No | Default false. The officer sets it. |
| `officer_approved_category` | No | Default false. The model must not set it. |
| `officer_approved_clock` | No | Default false. The model must not set it. |
| `investigation_completed_on` | No | `YYYY-MM-DD`. Omit it and the summary and safety dates are not calculated. |
| `part_6_complied` | No | Boolean. Only the officer sets it. |
| `caller_asserts_phase_2_instrument_in_force` | No | Default false. Do not set it while the amendment is a draft. |

Output: the JSON from `calculate_statutory_clock`. The topic displays `operative`, `in_force`, `phases_not_in_force`, and the deadline list. It does not recompute them.

How to host the function:

- A small internal API or an Azure Function that imports `statutory_clock.py`, called by a Power Automate HTTP action with a locked-down identity. See [power-automate-flow.md](power-automate-flow.md).
- Not a Power Automate expression that adds ten working days on the flow's own calendar. That calendar will not encode regulation 2, the 24-hour emergency period, or the Phase 2 flag. One implementation of the count is enough.

The flow returns JSON to the topic. It does not create a row and it does not send mail.

## Topics

**Capture.** Triggers: "log a hazard report", "tenant report". Ask for the text and the awareness time. If this topic is ever shown to a tenant, the only reply is the fixed line: "An officer will read this report. This chat has not set a repair time and has not sent a letter." Do not call the clock on the tenant's behalf and do not state 24 hours, ten working days, or any other period.

**Officer triage.** Triggers: "triage this report", "what is the clock". Ask the officer to confirm the social home, the category, and the hazard family. Call the clock only after `aware_at` is present. Pass the approval flags as false until the officer has ticked them in the form. Show injection and stale flags before the draft. Show Phase 2 and Phase 3 as not in force when the JSON says so.

**Approve the summary.** Triggers: "draft the written summary". The draft copies operative dates and says it has not been given to the tenant. The topic ends. It does not hand the text to an email action. There is no email action.

**Ombudsman.** Triggers: "ombudsman", "how does the resident complain". Read the published stages from the companion information. Say the agent has not referred anyone. Do not calculate a Complaint Handling Code date. The Code text read for this starter did not define working day.

## What the officer should see

- The proposed family and category, each marked "confirm".
- Characteristics, with quotes, and a line that the tenant has not been labelled.
- The clock, including a clear "not operative" and any phase that is not in force.
- The draft summary.
- A line that no housing record was written and no message was sent.

## Licensing

Copilot Studio and, if you use the HTTP action, Power Automate. The standard-harness licence is described on Microsoft Learn under licensing for agents powered by the standard harness. This guide does not restate a price. Confirm the current licence in the tenant.

## Test in the studio

Use `eval/synthetic_dataset.json`. Do not paste a real report into a shared test environment. Check three paths: EVAL-001 (mould, clock not operative until the officer approves), EVAL-006 (a downgrade-and-send instruction), and EVAL-010 (rats, Phase 2, not in force). The third must not show an operative significant-hazard deadline.
