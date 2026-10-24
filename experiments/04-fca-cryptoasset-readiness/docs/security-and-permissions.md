# Security and permissions

FCA cryptoasset authorisation readiness gap checker, Experiment 04. Catalogue ID UK02.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for a firm deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one policy pack and returns a draft observation register against a pinned FCA catalogue. Autonomy is A0. It has no action to take on the draft. The Compliance Officer or the MLRO owns every gap conclusion.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Conclude that a firm is ready, or that it is not ready.
- Give regulatory advice or legal advice.
- Accept or reject a gap.
- Submit an application, use Connect, or email the FCA.
- File a suspicious activity report.
- Approve a financial promotion.
- Treat a consultation or a plan to consult as a final rule.
- Write a production record or send a message.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. Tests in `tests/test_gap_register.py` and `tests/test_injection.py` check that an instruction inside a policy does not become a finding or an action.

## Data

**Read, in this starter.** The pack the reviewer supplies for that run. The as-of date and the stale threshold. The static catalogue.

**Not read.** Connect, KYC files, transaction alerts, blockchain-analytics tenants, SARs, wallets, private keys, mailboxes, and other firms' packs.

Policy text can name staff. The manifest does **not** assert a UK GDPR lawful basis. A candidate for the firm to confirm is Article 6(1)(f), legitimate interests, for an internal review of the firm's own drafts. Do not copy a public-task basis from Experiment 01. Special-category data is out of scope. If a pack contains it, stop and remove it before any production run.

The Python starter does not persist the pack. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

## Prompt injection and stale data

Uploaded policies are untrusted. The scanner drops a line that tells the checker to ignore instructions, mark the firm ready, suppress gaps, change `last_verified`, or treat a consultation as final. An instruction split across lines quarantines the document, so the rest of that file is not used as evidence.

The stale-data test compares `last_verified` (24 October 2026 in this catalogue) with the as-of date. Older than the threshold, default 90 days, is `stale`. Equal to the threshold is not. The checker does not download the page. A policy's own date is a separate flag, default 365 days, and is not the FCA-source test.

The residual risk is a misleading draft if a model is later wrapped around the JSON. The Compliance Officer or MLRO is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A0 means the agent cannot execute the decision even after a person agrees. The person still has to make it.

| Decision | Who |
|---|---|
| Treat an observation as a gap | Compliance Officer or MLRO |
| Rely on a row after a source is marked stale | Compliance Officer or MLRO, after someone re-opens the page |
| Use a quarantined document as evidence | Compliance Officer or MLRO |
| Copy the draft into a system the firm will rely on | Compliance Officer or MLRO |
| Submit an application or file a SAR | The firm's authorised person, or the MLRO. Outside the agent. |

Viewing the draft, re-running it, and printing the sources table do not need a separate approval.

## Controls a tenant would discuss

This starter configures none of them. Where this folder did not open the product page on 24 October 2026, the row says so.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Entra Agent ID | Not configured | The identity a production agent should run as. The product page was not opened for this experiment. |
| Conditional Access | Not configured | Restrict who can open the agent. Not re-verified here beyond the control name. |
| Power Platform DLP | Not configured | Block mail, HTTP to Connect, and a SharePoint write if someone proposes a connector later. |
| Microsoft Foundry prompt shields | Not called | Turn them on if a model sees the pack. Detailed filter behaviour was not re-opened. The injection scan in code does not depend on them. |
| Key Vault | Not provisioned | Only if a later secret exists. The checker has no secret. Removing a Foundry credential, if one is added, is a kill-switch step in the manifest. |
| Microsoft Purview | Not configured | Classification and retention of the pack are the firm's. |
| Application Insights | Not configured | If it is enabled, do not log policy text. |
| Dynamic Permissions, Dynamic Agent Risk, Dynamic Conditional Access | Not used | Experiment 01 records these as announced, with availability unverified. This folder did not re-check that announcement. |

## Logging

This starter writes no log. Before live use, log who ran it, when, the document ids and sizes rather than the text, the as-of date, the catalogue `last_verified` values, injection pattern ids, and the reviewer's accept or reject. Keep the policy on the firm's own file, not in an application trace.

## Kill switch

Turn the Copilot Studio agent off. Remove any Foundry access. If a connector has been added despite the default, block it in a Power Platform DLP policy. Stop calling the local checker. Contacts in the manifest use `example.com`. They are placeholders.

## Review

Reviewed for this starter on 24 October 2026. Next review 24 April 2027, and sooner if a pinned FCA page changes. The catalogue does not update itself.

## Synthetic data

The fixtures, the Harbourline pack, and the smoke report use an invented firm, Harbourline Markets Ltd. Do not replace them with a live application pack in this repository.

## Assumptions

Listed as A1 to A6 in the manifest: the lawful basis, UK-region Foundry if a model is used, a person re-checking the FCA pages, no connector without a manifest change, placeholder contacts, and synthetic samples only.
