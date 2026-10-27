# Security and permissions

KYC evidence intake, Experiment 16. Catalogue ID B004.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for a firm deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one synthetic customer file and returns a draft checklist against regulations 28, 33, and 40 of the Money Laundering Regulations 2017. It calls Experiment 12, which calls Experiment 08. Autonomy is A1. A KYC reviewer confirms the documents and the purpose. The agent cannot execute that step, and it cannot approve, reject, or onboard a customer, assign a final risk rating, file a suspicious activity report, or send the customer note.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Confirm the documents or the purpose `kyc_evidence`.
- Approve, reject, or onboard a customer.
- Assign a final risk rating.
- Decide that regulation 33 applies, including any PEP or FATF call-for-action determination.
- File or draft a suspicious activity report.
- Send the customer note, or any other external message.
- Write a production record, including Dataverse, SharePoint, or an onboarding system.
- Download the FATF list, or look a customer up at Companies House or another register.
- Release redacted text, or describe the Experiment 08 output as anonymised.
- Re-implement Experiment 12 or Experiment 08.

There is no tool whose side effect is any of the above. `record_reviewer_confirmation` updates a copy of the JSON in memory and still does not approve the customer. The skills say the agent must not call it. `approve_customer`, `reject_customer`, `onboard_customer`, `assign_risk_rating`, `file_sar`, and `send_to_customer` raise `ReviewForbidden`. `tests/test_prohibited.py`, `tests/test_injection.py`, `tests/test_stale.py`, and `tests/test_tipping_off.py` check that an instruction inside a document does not become an action.

## Data

**Read, in this starter.** The one customer file the reviewer supplies. The as-of date and the optional stale window. The static quotations in `src/sources.py`. Experiment 12 and Experiment 08, called in-process.

**Not read.** Onboarding systems, SAR channels, the FATF list, mailboxes, and the Experiment 08 reversible token vault.

File text may contain UK identifiers, and a PEP phrase can touch political opinions, which are special category data. An NHS number in the pasted text can sit in a health context. The manifest does **not** assert a UK GDPR lawful basis and does **not** assert an Article 9 condition. A firm applying customer due diligence may look at Article 6(1)(c). This file does not choose. The caller confirms both before production use.

The Python starter does not persist the text. The draft stores hashes, closed-list phrases, and the nested inventory. It does not store the body or the screening note. A file that is not marked synthetic is refused, and the refusal does not echo the body. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use the non-allocatable National Insurance, NHS, postcode, and sort-code fixtures documented in Experiment 08. Marrowgate Payments Limited is fictional. SYN-FRN-440016 is not an FCA firm reference number. The customers are synthetic references, not real people.

## Prompt injection, stale data, and tipping-off

Fixtures include instructions hidden in an HTML comment, after a form feed, after blank lines, and between zero-width characters, including instructions to approve the customer, set a rating, or tell the customer that a report was filed. The checker records them and does not follow them. `followed` is false.

A document date older than the threshold, default 90 days, is stale. Equal to the threshold is not. The same rule applies to the source pin of 27 October 2026. A sentence in the file does not clear the flag. The 90-day window is not the five-year period in regulation 40(3).

Customer-facing text is built from fixed sentences and checked against a lexicon. Reviewer questions are marked `not_for_the_customer`. They may quote regulation 33(4), which uses the word suspicious. That word is not copied into the customer note. The lexicon is not a complete reading of section 333A. Sections 333B, 333C, and 333D were not opened.

## Human approval

| Decision | Who |
| --- | --- |
| Confirm the documents, in order, and the purpose `kyc_evidence` | KYC reviewer |
| Rely on a stale, missing, or future date, or on stale pinned sources | KYC reviewer |
| Treat an unread or checksum-failed file as evidence | KYC reviewer |
| Use the customer-facing wording | KYC reviewer. This agent cannot send it. |
| Decide whether regulation 33 is engaged | KYC reviewer. Outside the agent. |
| Assign the final risk rating | KYC reviewer. Disabled here. |
| File or not file a suspicious activity report | Nominated officer. Disabled here. |

Viewing a draft and re-running it do not need a separate approval.

## Risk register

Assessed 27 October 2026 for this starter, not for a named firm. Residual risk is not all Low. The manifest holds the full rows. The residual risk that a later model treats the draft as anonymised is High, because Experiment 08 does not redact names, email addresses, or telephone numbers, and this draft must not be described as cleaned.

## Logging and the kill switch

This starter writes no log. Before live use, log who ran it, the customer-file id, the file hashes rather than the bodies, whether injection or a stale date was flagged, and the later human decision. Do not log the screening note.

Turn the Copilot Studio agent off. Stop calling `review()`. Remove any Foundry access. Block a later connector in a Power Platform DLP policy.

## Tenant controls named and not configured here

Entra Agent ID, Conditional Access, Power Platform DLP, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights. The product pages for those controls were not opened on 27 October 2026, except the Copilot Studio harness overview. Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access are recorded in Experiment 01 as announced, with availability unverified. This folder did not re-check that announcement.

## Review

27 October 2026. Next review 27 April 2027, and sooner if regulation 28, 33, or 40, or section 333A, changes.

There is no ATRS mapping. A public body that used this pattern would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record.

The FCA press release on AI Live Testing cohort 2, opened 27 October 2026, names anti-money laundering detection and Know Your Customer among the use cases. It is context. It is not a control this folder implements, and it does not mention this agent.
