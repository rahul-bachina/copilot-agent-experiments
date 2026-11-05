# Security and permissions

Underwriting submission summary, Experiment 37. Catalogue ID B006.

This note matches `agent-manifest.yaml`. `permissions.yaml` is the same file. If the note and the manifest disagree, the manifest is the control. It is written for a firm deciding whether to try the starter, not as a completed DPIA and not as an underwriting opinion.

## Purpose

The agent reads one synthetic broker submission and returns an extractive draft. Every stated fact carries a pinpoint citation. A closed-list field with no usable line is `not stated`. Autonomy is A0. The underwriter owns coverage and price. The agent does not accept or decline, does not suggest a price or terms, does not contact the broker, and does not write to an underwriting system.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Accept, decline, or refer a risk. `coverage_decision` stays null.
- Suggest a price or terms. `price_suggested` and `terms_suggested` stay null.
- Contact the broker. `broker_contacted` stays false.
- Write an underwriting system or bind cover.
- Decide that section 3 of the Insurance Act 2015 was met, or apply a section 8 remedy.
- Decide that the Consumer Duty or PRIN 2A was met.
- Recommend autonomy A3.
- Call Microsoft Foundry. `foundry_called` stays false.
- Read a submission that is not marked synthetic.
- Release the smoke test as a model score. `evaluation_released` stays false.

There is no tool whose side effect is any of the above. `schema/tools.json` marks the decision tools as not callable. `record_underwriter_review` is not an agent tool. Tests in `tests/test_prohibited.py` and `tests/test_injection.py` check that submission text does not become a decision.

## Data

**Read, in this starter.** The synthetic submission for that run, including the files Experiment 12 inventories. The as-of date and the pin window. The static source list. Experiment 29's number and date helpers.

**Not read.** An underwriting workbench, a bordereau, a broker mailbox, a rating engine, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane.

The samples in this repository are synthetic. Northfen Wharf Ltd is fictional. It is not an insurer, a syndicate, an MGA, or a broker. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms a basis before any live processing. Live submissions and personal data are outside this starter.

The Python starter does not persist the submission. The draft keeps the copied lines, because those are what was cited. It does not copy unused file bodies into a second store. A file with a deterministic identifier finding is not quoted. `output_is_anonymised` stays false.

## Prompt injection and stale data

The checker reads untrusted document text. The scanner records a line that tells the summariser to ignore instructions, accept or decline, set a price, email the broker, bind, or write the underwriting system. A sentence that already refuses the action is not treated as an injection, unless it also states an affirmative decision. Payload keys that try to set `coverage_decision`, `price_suggested`, `broker_contacted`, or `checker_passed` are stripped and are not echoed. `followed` stays false. Hidden text in an HTML comment, a form feed, trailing blank lines, or zero-width characters is recorded and is not copied into a fact.

The stale-data test compares `last_verified` (5 November 2026 for the pages this experiment opened) with the as-of date. Older than the threshold, default 90 days, is stale. The day the window ends is still current. Document dates use the same window, via Experiment 12 for the file date and via the document `reviewed_on` for the lines. The catalogue-boundary row is not a web page and is not stale-tested. Pages that were not opened are not stale-tested. The checker does not download the page. When a pin is stale, or a stale file is in the submission, `do_not_rely` is true. The draft is still produced. It is still not a decision.

The 90-day window is not a statutory period and not a Lloyd's deadline. A Lloyd's byelaw was not opened.

The residual risk is omission. A verbatim quote of the cited lines can leave out a later line that changes the risk. Residual risk R3 in the manifest stays High for that reason. The underwriter is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A0 means this starter cannot decide coverage or price even after a person agrees. The person still has to make any decision outside the tool.

| Decision | Who |
|---|---|
| Review every cited fact | Underwriter |
| Decide whether to ask the broker about a gap | Underwriter, outside this agent |
| Decide coverage | Underwriter, outside this agent |
| Set price and terms | Underwriter, outside this agent |
| Write the underwriting system or bind cover | Underwriter, outside this agent |
| Re-open a pinned page before relying on a legal note | Underwriter |
| Confirm a lawful basis before any live processing | Data protection officer |
| Deploy, publish, or turn a flow on | Outside this agent |

Producing the draft does not need a separate approval.

A request for autonomy A3 is refused. It is never the recommendation. `a3_recommended` stays false.

## Law notes, opened 5 November 2026

These are limits on what this starter may say. They are not a legal opinion.

- Insurance Act 2015 section 2(1): Part 2 applies to non-consumer insurance contracts only. Section 1 defines that term by reference to the Consumer Insurance (Disclosure and Representations) Act 2012. That Act was not opened.
- Section 3 is the duty of fair presentation, including section 3(4) and section 3(5). This starter does not decide that a presentation was fair and does not make the further enquiries in section 3(4)(b).
- Section 5 is what the insurer knows, ought to know, or is presumed to know, for section 3(5)(b) to (d). This starter does not decide what the insurer knows.
- Section 8 is the insurer's remedy. Schedule 1 was not opened. No remedy is applied.
- PRIN 2A.1 says the Consumer Duty applies to a firm's retail market business. PRIN 2A.2 states the three cross-cutting obligations and says they exhaust Principle 12. PRIN 3 and FG22/5 were not opened. This starter does not decide that a firm met the Duty. A label other than `retail` does not have PRIN 2A applied to it by this starter.
- UK GDPR Article 5 was read, including data minimisation and accuracy. Article 22 was shown as omitted. Article 22A(1) defines a solely automated decision as one with no meaningful human involvement, and a significant decision as one with a legal effect or a similarly significant effect. This starter does not quote a pre-substitution Article 22 as current law, and it does not certify meaningful human involvement.

## Controls a tenant would discuss

This starter configures none of them. None of these product pages was opened for this experiment, except the Copilot Studio harness overview and the generative-orchestration guidance, which are cited in the harness notes. Each row below is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Entra Agent ID | Not configured | Unverified. |
| Conditional Access | Not configured | Unverified. |
| Data loss prevention | Not configured | Unverified. |
| Microsoft Foundry prompt shields | Not called | Unverified. The product page was not opened. |
| Key Vault | Not used | Unverified. This starter has no secret to store. |
| Microsoft Purview | Not configured | Unverified. |
| Application Insights | Not configured | Unverified. The starter writes no log. |
| Customer Conversation harness | Not built | Described on the harness overview for voice and chat. A submission does not belong on a public chat. |

## Identity

The local command has no Entra sign-in. A later host would name the underwriter. This file does not.
