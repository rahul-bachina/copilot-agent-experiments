# Security and permissions

Privacy impact assessment assistant, Experiment 19. Catalogue ID L006.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one synthetic project brief and returns a draft data protection impact assessment. It screens recorded answers against UK GDPR Article 35(1) and (3) and the ICO list opened on 28 October 2026. It screens solely automated significant decisions against Articles 22A to 22D. It calls Experiment 08. Autonomy is A1. A privacy officer approves the assessment. A project owner accepts residual risk. The agent cannot execute either step, and it cannot decide that a DPIA is required, decide that prior consultation is required, or send that consultation.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Approve, reject, or sign off a DPIA.
- Accept residual risk.
- Decide that Article 35 requires a DPIA, or that it does not. `dpia_required` stays null.
- Decide that Article 36(1) requires prior consultation, or send that consultation.
- Decide that processing is lawful, or that an Article 22B condition is met. `lawful` stays null.
- Write a production record, including a DPIA register, Dataverse, or SharePoint.
- Infer a screening answer from an inventory or a manifest.
- Treat a disabled regulated-decision tool as meaningful human involvement under Article 22A(1)(a).
- Release redacted text, or describe the Experiment 08 output as anonymised.
- Re-implement Experiment 08.

There is no tool whose side effect is any of the above. `record_external_attestation` updates a copy of the JSON in memory and still does not approve the DPIA. The skills say the agent must not call it. `approve_assessment`, `reject_assessment`, `sign_off_assessment`, `accept_residual_risk`, `send_prior_consultation`, and `write_production_record` raise `AssessmentForbidden`. `tests/test_assess_safety.py` checks that an instruction inside a brief does not become an action.

## Data

**Read, in this starter.** The one brief the team supplies. An optional Experiment 03 inventory JSON. An optional permissions manifest. The as-of date. The static quotations in `src/sources.py`. Experiment 08, called in-process.

**Not read.** A live DPIA register, the Commission or ICO inbox, mailboxes, and the Experiment 08 reversible token vault.

Brief text may contain UK identifiers, and a project may describe special category data. The manifest does **not** assert a UK GDPR lawful basis and does **not** assert an Article 9 condition. The caller confirms both before production use. A basis string copied from a brief or an inventory is a quotation.

The Python starter does not persist the text. The draft stores hashes, closed-list phrases, and the redacted fields. It does not store raw identifier values. A brief that is not marked synthetic is refused, and the refusal does not echo the body. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use the non-allocatable National Insurance fixture documented in Experiment 08. Northwharf Borough Council is fictional.

## Prompt injection and stale sources

Fixtures include instructions hidden in an HTML comment, after a form feed, after blank lines, and between zero-width characters, including instructions to approve the DPIA, skip consultation, or clear a stale flag. The checker records them and does not follow them. `followed` is false. The phrase is removed from the copied section. It remains in `prompt_injection.signals`.

The source pin of 28 October 2026 is stale when the as-of date is more than 90 days later. A sentence in the brief does not clear the flag. The 90-day window is not the review duty in Article 35(11).

## Human approval

| Decision | Who |
| --- | --- |
| Approve the assessment | Privacy officer |
| Accept residual risk | Project owner |
| Decide whether to consult under Article 36(1), and send that consultation if they decide to | Privacy officer. This agent cannot send it. |
| Rely on the screening after the pinned sources are marked stale | Privacy officer |
| Treat text copied from an inventory or a manifest as the team's own answer | Project owner |

Viewing a draft and re-running it do not need a separate approval.

## Risk register

Assessed 28 October 2026 for this starter, not for a named organisation. Residual risk is not all Low. The manifest holds the full rows. The residual risk that a later model treats the draft as anonymised is High, because Experiment 08 does not redact names, email addresses, or telephone numbers, and this draft must not be described as cleaned.

## Logging and the kill switch

This starter writes no log. Before live use, log who ran it, the project id, the checksum, whether injection or a stale pin was flagged, and the later human decision. Do not log raw identifiers.

Turn the Copilot Studio agent off. Stop calling `assess()`. Remove any Foundry access. Block a later connector in a Power Platform DLP policy.

## Tenant controls named and not configured here

Entra Agent ID, Conditional Access, Power Platform DLP, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights. The product pages for those controls were not opened on 28 October 2026, except the Copilot Studio harness overview. Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access are recorded in Experiment 01 as announced, with availability unverified. This folder did not re-check that announcement.

## Review

28 October 2026. Next review 28 April 2027, and sooner if Article 35, Article 36, or Articles 22A to 22D change, or if the ICO withdraws the DPIA pages opened for this starter.

There is no ATRS submission. A public body that used this pattern would consider the Algorithmic Transparency Recording Standard separately. An Experiment 03 inventory can be an input. This starter does not submit a record.
