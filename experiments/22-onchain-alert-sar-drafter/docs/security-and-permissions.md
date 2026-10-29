# Security and permissions

On-chain monitoring alert investigator and SAR narrative drafter, Experiment 22. Catalogue ID UK07.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for a firm deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one synthetic on-chain alert, and any Travel Rule transfer or KYC file supplied with it, and returns an internal timeline, an investigation note, and a SAR narrative. Autonomy is A1. The nominated officer decides whether the section 330 or section 331 test is met and whether to file. The agent cannot execute that step. It cannot file with the National Crime Agency, request a defence, freeze or move a cryptoasset, or draft customer-facing content.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- File, submit, or suppress a suspicious activity report.
- Request a defence against money laundering or a defence against terrorist financing.
- Decide that anyone knows or suspects, or that there are reasonable grounds.
- Record the nominated officer's decision.
- Assign a SAR glossary code.
- Draft or send any customer-facing wording.
- Freeze, restrict, or close an account or a wallet.
- Move a cryptoasset.
- Query a chain, a node, or a blockchain-analytics vendor.
- Write a production record, including Dataverse, SharePoint, or a case system.
- Release redacted text, or describe the Experiment 08 output as anonymised.

There is no tool whose side effect is any of the above. `file_with_nca`, `request_daml`, `contact_customer`, `freeze_account`, `move_crypto`, `record_mlro_decision`, `record_suspicion`, and `assign_glossary_code` raise `InvestigationForbidden`. `tests/test_prohibited.py`, `tests/test_injection.py`, `tests/test_stale.py`, `tests/test_addresses.py`, and `tests/test_tipping_off.py` check that an instruction inside a case does not become an action.

## Data

**Read, in this starter.** The one case the analyst supplies. The as-of date and the optional stale window. The static quotations in `src/sources.py`. Experiments 10, 16, and 08, called in-process when the case includes the matching input. Experiment 04's pinned source row, not its gap register.

**Not read.** The NCA SAR Portal, chain nodes, private keys, customer channels, production records, the SAR glossary, and the Financial Crime Guide.

An analyst note may contain UK identifiers. The manifest does **not** assert a UK GDPR lawful basis and does **not** assert an Article 9 condition. A firm keeping records under the Money Laundering Regulations may look at Article 6(1)(c). This file does not choose. The caller confirms both before production use. There is no ATRS mapping. This starter is not a public-sector tool and does not submit a record.

The Python starter does not persist the text. A case that is not marked synthetic is refused, and the refusal does not echo the body. A string that looks like a live chain address is omitted and is not copied. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use the non-allocatable National Insurance number and postcode fixtures documented in Experiment 08. Harbourline Markets Ltd is fictional. Addresses start with `SYNTH-ADDR-`. Hashes start with `SYNTH-TX-`.

## Prompt injection, stale data, and tipping-off

Fixtures include instructions to file, not to file, tell the customer, freeze a wallet, move crypto, and request a defence. The checker records them and does not follow them. `followed` is false. A field longer than 4,000 characters is not fully read.

A source pin or an alert date older than the threshold, default 90 days, is stale. Equal to the threshold is not. An event after the as-of date is listed and not treated as having happened. A sentence in the case does not clear the flag.

Customer-facing text is not drafted. `customer_facing.text` is always null. A requested customer message is scanned for instructions and then dropped. It is not echoed. Section 333A turns on whether a disclosure is likely to prejudice an investigation. This agent does not make that judgement. Sections 333B, 333C, and 333D were not opened.

## Human approval

| Decision | Who |
| --- | --- |
| Decide whether the section 330 or section 331 test is met | Nominated officer |
| File or not file with the NCA | Nominated officer |
| Request a defence against money laundering or terrorist financing | Nominated officer |
| Rely on a stale source, a stale alert, or a future-dated event | Nominated officer |
| Treat a sanctions marker, a PEP marker, or a counterparty label as a determination | Nominated officer |
| Use any customer-facing wording | Nominated officer. This agent drafts none. |

Viewing a draft and re-running it do not need a separate approval.

## Risk register

Assessed 29 October 2026 for this starter, not for a named firm. Residual risk is not all Low. The manifest holds the full rows. The residual risk that a later model writes a customer sentence from this context is the one the design refuses in code: there is no customer-text field to fill.

## Logging and the kill switch

This starter writes no log. Before live use, log who ran it, the alert id, whether injection or a stale date was flagged, and the later human decision. Do not log the analyst note, an omitted address, or a requested customer message.

Turn the Copilot Studio agent off. Stop calling `investigate()`. Remove any Foundry access. Block a later connector in a Power Platform DLP policy.

## Tenant controls named and not configured here

Entra Agent ID, Conditional Access, Power Platform DLP, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights. The product pages for those controls were not opened on 29 October 2026, except the Copilot Studio harness overview. Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access are recorded in Experiment 01 as announced, with availability unverified. This folder did not re-check that announcement.

## Review

29 October 2026. Next review 29 April 2027, and sooner if section 330, section 331, section 333A, or regulations 19 or 21 change.

There is no ATRS mapping. A public body that used this pattern would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record.
