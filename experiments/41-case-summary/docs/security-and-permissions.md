# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## What a run may read

One synthetic case history. The as-of date. The static notes in `src/sources.py`. Experiment 08 `propose()`, called in-process. The redacted text is not copied into the draft. `release()` is not called.

The Python starter does not persist the case. A case that is not marked synthetic is refused, and the refusal does not echo the text.

## What a run must not do

Contact the customer. Change a case record. Close a complaint. Offer redress. Decide an outcome. Label a customer as vulnerable. Send. Spend. Call a model. Call the network. Mark its own draft accurate.

`record_accuracy_check` is not an agent tool. The command line does not expose it. If a person records a check, the returned object still does not contact the customer and does not change the record.

## Identity

There is no sign-in check. The representative is whoever can run the command. A name passed to `record_accuracy_check` is a string the caller supplies. It is not an Entra object. This starter does not call Microsoft Entra.

## Platform controls, for a deployment this starter does not perform

These product pages were not opened on 9 November 2026. Treat the names as unverified here.

- **Microsoft Entra Agent ID and Conditional Access.** Not registered. Not verified.
- **Power Platform DLP.** No policy is created. Not verified.
- **Microsoft Foundry prompt shields.** Not called. The product page was not opened. Unverified.
- **Key Vault.** No secret is stored. Not verified.
- **Microsoft Purview.** No label and no DLP policy is created. Not verified.
- **Application Insights.** This starter writes no log. A trace that stored the case text would undo the minimisation. Unverified.

## UK GDPR

Article 5 was read on 9 November 2026. Article 5(1)(c) is data minimisation. Article 5(1)(d) is accuracy. This starter withholds flagged identifiers and leaves stale events out of the extract. It does not erase or rectify a record, and it does not find that Article 5 has been met. Article 5(3) says compatible further processing is not, by itself, lawful. Article 6 was not opened. No lawful basis is chosen.

Article 22 was shown as omitted. Article 22A(1) and (2) were read. Section 80 of the Data (Use and Access) Act 2025 was read, including the substituted text of Articles 22B, 22C, and 22D. This starter does not take a significant decision and does not certify meaningful human involvement. Article 22D regulations were not opened. S.I. 2026/82 was not opened. Article 9 was not opened. No special-category condition is asserted.

The ICO page on accuracy and statistical accuracy was requested and returned HTTP 403. It is not quoted. Unverified.

## Logging

This starter writes no log. Before live use, log the case id rather than the words, the as-of date, the sentence count, whether an instruction or a stale pin was flagged, and the Experiment 08 finding count and input hash. Do not log the case text or a raw identifier.

## Risk

Assessed 9 November 2026 for this starter, not for a named organisation. Residual risk is not all Low. The residual risk that a verbatim sentence misleads by omission is High. The residual risk that a later log stores a name Experiment 08 does not redact is High. The manifest holds the rows.

## Kill switch

Do not run the command. There is no published agent to switch off.

## Review

Last reviewed 9 November 2026. Next review 9 May 2027, and sooner if a pinned page is re-opened and has changed.
