# Security and permissions

Cryptoasset financial promotions pre-checker, Experiment 23. Catalogue ID UK08.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for a firm deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one synthetic cryptoasset promotion (web copy, a social post, or app screen text) and returns a draft checklist for a human compliance reviewer. Autonomy is A0. The section 21 approver signs off. The agent cannot execute that step. It cannot approve a promotion, publish one, rewrite copy, or give a compliance opinion.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Approve, reject, or sign off a financial promotion under section 21 of the Financial Services and Markets Act 2000.
- Publish, schedule, or send a promotion.
- Draft replacement copy.
- Give a compliance opinion or legal advice.
- Decide that section 21, article 73ZA, or paragraph 26F applies, or that an offence under section 25 would be committed.
- Decide that a person has permission under section 55NA. That section was not opened.
- Look up the Financial Services Register or FCA Connect.
- Write a production record, including an approvals register, a CMS, Dataverse, or SharePoint.
- Apply an inventory lifecycle status. Experiment 03 is called with no approval.
- Release redacted text, or describe the Experiment 08 output as anonymised.

There is no tool whose side effect is any of the above. `approve_promotion`, `publish_promotion`, and `give_compliance_opinion` raise `ProhibitedAction`. `tests/test_prohibited.py`, `tests/test_injection.py`, and `tests/test_stale.py` check that an instruction inside a draft does not become an action.

## Data

**Read, in this starter.** The one promotion the reviewer supplies. The as-of date and the optional stale window. The static quotations in `src/sources.py`. Experiment 08, called in-process on the body. Experiment 03, called in-process when an inventory record and a requested lifecycle status are present. Experiment 04's pinned marketing-page row, not its gap register.

**Not read.** Publishing tools, social accounts, the Financial Services Register, section 55NA, section 55NB, COBS 4 Annex 1R, COBS 10, COBS 10A, and recipient lists.

A draft may contain a UK identifier. The manifest does **not** assert a UK GDPR lawful basis and does **not** assert an Article 9 condition. A candidate for the DPO to confirm is Article 6(1)(f), legitimate interests, for an internal review of the firm's own draft. This file does not choose. The caller confirms both before production use. There is no ATRS mapping. This starter is not a public-sector tool and does not submit a record.

The Python starter does not persist the text. A promotion that is not marked synthetic is refused, and the refusal does not echo the body. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use the non-allocatable National Insurance number fixture documented in Experiment 08. Harbourline Markets Ltd is fictional. Contacts use example.com.

## Prompt injection and stale data

Fixtures include instructions to approve, publish, and set `s21_approver_decision`. The checker records them and does not follow them. `followed` is false. A matching line is not used as evidence that a warning or a route is present. An instruction that appears only when line breaks are removed quarantines the whole text.

A source pin older than the threshold, default 90 days, is stale. Equal to the threshold is not. An as-of date before the pin is also not current. A sentence in the draft does not clear the flag. Stale rows are still returned, with `rely_before_reopen` false.

## Human approval

| Decision | Who |
| --- | --- |
| Sign off the promotion, or refuse to | Section 21 approver |
| Treat a flagged phrase as a breach, or as acceptable | Section 21 approver |
| Rely on a row after a source is marked stale | Section 21 approver |
| Confirm the communication route, including any section 55NA permission | Section 21 approver |
| Publish, schedule, or send the promotion | Section 21 approver. This agent publishes none. |
| Change the lifecycle status of an inventoried agent | Governance owner. Experiment 03. |

Viewing a checklist and re-running it do not need a separate approval. Neither is sign-off.

## Risk register

Assessed 30 October 2026 for this starter, not for a named firm. Residual risk is not all Low. The manifest holds the full rows. The residual risk that a later model treats a complete-looking draft as approved is the one the design refuses in code: `promotion_approved` and `compliance_opinion` stay false, and `compliance_finding` is false on every row.

## Logging and the kill switch

This starter writes no log. Before live use, log who ran it, the promotion id, whether injection or a stale date was flagged, and the later human decision. Do not log the original body.

Turn the Copilot Studio agent off. Stop calling `precheck()`. Remove any Foundry access. Block a later connector in a Power Platform DLP policy.

## Tenant controls named and not configured here

Entra Agent ID, Conditional Access, Power Platform DLP, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights. The product pages for those controls were not opened on 30 October 2026, except the Copilot Studio harness overview and the billing and skills pages named in `docs/harness-comparison.md`. Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access are recorded in Experiment 01 as announced, with availability unverified. This folder did not re-check that announcement.

## Review

30 October 2026. Next review 30 April 2027, and sooner if section 21, section 25, paragraph 26F, article 73ZA, COBS 4.2, or COBS 4.12A changes.

There is no ATRS mapping. A public body that used this pattern would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record.
