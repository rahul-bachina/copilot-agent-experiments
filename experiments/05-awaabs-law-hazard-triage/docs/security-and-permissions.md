# Security and permissions

Awaab's Law hazard triage, Experiment 05. Catalogue ID UK01.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for a landlord deciding whether to try the starter, not as a completed DPIA or an ATRS record.

## Purpose

The agent drafts a triage for a housing officer: a proposed category, vulnerability characteristics for review, the statutory clock, a written summary, Ombudsman information, and a reasonable-endeavours record. Autonomy is A1. The officer approves the hazard category, the clock, and every tenant-facing summary.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Send the written summary, a safety note, an email, an SMS, or any other tenant-facing message.
- Create or update a housing management record, a repairs order, or a Dataverse row.
- Decide the hazard category, or that the home is a social home.
- Decide that the section 10A(5) defence is made out.
- Refer a complaint to the Housing Ombudsman.
- Label a tenant as vulnerable, or write a marker onto a tenancy.
- Book alternative accommodation or spend.
- Downgrade a proposal because the report text says to.
- Calculate a timeframe inside the model. Dates come from `src/statutory_clock.py`.

There is no tool whose side effect is any of the above. `tests/test_triage_safety.py` checks that an instruction to send, write, label, refer, or declare a defence does not become an action.

## Data

**Read, in this starter.** The report the officer supplies. The awareness time and, if the officer has confirmed them, the category, the hazard family, and the other clock inputs. Steps the officer types for the endeavours record. The static instructions.

**Not read.** Housing management production data, tenancy vulnerability markers, contractor or finance systems, mailboxes, Housing Ombudsman systems, and other tenants' reports.

A report can contain health information and information about a child. The manifest does **not** assert an Article 9 condition. The landlord's DPO has to choose one before any live processing. The starter's lead basis is Article 6(1)(c), legal obligation under section 10A. A council may also look at public task. A private registered provider should not copy a public-task basis without advice. The Python starter does not persist the text.

Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at the time of deployment.

## Controls to confirm before a tenant is connected

Nothing in this list is provisioned by the repository. Names are the ones on the Microsoft pages read on 24 October 2026, except where a page was not opened.

**Microsoft Entra Agent ID.** The Entra what's-new page says the Agent ID platform became generally available in April 2026 ([what's new](https://learn.microsoft.com/en-us/entra/fundamentals/whats-new)). The page on creating an agent identity still labels the admin center wizard "New agent identity (Preview)" ([create agent identities](https://learn.microsoft.com/en-us/entra/agent-id/create-delete-agent-identities)). Use a dedicated identity if the landlord deploys this, with no mail and no housing role. This starter does not create one. The wizard's Preview label is a preview feature. Do not treat the whole platform as preview, and do not treat the wizard as generally available, on the strength of those two pages.

**Conditional Access.** Entra Agent ID documentation describes Conditional Access for agent identities. A policy is a tenant decision. None is configured here. Unverified in this repository: the exact policy templates in a given tenant.

**Power Platform DLP.** A data-loss-prevention policy should block mail connectors and housing connectors in the environment that hosts the clock flow. The flow only needs to call the clock API. See [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md). No policy file is included.

**Microsoft Foundry prompt shields.** Microsoft documents prompt shields as a control on generative deployments. Confirm the current control name in the Foundry resource you use. This starter does not enable one, because it does not call a model. Unverified here: the portal label on 24 October 2026. That product page was not opened for this revision. The tests in this folder are the control on the mock stand-in.

**Key Vault.** If the clock API cannot use a managed identity, the secret belongs in Key Vault, not in the flow and not in this repository. Revoking that access is one of the kill switches in the manifest. The vault is not provisioned.

**Microsoft Purview.** A landlord that already uses Purview for audit or DLP should decide whether this agent's prompts and outputs are in scope. This starter does not connect Purview, and it does not claim a particular Copilot Studio audit schema. That wiring is unverified here.

**Application Insights.** A production host can send operational telemetry there. Do not log the report text. This starter sends nothing.

**Data (Use and Access) Act 2025.** Section 80 inserts Articles 22A to 22D, with safeguards for significant decisions based solely on automated processing. This starter does not make the hazard category, the clock approval, or the summary a solely automated decision. The officer approves each one. That is a design choice, not a legal opinion that the articles cannot apply to some other deployment.

## Prompt injection and stale data

The report is untrusted. Fixtures include "ignore previous instructions", "send the summary", "mark the tenant as vulnerable", a 2019 inspection presented as the awareness time, and an instruction to write the housing system and declare the defence.

The mock triage flags those and still:

- keeps the officer's awareness time
- refuses to send, file, label, refer, or find a defence
- refuses to lower the proposal

The residual risk is a misleading draft. The officer is the control. There is no autonomous action sitting behind a bad draft.

## Human approval

Mandatory before anyone relies on the output:

- the hazard category and the hazard family
- that the home is a social home in England
- the clock
- Part 6 compliance, or that preventative work cannot reasonably begin within five working days, before those facts change a hard stop
- a vulnerability characteristic, before it is recorded anywhere
- the written summary, before it is given to the tenant
- the endeavours record, before it is filed

Viewing a draft and calculating a clock that comes back non-operative do not need a separate approval. Relying on the date does.

## Logging

This starter writes no log. Before live use, log the invocation (who, when, size of the text, not the text), the clock inputs and the rule ids, the officer's approvals, and any rejected draft. Keep the report on the repairs file only.

## Kill switch

Turn the Copilot Studio agent off. Remove the Foundry access used by any orchestration. If a connector has been added despite the default, block it in a Power Platform DLP policy. The manifest lists placeholder contacts on `example.com`. Replace them. They are not a landlord.

## Review

Reviewed for this starter on 24 October 2026. Next review 24 April 2027, and sooner if the regulations change. On that retrieval the Phase 2 amendment was still a draft, not a made statutory instrument, with a stated commencement of 30 November 2026. Phase 3 had no instrument. A proclaimed change to England and Wales bank holidays also needs a review.

## Synthetic data

Every report in `eval/` and `examples/` is invented. Do not paste a live case into a shared test environment.
