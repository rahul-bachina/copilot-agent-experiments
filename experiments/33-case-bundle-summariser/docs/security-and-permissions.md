# Security and permissions

Evidence and case-bundle summariser, Experiment 33. Catalogue ID UK09.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a penetration test.

## Purpose

The agent reads one synthetic case bundle and returns an extractive draft. Every sentence carries a pinpoint citation. A deterministic checker fails a sentence whose cited span does not contain it, or that has no citation. Autonomy is A0. The decision-maker reviews every cited sentence. The agent does not recommend an outcome, make a disclosure decision, or make a credibility finding.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Recommend an outcome. `case_outcome` stays null. `outcome_recommended` stays false.
- Make a disclosure decision. `disclosure_decision` stays null. Nothing is disclosed.
- Make a credibility finding. `credibility_finding` stays null.
- Accept the summary as a decision. On the agent path, `summary_accepted_as_reading_aid` stays false.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This starter stays at A0.
- Call Microsoft Foundry. `foundry_called` stays false.
- Write a production record or send a message.
- Read a bundle that is not marked synthetic.
- Quote a price or look up a licence in an admin centre.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. `schema/tools.json` marks `recommend_outcome`, `decide_disclosure`, `find_credibility`, `accept_summary`, `send_external`, and `write_production_record` as not callable. `record_sentence_review` is not an agent tool. Tests in `tests/test_prohibited.py` and `tests/test_injection.py` check that bundle text does not become an outcome or a disclosure.

## Data

**Read, in this starter.** The synthetic bundle for that run. The as-of date and the pin window. The static source list.

**Not read.** A case system, a disclosure schedule, a mailbox, a Teams chat, a production agent, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane.

The samples in this repository are synthetic. Reedfen Constabulary, Northfen Casework Unit, and Example Barring Desk are fictional. They are not a police force, the Home Office, or the Disclosure and Barring Service. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms a lawful basis before any live processing. Live cases and personal data are outside this starter.

The Python starter does not persist the bundle. The draft keeps the copied sentences, because those are what was cited, and the document ids, pages, paragraphs, and lines. It does not copy unused document bodies into a second store.

## Prompt injection and stale data

The checker is itself a reader of untrusted document text. The scanner records a line that tells the summariser to ignore instructions, recommend an outcome, disclose material, or find a person credible. A sentence that already refuses the action is not treated as an injection, unless it also matches an affirmative decision pattern. Payload keys that try to set `case_outcome`, `disclosure_decision`, `credibility_finding`, `checker_passed`, or `proposed_sentences` are stripped and are not echoed. `followed` stays false. Hidden text in an HTML comment, a form feed, trailing blank lines, or zero-width characters is recorded and is not copied into the reading.

The stale-data test compares `last_verified` (4 November 2026 for the pages this experiment opened) with the as-of date. Older than the threshold, default 90 days, is stale. The day the window ends is still current. Document review dates use the same window. A document whose status is not current, or that names a successor, is not quoted. The catalogue-boundary row is not a web page and is not stale-tested. The checker does not download the page and does not rewrite the review date. When a pin is stale, or a stale or superseded document is in the bundle, `do_not_rely` is true. The draft is still produced. It is still not a decision.

The residual risk is omission. A verbatim quote of the cited lines can leave out a later line that changes the reading. Residual risk R3 in the manifest stays High for that reason. The decision-maker is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A0 means this starter cannot decide a case even after a person agrees. The person still has to make any decision outside the tool.

| Decision | Who |
|---|---|
| Review every cited sentence | Decision-maker |
| Decide any case outcome | Decision-maker, outside this agent |
| Make a disclosure decision | Decision-maker, outside this agent |
| Make a credibility finding | Decision-maker, outside this agent |
| Re-open a pinned page before relying on a legal note | Decision-maker |
| Confirm a lawful basis before any live processing | Data protection officer |
| Deploy, publish, or turn a flow on | Outside this agent |

Producing the draft and printing the sources table do not need a separate approval.

A request for autonomy A3 is refused. It is never the recommendation. `a3_recommended` stays false.

## Law notes, opened 4 November 2026

These are limits on what this starter may say. They are not a legal opinion.

- UK GDPR Article 22, on legislation.gov.uk, showed the article omitted. Chapter 3 Section 4A was substituted by the Data (Use and Access) Act 2025, section 80(1). Article 22A(1) defines a decision based solely on automated processing as one with no meaningful human involvement, and a significant decision as one that produces a legal effect or a similarly significant effect. This starter does not quote a pre-substitution Article 22, and it does not certify meaningful human involvement. It only refuses to take the decision.
- Data Protection Act 2018 section 14 showed as omitted from 5 February 2026. This starter does not quote the old section 14 safeguards as current law. Section 80(3) of the 2025 Act substitutes sections 50A to 50D for law-enforcement processing. Those sections were not applied here.
- Criminal Procedure and Investigations Act 1996 section 3(1) is the prosecutor's duty to disclose prosecution material which might reasonably be considered capable of undermining the prosecution case or of assisting the accused, or to give a written statement that there is none. This starter does not apply that test. The Part II Code of Practice was not opened. Police disclosure duties under that code are unverified.
- The Algorithmic Transparency Recording Standard policy, gov.uk, published 17 December 2024, was opened. It does not decide whether this starter is in scope. This starter does not publish a record.
- The Home Office asylum case summarisation evaluation and the GOV.UK disclosure news of 14 July 2026 were opened as context. Their figures are theirs. This starter does not repeat them as its own results, and it is not those pilots. The DBS barring summary tool's ATRS record was opened as context. This starter is not that tool.

## Controls a tenant would discuss

This starter configures none of them. None of these product pages was opened for this experiment. Each row is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Foundry, including Document Intelligence, Azure AI Search, and the groundedness evaluator | Not called | Unverified. The product page was not opened for this experiment. UK region availability is unverified. |
| Microsoft Foundry prompt shields | Not called | Unverified. That page was not opened for this experiment. |
| Microsoft Entra Agent ID | Not configured | Unverified. Not opened for this experiment. |
| Conditional Access | Not configured | Unverified. Not opened for this experiment. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this experiment. A later connector that can send or write would need a policy the organisation writes. |
| Key Vault | Not provisioned | Unverified. Not opened. The checker has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of any later draft is the organisation's. |
| Application Insights | Not configured | Unverified. Not opened. This starter writes no log. |

## Logging

This starter writes the JSON to standard output when the command line is used. It does not write a log store. A tenant that later wraps the script should decide retention outside this folder. Do not log a real case into this repository.
