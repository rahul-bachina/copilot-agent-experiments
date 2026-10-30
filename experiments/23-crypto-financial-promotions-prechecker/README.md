# Experiment 23: Cryptoasset financial promotions pre-checker

Catalogue ID **UK08**. Related to, and kept separate from, the generic brand-compliance row R006. A follow-on for the same kind of buyer as [Experiment 04](../04-fca-cryptoasset-readiness/) (UK02, FCA cryptoasset authorisation readiness). Free-text copy goes through [Experiment 08](../08-uk-pii-redaction-gateway/) (O005, UK identifier PII gateway) before any excerpt is stored. A request to change an inventory lifecycle status is handed to [Experiment 03](../03-agent-inventory-atrs-assurance/) (G010) and is not applied.

A marketing team has a draft web page, social post, or app screen for a cryptoasset. A compliance reviewer still has to read it against the financial promotion rules before anyone communicates it. This starter prepares that reading. It returns a draft checklist. The section 21 approver signs off.

**Autonomy A0.** The agent does not approve a promotion, does not publish one, and does not give a compliance opinion. `s21_approver_decision` stays null. Nothing is rewritten into replacement copy. A rewrite would be another promotion, and this agent does not draft one.

Stack in the catalogue: Copilot Studio, Microsoft Foundry, and Power Platform. The checklist is Python in the standard library, so a reviewer can run it without a tenant. Foundry is not called. Power Platform is the place a firm might later put the approval step. This starter does not create a flow in a tenant.

The firm in the samples is Harbourline Markets Ltd, the invented firm from Experiment 04.

## The problem

[Section 21(1)](https://www.legislation.gov.uk/ukpga/2000/8/section/21) of the Financial Services and Markets Act 2000 says a person must not, in the course of business, communicate an invitation or inducement to engage in investment activity, or to engage in claims management activity. Subsection (2) says that does not apply if the person is an authorised person, or if the content is approved for the purposes of that section by an authorised person. Subsection (2A) says the content may be approved only if the approval is permitted under section 55NA, or falls within an exemption under section 55NB. Subsection (13) says "communicate" includes causing a communication to be made. Subsection (14) says "investment" includes any asset, right or interest, including where an asset, right or interest is, or comprises or represents, a cryptoasset.

The section 21 page, opened 30 October 2026, says it is up to date with all changes known to be in force on or before 25 October 2026, and that there are changes that may be brought into force at a future date. Sections 55NA and 55NB were named and not opened. This checker does not decide that an approver has permission.

[Section 25(1)](https://www.legislation.gov.uk/ukpga/2000/8/section/25) says a person who contravenes section 21(1) is guilty of an offence and liable, on conviction on indictment, to imprisonment for a term not exceeding two years or a fine, or both. The FCA marketing page uses the same maximum. This checker does not decide that an offence would be committed. Section 25(2) is a defence. It is not applied here.

[Paragraph 26F](https://www.legislation.gov.uk/uksi/2005/1529/schedule/1/paragraph/26F) of Schedule 1 to the Financial Services and Markets Act 2000 (Financial Promotion) Order 2005, as displayed on 30 October 2026, defines a qualifying cryptoasset. The page says the paragraph was substituted by the Financial Services and Markets Act 2000 (Cryptoassets) Regulations 2026, with a note "25 February 2026 for specified purposes, otherwise prospective." This checker does not decide whether that substitution is the text in force for a given draft, and it does not decide that a product is a qualifying cryptoasset.

[Article 73ZA](https://www.legislation.gov.uk/uksi/2023/612/article/7/made) was opened as originally made in the Financial Services and Markets Act 2000 (Financial Promotion) (Amendment) Order 2023. It says the financial promotion restriction does not apply to a communication which relates only to one or more qualifying cryptoassets and which is communicated by a registered person, or on behalf of a registered person where the communication is non-real time and that person prepared the content. The revised article on the 2005 Order was not opened. A "registered person" in that article is an MLR cryptoasset exchange provider or custodian wallet provider on the FCA register, and not an authorised person. This checker does not decide that a firm is on that register.

The FCA page [Cryptoasset firms marketing to UK consumers](https://www.fca.org.uk/firms/cryptoassets/marketing-uk-consumers), first published 8 June 2023 and last updated 6 February 2026, says the regime applies from 8 October 2023 and lists four routes: an FCA authorised person communicates the promotion; an unauthorised person has it approved by an authorised person; an MLR-registered cryptoasset business communicates it; or the promotion complies with an exemption in the Financial Promotion Order. The same page still says legislation on a regulatory gateway for approvers was making its way through Parliament. Section 21(2A), on the legislation.gov.uk text opened the same day, is already in the revised section, with a commencement note of 7 February 2024 in so far as not already in force. This checker records both sentences. It does not choose between them. Experiment 04 pinned the same marketing-page sentence on 24 October 2026 and did not overwrite it. This experiment does not overwrite it either.

[COBS 4.2.1R](https://www.handbook.fca.org.uk/handbook/COBS/4/2.html), opened 30 October 2026, last updated on that site on 23 October 2025, says a firm must ensure that a communication or a financial promotion is fair, clear and not misleading. COBS 4.2.5G says a communication or a financial promotion should not describe a feature as "guaranteed", "protected" or "secure", or use a similar term, unless that term is capable of being fair, clear and not misleading and the firm communicates the information necessary to make the use of the term fair, clear and not misleading. The checker flags the words. It does not decide that the term fails that test.

[COBS 4.12A](https://www.handbook.fca.org.uk/handbook/COBS/4/12A.html), opened the same day, last updated on that site on 23 October 2025, with a future version dated 25 October 2027 which was not opened:

- COBS 4.12A.7R says a firm must not communicate or approve a financial promotion which relates to a restricted mass market investment and which offers to a retail client any monetary or non-monetary incentive, subject to the conditions in that rule. The examples on that page, cited there as COBS 4.12A.8G, include bonuses when investing, bonuses where the client refers another person, cashback, volume-linked fee discounts, free gifts such as laptops or mobile telephones, and additional free investments or discounts on investments. Paragraph (3) of the rule does not list qualifying cryptoassets. Paragraph (4) is a transfer-only condition. This checker does not decide that either condition is met.
- COBS 4.12A.11R(1)(d) sets this risk warning where the promotion relates to one or more qualifying cryptoassets or UK RIE cryptoasset exchange traded notes: "Don't invest unless you're prepared to lose all the money you invest. This is a high-risk investment and you should not expect to be protected if something goes wrong." COBS 4.12A.11R(2)(a) sets a shorter warning where a third-party marketing provider's character limit is exceeded. This checker cannot see that limit.
- COBS 4.12A.11R(3) requires, for a website, mobile application or other digital medium, a link in the form "Take 2 mins to learn more" to a risk summary selected from COBS 4 Annex 1R, with the exceptions in (3)(b). Annex 1R was not opened. The summary text is not checked. Prominence rules COBS 4.12A.36R and COBS 4.12A.38R were named and not opened.
- COBS 4.12A.15R restricts a direct offer financial promotion unless the conditions in COBS 4.12A.18R (at least 24 hours' cooling off), COBS 4.12A.20R (personalised risk warning), COBS 4.12A.21R (categorisation) and COBS 4.12A.28R (appropriateness) are satisfied. The personalised warning in COBS 4.12A.20R(1)(b) is: "[Client name], this is a high-risk investment. How would you feel if you lost the money you're about to invest? Take 2 mins to learn more." COBS 4.12A.28R(1)(d) names a person who will transact in a qualifying cryptoasset. The glossary definition of "direct offer financial promotion" was not opened. The checker does not decide that a draft is one. COBS 10 and COBS 10A were named and not opened.

An FCA freedom-of-information release dated 20 February 2026 (FOI2026/00006) says that for 1 January to 31 December 2025 the FCA issued 1,528 alerts with respect to unauthorised crypto entities and promotions, out of 2,329 alerts in total. That figure is context. It is not an input to the checker.

PS23/6 and FG23/3 are named on the marketing page and were not opened. GC23/2 is still described there as a guidance consultation and was not opened.

## Non-goals

- Approving, rejecting, or signing off a financial promotion.
- Publishing, scheduling, or sending a promotion, including to a website, an app store, or a social network.
- Drafting replacement or "compliant" copy.
- Deciding that section 21 applies, that an exemption applies, that article 73ZA applies, or that an offence would be committed.
- Deciding that a person has section 55NA permission, or that section 21(2A) has overtaken the sentence still on the marketing page.
- Deciding that a cryptoasset is a qualifying cryptoasset under paragraph 26F, or that the February 2026 substitution is in force for the draft.
- Deciding that COBS 4.12A.7R(3) or (4), or COBS 4.12A.11R(5), is satisfied.
- Deciding that a draft is a direct offer financial promotion, or that a client has already had a cooling-off period.
- Checking prominence, the COBS 4 Annex 1R risk summary, or COBS 10 appropriateness questions. Those texts were not opened.
- Giving legal, regulatory, or compliance advice, or a view that the firm has met the Consumer Duty. The Consumer Duty sourcebook was not opened for this experiment.
- Reading fca.org.uk or legislation.gov.uk at run time.
- Writing a production approvals register.

## What was opened

Opened on 30 October 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [FSMA 2000 s.21](https://www.legislation.gov.uk/ukpga/2000/8/section/21) | The restriction, the two routes in subsection (2), subsection (2A) on approval, "communicate", and the cryptoasset words in subsection (14). Up to date with changes known to be in force on or before 25 October 2026. |
| [FSMA 2000 s.25](https://www.legislation.gov.uk/ukpga/2000/8/section/25) | The offence for contravening section 21(1), including the two-year maximum on indictment. Not applied to any draft. |
| [FPO Schedule 1, paragraph 26F](https://www.legislation.gov.uk/uksi/2005/1529/schedule/1/paragraph/26F) | The qualifying-cryptoasset definition as displayed, including the substitution note. |
| [SI 2023/612, article 7](https://www.legislation.gov.uk/uksi/2023/612/article/7/made) | Article 73ZA as originally made. |
| [FCA marketing page](https://www.fca.org.uk/firms/cryptoassets/marketing-uk-consumers) | Four routes, 8 October 2023, risk warnings, a 24-hour cooling-off period, and the gateway sentence that is still on the page. Last updated 6 February 2026. |
| [COBS 4.2](https://www.handbook.fca.org.uk/handbook/COBS/4/2.html) | COBS 4.2.1R and COBS 4.2.5G. Last updated on that site 23 October 2025. |
| [COBS 4.12A](https://www.handbook.fca.org.uk/handbook/COBS/4/12A.html) | The incentive rule, the cryptoasset risk warning, the digital-medium link, and the four direct-offer conditions. Same Handbook date. Future version 25 October 2027 not opened. |
| [FCA FOI2026/00006](https://www.fca.org.uk/freedom-information/information-crypto-related-alerts-february-2026) | 1,528 and 2,329. Context only. |
| [Copilot Studio harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | See [docs/harness-comparison.md](docs/harness-comparison.md). |

## What the draft does

`src/precheck.py` reads one JSON promotion and writes one JSON document. The same text and the same as-of date produce the same JSON. `promotion_approved`, `published`, and `compliance_opinion` are false. `s21_approver_decision` is null. `actions_taken` is empty. `rewrite_drafted` is false.

Each checklist row is an observation about text. `compliance_finding` is false on every row. A row can say a phrase was present, not found, or flagged for the approver. None of those words is a pass or a fail.

Lines that tell the checker to approve, publish, or ignore its instructions are recorded and are not used as evidence. If that instruction only appears once line breaks are removed, the whole text is quarantined and no phrase is treated as present.

The body stored for the reviewer is the redacted text from Experiment 08. `output_is_anonymised` stays false. The original is not copied into the result. A record that is not marked synthetic is refused. The refusal does not echo the body.

Where the caller attaches an inventory record and an untrusted control asks for a lifecycle status, Experiment 03's `propose_status_change` and `apply_status_change` are called with no approval. The status is not applied. Experiment 03's manifest generator is called only when PyYAML and jsonschema can be imported. This experiment's tests do not install those packages. The generator is never asked to mark a manifest approved.

Experiment 04's marketing-page pin is read. Its gap register is not run.

A source is stale when the as-of date is more than 90 days after 30 October 2026. Equal to 90 days is not stale. A stale row is still returned, and it says not to rely on it until a person has re-opened the page.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 03, 04, and 08 need to be beside this folder.

```bash
cd experiments/23-crypto-financial-promotions-prechecker
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/precheck.py --input examples/sample_web.json --as-of 2026-10-30
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

The exit code is 0 when a checklist is produced. A refusal of a record that is not marked synthetic is exit code 2, and the body is not printed.

## Limitations

- A checklist is not a compliance opinion and it is not an approval.
- Phrase matching misses paraphrase, images, and video. No image was opened. Foundry vision is not used.
- The Handbook page shows a future version on 25 October 2027. That version was not opened. COBS 4.12A.11R(5) tells a firm to omit the words "and you are unlikely to be protected if something goes wrong" from the warning in (1)(d) when its conditions are met. The warning in (1)(d) uses different words ("you should not expect to be protected"). This checker does not reconcile that. It does not delete words from a draft.
- Paragraph 26F's substitution is marked prospective except for specified purposes. Those purposes were not opened.
- Article 73ZA was read as originally made. A later consolidation was not opened.
- The marketing page and section 21(2A) are both recorded. The checker does not decide which sentence a firm should follow.
- The first-occasion exceptions in the Handbook (cooling off and the personalised warning are not required every time) need the client's history. This checker cannot see it.
- Prominence, the Annex 1R risk summary, and the COBS 10 questions were not opened, so they are not checked.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).

This is not legal advice and it is not a statement of any firm's compliance.

## Two Copilot Studio harnesses

Both call `src/precheck.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness approves, publishes, or rewrites. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The reviewer pastes a draft, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the same JSON. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- Experiment 04, the authorisation-readiness pack and the marketing-page pin: [../04-fca-cryptoasset-readiness/](../04-fca-cryptoasset-readiness/).
- Experiment 08, the identifier gateway: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- Experiment 03, the lifecycle proposal this draft can call: [../03-agent-inventory-atrs-assurance/](../03-agent-inventory-atrs-assurance/).

## Project structure

```
experiments/23-crypto-financial-promotions-prechecker/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── copilot-studio/
├── skills/
├── schema/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 30 October 2026

- [Financial Services and Markets Act 2000, section 21](https://www.legislation.gov.uk/ukpga/2000/8/section/21)
- [Financial Services and Markets Act 2000, section 25](https://www.legislation.gov.uk/ukpga/2000/8/section/25)
- [Financial Promotion Order 2005, Schedule 1, paragraph 26F](https://www.legislation.gov.uk/uksi/2005/1529/schedule/1/paragraph/26F)
- [Financial Promotion (Amendment) Order 2023, article 7 (article 73ZA as made)](https://www.legislation.gov.uk/uksi/2023/612/article/7/made)
- [FCA, cryptoasset firms marketing to UK consumers](https://www.fca.org.uk/firms/cryptoassets/marketing-uk-consumers)
- [FCA Handbook, COBS 4.2](https://www.handbook.fca.org.uk/handbook/COBS/4/2.html)
- [FCA Handbook, COBS 4.12A](https://www.handbook.fca.org.uk/handbook/COBS/4/12A.html)
- [FCA, FOI2026/00006](https://www.fca.org.uk/freedom-information/information-crypto-related-alerts-february-2026)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
