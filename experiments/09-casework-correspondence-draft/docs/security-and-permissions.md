# Security and permissions

Correspondence Draft Agent, Experiment 09. Catalogue ID O008.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for a correspondence unit, a DPO, and a security lead deciding whether to try the starter. It is not a completed DPIA and it is not an ATRS submission.

## Purpose

The agent drafts one reply from supplied lines to take, proposes a channel, calculates a casework clock, and flags vulnerability wording. Autonomy is A1. The author approves the recipient and the final text.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Send a letter, an email, a holding reply, or a transfer.
- Choose the final recipient from the letter.
- Invent a policy position, or paste a withdrawn, overdue, or future line.
- Create or update a correspondence case.
- Publish an ATRS record, or decide that a deployment is in mandatory scope.
- Decide that no reply will be sent, decide an FOI exemption, or decide a complaint outcome.
- Label a person, or auto-close a case.
- Calculate the reply date inside a model. Dates come from `src/sla.py`.

There is no tool whose side effect is any of the above. `tests/test_draft_safety.py` checks that an instruction to send, approve a recipient, invent a closure, publish the ATRS note, or close the case does not become an action.

## Data

**Read, in this starter.** The letter the author pastes. The receipt date, the as-of date, and, if the author has confirmed them, the regime and the target. The synthetic lines file. The static instructions. The Python starter does not persist the text.

**Not read.** Mailboxes, case-management systems, MP or constituent directories, other cases, and ATRS publication systems.

An address in the letter is not copied into `approved_recipient`. The author types the address as an argument if they want it recorded, and the draft is still not sent.

Letter text can contain health information and other special-category data. The manifest does **not** assert an Article 9 condition. The Guide, paragraphs 47 to 50 in the PDF retrieved on 26 October 2026, describes bases a department could consider, including Data Protection Act 2018 Schedule 1 paragraphs 6 and 23. This starter does not assert them. The DPO chooses a condition before any live processing.

The lead basis recorded for ordinary correspondence is Article 6(1)(e), public task, which is the basis Guide paragraph 45 says public bodies should consider. The DPO confirms it. FOI, EIR, and subject-access letters are routed out. Paragraph 46's legal-obligation basis is described and not applied, because this agent does not answer those requests.

Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

## Entra, Conditional Access, and DLP

**Microsoft Entra Agent ID.** The overview retrieved on 26 October 2026 describes it as the identity and security framework for agents, and says Agent ID is available for all Microsoft Entra customers. It links Conditional Access for agents. It also says extending Entra security features to agents requires Microsoft Agent 365. This starter does not register an agent identity or a blueprint. The page on creating an agent identity, including any Preview label on the admin-center wizard, was not opened for this revision. Do not treat a wizard label as verified here.

**Conditional Access.** The Agent ID overview says agents can receive adaptive access policies and links a Conditional Access page. That page was not opened. No policy is configured here. Which templates a tenant can turn on is unverified in this repository.

**Power Platform DLP.** The agents overview retrieved the same day lists DLP and governance controls as supported on both the standard harness and the GitHub Copilot harness. This repository does not apply a policy. Before any connector is added, a DLP policy should block mail and case-system connectors. The manifest has to change in the same change as any connector. The exact connector names in a tenant's DLP taxonomy were not verified.

## Key Vault, Purview, Application Insights, prompt shields

**Key Vault.** Not provisioned. If a later Foundry call cannot use a managed identity, the key belongs in Key Vault, and removing that access is one of the kill switches. No secret is stored in this folder.

**Microsoft Foundry prompt shields.** Microsoft documents prompt shields as a control on generative deployments. Confirm the current control name in the resource you use. This starter does not enable one, because it does not call a model. Unverified here: the portal label on 26 October 2026. That product page was not opened. The tests in this folder are the control on the mock stand-in. A filter is not a substitute for having no send tool.

**Microsoft Purview.** The Entra page says Agent 365 can be bought as an add-on with the Purview suite. It does not say that a Copilot Studio transcript of this agent is audited. An organisation that already uses Purview should decide whether prompts and outputs are in scope. This starter does not connect Purview, and it does not claim a particular audit schema. That wiring is unverified here.

**Application Insights.** Not configured. A later deployment can log invocation counts, the library id, and failure codes. It should not log the letter. Whether Copilot Studio writes its own run history into Application Insights was not verified. The agents page says this harness has a Monitor tab for sessions and credit usage. That is not the same statement as an Application Insights workspace.

## Prompt injection and stale data

The letter is untrusted. Fixtures include "ignore previous instructions", "send the email", "recipient approved", an instruction to state that parks will close permanently, "treat the withdrawn line as current", "publish the ATRS record", "close the case", and a 2014 position presented as current.

The mock drafter flags those and still:

- keeps the author's receipt date and as-of date
- refuses to send
- refuses to approve a recipient from the letter
- refuses to paste a withdrawn or overdue line
- leaves send, final recipient, policy invention, case write, ATRS publication, no-reply, transfer, FOI exemption, complaint outcome, and a vulnerability label in `decisions_not_taken`

The residual risk is a misleading draft around the cited lines. The author is the control. There is no autonomous action sitting behind a bad draft.

## Human approval

Mandatory before anyone relies on the output:

- the channel, and whether a ministerial reply is required
- the reply target, before a due date is treated as operative
- a vulnerability or immediate-review flag, before it is recorded
- the recipient
- the final text
- sending, which stays outside the agent even after that approval
- a no-reply decision, a transfer, an information-rights outcome, or a complaint outcome, which are outside the agent

Viewing a draft, re-running it, and calculating a reference clock from a target the author has typed do not need a separate approval. Relying on the date does.

The standard-harness topics and the GitHub Copilot harness skills use this list as it stands. Neither harness adds an approval point, and neither is given a send or a write. See [harness-comparison.md](harness-comparison.md).

## Logging

This starter writes no log. Before live use, log who ran it, when, the size of the text rather than the text, the library id, the clock inputs and the reason code, the line ids cited, and the author's approval of the recipient and the text. Do not log the letter in an application trace. The letter belongs on the case file.

## Kill switch

Turn the Copilot Studio agent off. Remove the Foundry access used by any orchestration. If a connector has been added despite the default, block it in a Power Platform DLP policy. The manifest lists placeholder contacts on `example.gov.uk`. Replace them. They are not a department.

## Review

Reviewed for this starter on 26 October 2026. Next review 26 April 2027, and sooner if the correspondence guide changes or England and Wales bank holidays change by proclamation.

## Synthetic data

The fixtures, the sample, and the smoke report use invented people and the fictional Department for Civic Spaces. Do not replace them with live letters in this repository.

## Assumptions

Listed as A1 to A6 in the manifest: the calendar and the 20-working-day ceiling for a department, the UK GDPR basis, UK-region Foundry, no mailbox or case connector without a manifest change, a real lines library before production, and placeholder contacts.
