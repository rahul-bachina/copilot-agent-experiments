# Security and permissions

Complaint Intake Agent, Experiment 02. Catalogue ID C006.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for a firm deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent drafts an intake for a complaints handler: a proposed classification, vulnerability characteristics for review, a DISP clock, a Consumer Duty mapping, and an acknowledgement. Autonomy is A1. A handler validates every classification and every severity.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Send an acknowledgement, a summary resolution communication, a holding response, a final response, or any other message.
- Create, update, resolve, or close a Dynamics 365 case, or write any other production record.
- Uphold, reject, or close a complaint.
- Decide redress, a refund, a goodwill payment, or a fee waiver.
- Refer a complaint to the Financial Ombudsman Service.
- Label a customer as vulnerable, or write a marker onto a customer record.
- Decide that the firm has breached the Consumer Duty.
- Calculate DISP dates inside the model. Dates come from `src/disp_clock.py`.

There is no tool whose side effect is any of the above. A prompt-injection test checks that an instruction to uphold, pay, send, or label does not become an action. See `tests/test_intake_safety.py`.

## Data

**Read, in this starter.** The complaint text the handler supplies for that run. The receipt date and, if the handler has confirmed them, the route and the provider's closed dates. The static instructions.

**Not read.** Dynamics 365 production data, customer vulnerability markers, core banking or policy systems, mailboxes, Financial Ombudsman Service systems, and other customers' complaints.

A later read of one open incident is described in [dynamics-365-customer-service.md](dynamics-365-customer-service.md). It is not built, and the manifest must be edited before it is.

Complaint text can contain health information and other special-category data. The manifest does **not** assert an Article 9 condition. The firm's DPO has to choose one before any live processing. The starter's lead basis for ordinary complaint handling is Article 6(1)(c), legal obligation under DISP, and that too is marked as something to confirm. Do not copy Experiment 01's public-task basis. This agent is for a firm, not a public authority.

The Python starter does not persist the text. Retention of whatever the handler then saves is the firm's complaints-file schedule.

Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at the time of deployment.

## Prompt injection and stale data

The complaint is untrusted. Fixtures include "ignore previous instructions", "send the email", "mark the customer as vulnerable", a 2014 balance presented as current, and an instruction to move the receipt date to 2019.

The mock intake flags those and still:

- keeps the handler's receipt date
- refuses to send
- refuses to label the customer
- leaves uphold, reject, redress, close, and FOS referral in `decisions_not_taken`

The residual risk is a misleading draft. The handler is the control. There is no autonomous action sitting behind a bad draft.

## Human approval

Mandatory before anyone relies on the output:

- the complaint classification
- product, root cause, and severity
- the route passed into the clock
- exceptional circumstances, before a 35-business-day date is used
- a vulnerability characteristic, before it is recorded anywhere
- the acknowledgement, before it is sent
- any uphold, reject, redress, or closure, which are outside the agent even after approval of the draft

Viewing a draft, re-running it, and calculating the clock from inputs the handler has typed do not need a separate approval. Relying on a suggested PSD route does.

## Logging

This starter writes no log. Before live use, log the invocation (who, when, size of the text, not the text), the clock inputs and the rule ids, the handler's edits, and any schema rejection. Keep the complaint itself on the case file only.

## Kill switch

Turn the Copilot Studio agent off. Remove the Foundry access used by any orchestration. If a connector has been added despite the default, block it in a Power Platform DLP policy. The manifest lists placeholder contacts on `example.com`. Replace them. They are not a real firm.

## Review

Reviewed for this starter on 24 October 2026. Next review 24 April 2027, and sooner if DISP changes. The DISP 1.6 page retrieved on 24 October 2026 showed a future version dated 25 October 2027. That text is not encoded. A proclaimed change to England and Wales bank holidays also needs a review, because the clock will not invent one-off holidays.

## Synthetic data

The fixtures, the sample, and the smoke report use invented people and a fictional firm, Northbridge Mutual. Do not replace them with live complaints in this repository.

## Assumptions

Listed as A1 to A5 in the manifest: England and Wales calendar, the UK GDPR basis, UK-region Foundry, no Dynamics connector without a manifest change, and placeholder contacts.
