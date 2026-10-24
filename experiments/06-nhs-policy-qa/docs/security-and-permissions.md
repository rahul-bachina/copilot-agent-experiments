# Security and permissions

Policy Q&A for UK public-sector and NHS corporate services, Experiment 06. Catalogue ID M003.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for an organisation deciding whether to try the starter, not as a completed DPIA, a clinical safety case, or an ATRS record.

## Purpose

The agent quotes approved HR, finance, procurement, IT, and estates policies, with the version and the review date. It says "I don't know" when nothing approved and in date matches. It withholds a policy past its review date. It reports a conflict and drafts a change note that is not published. Autonomy is A0. The policy owner approves authoritative sources. The agent cannot.

Clinical questions are refused and signposted. The starter does not claim a medical-device classification. A clinical safety officer decides what applies before any deployment that could touch care.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Approve or reject a policy, a source, an expense, a request, or a disciplinary outcome.
- Give clinical advice, or read a patient record, a prescribing system, or a guideline library.
- Decide a person's leave balance, pay, or entitlement.
- Place an order, award a contract, or approve spend.
- Publish a change note, or create or update SharePoint, a policy register, payroll, or a finance system.
- Send email, a Teams message, or any other communication.
- Treat a stale policy, a draft, a superseded file, or an unapproved note as the current rule.
- Choose between two approved policies that disagree.

There is no tool whose side effect is any of the above. `tests/test_answer.py` checks that an instruction to approve, a clinical question, a draft, and a stale policy do not become an action or a quotation.

## Data

**Read, in this starter.** The synthetic register. One question. The as-of date. The owner review reads the same register, including drafts, so it can report gaps. Staff answers do not quote those drafts.

**Not read.** Patient records, prescribing, payroll, ESR, staff files, finance ledgers, purchase-to-pay, mailboxes, Teams chats, and the unfiltered SharePoint library.

The register in this folder is fictional and contains no personal data. A question someone types later might. The manifest does **not** assert an Article 9 condition. The organisation's DPO confirms the Article 6 basis before any live processing. Public task is a candidate for a public body. It is not a decision, and it should not be copied from this file into a firm. The Python starter does not persist the question.

Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at the time of deployment.

## Controls to confirm before a tenant is connected

Nothing in this list is provisioned by the repository. Names are the ones on the Microsoft pages read on 24 October 2026, except where a page was not opened.

**Microsoft Entra Agent ID.** The Entra what's-new page says the Agent ID platform became generally available in April 2026 ([what's new](https://learn.microsoft.com/en-us/entra/fundamentals/whats-new)). The page on creating an agent identity still labels the admin center step "New agent identity (Preview)" ([create agent identities](https://learn.microsoft.com/en-us/entra/agent-id/create-delete-agent-identities)). The programmatic example on that page calls Microsoft Graph on the beta endpoint. Use a dedicated identity if the organisation deploys this, with no mail role and no clinical role. This starter does not create one. The wizard's Preview label is a preview feature. The beta example is not the same statement as the platform's general availability. Do not treat the wizard or the beta call as generally available on the strength of the what's-new sentence alone.

**Conditional Access.** Entra Agent ID documentation describes Conditional Access for agent identities. A policy is a tenant decision. None is configured here. The what's-new page also lists extended Conditional Access protections for agents' user accounts as a public preview item. Unverified in this repository: which of those controls a given tenant can turn on.

**Power Platform DLP.** A data-loss-prevention policy should block mail, SharePoint write, payroll, finance, and clinical connectors in the environment that hosts the flow. The flow only needs to call the register API. No policy file is included.

**Microsoft Foundry prompt shields.** Microsoft documents prompt shields as a control on generative deployments. Confirm the current control name in the Foundry resource you use. This starter does not enable one, because it does not call a model. Unverified here: the portal label on 24 October 2026. That product page was not opened for this revision. The tests in this folder are the control on the deterministic register.

**Key Vault.** If the register API cannot use a managed identity, the secret belongs in Key Vault, not in the flow and not in this repository. Revoking that access is one of the kill switches in the manifest. The vault is not provisioned.

**Microsoft Purview.** An organisation that already uses Purview for audit or sensitivity labels should decide whether this agent's prompts and outputs are in scope. This starter does not connect Purview, and it does not claim a particular Copilot Studio audit schema. That wiring is unverified here.

**Application Insights.** A production host can send operational telemetry there. Do not log the question or the clause text. This starter sends nothing.

**SharePoint.** Pointing generative answers at the policy library is the control that would fail closed if it were added. Drafts and old versions live beside current files. The build guide leaves that connector off. DLP is the backstop if someone adds it later.

**Data (Use and Access) Act 2025.** Section 80 inserts Articles 22A to 22D, with safeguards for significant decisions based solely on automated processing. This starter does not make a clinical decision, an entitlement decision, or a policy approval. It returns a quotation or a refusal. That is a design choice, not a legal opinion that the articles cannot apply to some other deployment.

## Prompt injection and stale data

The question and the policy text are untrusted. Fixtures include "ignore previous instructions", a request to set `approved_by_policy_owner`, a clinical question mixed with that instruction, a superseded leave policy, a draft that allows verbal orders, a password rule past its review date, and a clause whose only job is to instruct the model.

The register:

- quarantines the instructing clause
- refuses the instructing question
- leaves drafts, superseded files, and unapproved notes out of staff answers
- withholds a policy whose review date is before the as-of date, and does not return the clause text
- refuses to pick a side when two approved policies disagree

The residual risk is a misleading reading of the JSON, if a model is wrapped around it later. The member of staff, and the policy owner for any change, are the control. There is no autonomous action sitting behind a bad draft.

## Human approval

Mandatory before anyone relies on the output:

- adding or replacing a document in the authoritative register (policy owner)
- accepting a change note and amending a policy (policy owner)
- relying on a quotation as the current rule (the person who asked, within their role)
- using a quarantined clause as policy text (policy owner)

Viewing a draft answer does not need a separate approval. The agent still cannot publish it. A stale or conflicting result is already marked `may_be_relied_on` false.

## Logging

This starter writes no log. The JSON includes an unanswered-question entry with `persisted` false. Before live use, log who ran it, when, the outcome, the policy ids and review dates, and the as-of date. Keep the question text out of the trace.

## Kill switch

Turn the Copilot Studio agent off. Remove the Foundry access used by any orchestration. If a connector has been added despite the default, block it in a Power Platform DLP policy. The manifest lists placeholder contacts on `example.com`. Replace them. They are not an organisation.

## Review

Reviewed for this starter on 24 October 2026. Next review 24 April 2027, and sooner if a clinical question is found to have been answered, if SharePoint or a model is connected, or if NHS England publishes a new position on Copilot in corporate services or in clinical work.

## Synthetic data

Every policy in `fixtures/` and every question in `eval/` is invented. Northmere NHS Foundation Trust is not a real trust. Do not paste a live policy or a real staff question into a shared test environment.

## NHS rollout facts used in the README

Checked on 24 October 2026 against [NHS England's announcement of 8 June 2026](https://www.england.nhs.uk/2026/06/500000-nhs-staff-to-get-new-artificial-intelligence-tools-to-help-free-up-more-time-for-patients/) and a [Microsoft feature of 21 October 2026](https://news.microsoft.com/source/emea/features/before-the-ambulance-arrives-how-ai-is-helping-the-nhs-rethink-patient-care/). The 43-minute trial figure is not a result of this experiment. The announcement does not, on the page opened, mention Copilot Studio. This starter uses Copilot Studio because catalogue row M003 is M365 + CS.
