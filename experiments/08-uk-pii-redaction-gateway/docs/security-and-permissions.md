# Security and permissions

Sensitive Data Redaction Agent, Experiment 08. Catalogue ID O005.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The gateway proposes redactions of UK identifiers and returns a DPO audit record that does not contain the raw values. Autonomy is A1. A privacy reviewer approves the redacted output before anyone releases it. The agent never releases it. The output is not described as anonymised.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Release or send the redacted text.
- Claim the output is anonymised, de-identified, or safe to publish.
- Approve its own proposal.
- Write a production record, a Purview label, or a Key Vault secret.
- Look up an NHS number, a National Insurance number, a sort code, or a company.
- Decide a UK GDPR outcome for the caller.

There is no tool whose side effect is any of the above. `tests/test_gateway_safety.py` checks that an instruction to release, send, or treat the text as fully anonymised does not become an action, and that `release()` raises.

## Data

**Read, in this starter.** The one text the caller supplies. The caller id. An optional rules date. The static rules in `src/identifiers.py`.

**Not read.** The NHS Personal Demographics Service, HMRC, the Companies House register at runtime, a sort-code directory, mailboxes, and any token vault the caller later stores.

The text can contain an NHS number and other health detail. The manifest does **not** assert an Article 9 condition. The caller's DPO has to choose one before any live processing. The manifest also does not assert an Article 6 basis. A public body and a firm do not share one. Do not copy Experiment 01's public-task basis or Experiment 02's legal-obligation basis.

The Python starter does not persist the text. The audit record stores a SHA-256 and offsets.

The ICO's anonymisation guidance, read on 26 October 2026, says effective anonymisation means people are not identifiable, and that pseudonymisation leaves personal data in scope. Replacing an identifier, and keeping a map, is the second of those. This gateway's default is not to return the map. Either way, `output_is_anonymised` is false.

Production inference, if a model adapter is added, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at the time of deployment. The deterministic path makes no network call.

## Prompt injection and stale rules

Fixtures include instructions to ignore the rules, to skip redaction, to call the text fully anonymised, and to release it. The detectors still run. An earlier `rules_as_of` is flagged. The pinned date stays 26 October 2026. A sentence in the text cannot move it.

The residual risk is a missed identifier. The reviewer is the control for release. There is no autonomous send behind a bad proposal. Residual risk R1 in the manifest is High. Do not read the register as a finished assessment.

## Human approval

| Decision | Who |
| --- | --- |
| Approve the redacted output before release | Privacy reviewer |
| Accept or reject each model suggestion before it is treated as a redaction | Privacy reviewer |
| Decide whether a reversible token vault may be stored | Privacy reviewer |
| Release or send the redacted output | Privacy reviewer. Outside the agent even after approval. |

Viewing a proposal and re-running detection do not need a separate approval.

## Platform controls, for a deployment this starter does not perform

**Microsoft Entra Agent ID and Conditional Access.** [Conditional Access for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id), retrieved 26 October 2026, describes Conditional Access for agent identities and for agents acting for a user. The page lists licence plans, including Microsoft 365 E7 and an Agent 365 licence with Entra P1 or Microsoft 365 E3. That is what the page said. It is not a licensing recommendation, and this starter does not register an agent identity. Confirm the tenant. A policy that targets an agent identity does not, on that page, apply to a separate agent user account.

**Power Platform DLP.** A data-loss-prevention policy can block a connector someone adds later for mail or for a case system. No policy is created here. Whether a custom connector for this gateway would land in a given connector group was not verified on 26 October 2026.

**Microsoft Purview.** Sensitivity labels and Purview DLP are the usual tenant controls for classified files. This starter does not create a label or a policy. How a redaction proposal should be labelled was not verified.

**Microsoft Foundry prompt shields.** Described in [foundry.md](foundry.md). They detect prompt attacks. They do not redact UK identifiers and they do not replace the missing release tool. Document attack detection is off by default on the page that was read. Spotlighting is preview. Nothing is deployed here.

**Key Vault.** The place a caller would store a reversible map, or a model key if a managed identity cannot be used. Not provisioned. The gateway does not write to it.

**Application Insights.** A production caller may send the audit events, without raw identifiers and without the token map. Not configured. A UK-resident workspace is a deployment choice this repository cannot enforce.

## Logging

This starter writes no log of its own. The proposal contains the audit record. Before live use, store that record, not the source text, where the DPO can read it. Do not put the token vault in the same row.

## Kill switch

Stop the caller importing `propose`. Turn the Copilot Studio agent off. Remove any model adapter's identity. If a connector has been added despite the default, block it in a Power Platform DLP policy.

Contacts in the manifest use `example.com`. They are placeholders.

## Review

Reviewed for this starter on 26 October 2026. Next review 26 April 2027, and sooner if the NHS, HMRC, or Companies House rules cited in the README change.
