# Experiment 22: On-chain monitoring alert investigator and SAR narrative drafter

Catalogue ID **UK07**. A follow-on for the same kind of buyer as [Experiment 04](../04-fca-cryptoasset-readiness/) (UK02, FCA cryptoasset authorisation readiness), [Experiment 10](../10-travel-rule-exception-triage/) (UK05, Travel Rule exception triage), and [Experiment 16](../16-kyc-evidence-intake/) (B004, KYC evidence intake). Free-text notes go through [Experiment 08](../08-uk-pii-redaction-gateway/) (O005, UK identifier PII gateway) before they are repeated in the draft.

A blockchain-analytics tool raises an alert. An analyst still has to put the hops, the customer file, and any Travel Rule exception into one timeline, and the nominated officer still has to decide whether a disclosure is required. This starter prepares that reading. It drafts an internal investigation note and a suspicious activity report narrative. The MLRO, or the nominated officer, decides whether to file.

**Autonomy A1.** Nothing is filed with the National Crime Agency. No defence against money laundering is requested. No wallet is frozen and no cryptoasset is moved. The agent does not draft customer-facing content about a suspicion, a disclosure, or an investigation. That boundary is [Proceeds of Crime Act 2002, section 333A](https://www.legislation.gov.uk/ukpga/2002/29/section/333A) (tipping off in the regulated sector), opened on 29 October 2026. The agent does not decide whether an offence would be committed. It does not draft the customer text at all.

Stack in the catalogue: Microsoft Foundry, Microsoft Fabric, and Copilot Studio. The timeline and the narrative are Python in the standard library, so an analyst can run them without a tenant. No chain node is queried. Fabric is described as the place a firm might later hold the alert export. This starter does not connect to it.

The firm in the samples is Harbourline Markets Ltd, the invented firm from Experiment 04. Addresses start with `SYNTH-ADDR-`. Transaction hashes start with `SYNTH-TX-`. Anything else is left out of the narrative.

## The problem

[Regulation 19(4)(d)](https://www.legislation.gov.uk/uksi/2017/692/regulation/19) of the Money Laundering Regulations 2017 says the firm's policies must require anyone who knows or suspects, or has reasonable grounds for knowing or suspecting, that a person is engaged in money laundering or terrorist financing to comply with Part 7 of the Proceeds of Crime Act 2002 or Part 3 of the Terrorism Act 2000. [Regulation 21(3)](https://www.legislation.gov.uk/uksi/2017/692/regulation/21) requires a nominated officer. Regulation 21(5) says that where a disclosure is made to that officer, the officer must consider it in the light of any relevant information available to the firm and determine whether it gives rise to knowledge or suspicion or reasonable grounds for knowledge or suspicion.

[Section 330](https://www.legislation.gov.uk/ukpga/2002/29/section/330) of the Proceeds of Crime Act 2002 is the regulated-sector failure-to-disclose offence. The required disclosure goes to a nominated officer, or to a person authorised for the purposes of that Part by the Director General of the National Crime Agency, as soon as is practicable. [Section 331](https://www.legislation.gov.uk/ukpga/2002/29/section/331) is the offence for a nominated officer in the regulated sector who does not make the required disclosure onward. This starter does not decide that either test is met.

The FCA registration page, opened 29 October 2026 and last updated on that site on 30 June 2026, expects a fiat (off-chain) and a cryptoasset (on-chain) transaction monitoring tool, and the rules and thresholds set in those tools. It says the FCA cannot recommend or endorse any tool. It also expects a SAR policy with a route to the MLRO or nominated officer and externally to the National Crime Agency, and a reference to tipping off and to the circumstances where a Defence Against Money Laundering or a Defence Against Terrorist Financing might be considered. This starter does not configure a monitoring tool and does not request either defence.

## Non-goals

- Filing, submitting, or suppressing a suspicious activity report, including on the NCA SAR Portal.
- Requesting a defence against money laundering or a defence against terrorist financing.
- Deciding that anyone knows or suspects money laundering, or that there are reasonable grounds.
- Deciding that regulation 21(5) is satisfied.
- Drafting a Terrorism Act disclosure. Part 3 of that Act was not opened. A marker on the record is passed through for a person.
- Assigning a SAR glossary code. The glossary list was not opened.
- Drafting or sending any customer-facing wording, including a neutral holding reply.
- Applying the permitted-disclosure exceptions in sections 333B, 333C, or 333D. Those sections were not opened.
- Freezing, restricting, or closing an account or a wallet.
- Moving, returning, or making available a cryptoasset.
- Querying a chain, a node, or a blockchain-analytics vendor.
- Treating a supplied label such as "mixer" as a finding about a real cluster. The label is quoted only when it is already on the synthetic record.
- Converting a cryptoasset price into sterling. The firm supplies `value_gbp`, or the narrative says the sterling figure is absent.
- Re-scoring the Experiment 04 authorisation pack, deciding a Travel Rule hold, or confirming a KYC file.
- Giving legal, regulatory, or sanctions advice.

## What was opened

Opened on 29 October 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [POCA 2002 s.330](https://www.legislation.gov.uk/ukpga/2002/29/section/330) | The regulated-sector conditions, including knowledge or suspicion or reasonable grounds, information that came in the course of a business in the regulated sector, and the required disclosure to a nominated officer or a person authorised by the Director General of the NCA, as soon as is practicable. The page warns that revised legislation on the site may not be fully up to date. No "in force on or before" date was on the extract. |
| [POCA 2002 s.331](https://www.legislation.gov.uk/ukpga/2002/29/section/331) | The nominated officer's onward disclosure. Same page warning. |
| [POCA 2002 s.333A](https://www.legislation.gov.uk/ukpga/2002/29/section/333A) | Tipping off in the regulated sector: disclosing that a disclosure under that Part has been made, or that an investigation is contemplated or being carried out, where the disclosure is likely to prejudice an investigation. Subsections (1) and (3) both require that likelihood. The agent does not decide it. |
| [MLRs 2017 reg. 19](https://www.legislation.gov.uk/uksi/2017/692/regulation/19) | Policies must include internal reporting that points staff to POCA Part 7 or Terrorism Act Part 3, and scrutiny of transactions that are unusually complex or unusually large, an unusual pattern, or without apparent economic or legal purpose. The page says it is up to date with all changes known to be in force on or before 25 October 2026. |
| [MLRs 2017 reg. 21](https://www.legislation.gov.uk/uksi/2017/692/regulation/21) | A nominated officer must be appointed. Regulation 21(5) is the officer's determination. Same "on or before 25 October 2026" banner. |
| [FCA registration expectations](https://www.fca.org.uk/firms/cryptoassets/application-registration) | On-chain and off-chain monitoring tools, rules and thresholds, no FCA endorsement of a tool, and the SAR escalation route. First published 22 March 2023, last updated 30 June 2026. |
| [FCA regime overview](https://www.fca.org.uk/publications/policy-statements/cryptoasset-regime) | Published and last updated 30 June 2026. The MARC paragraph says the FCA has narrowed the on-chain monitoring requirement for large UK qualifying cryptoasset trading platforms. That sentence is about market abuse, not this AML alert. Financial Crime Guide updates are described as a plan to consult. The guide was not opened. |
| [UKFIU, Submitting a SAR, chapter 2](https://www.nationalcrimeagency.gov.uk/who-we-are/publications/775-ukfiu-chapter-2-submitting-a-sar/file) | Version 1.1, December 2025. A reason for suspicion should say who is involved, how, when, and why, and should describe the property. The reason field is limited to 8,000 characters. Glossary codes are chosen in the SAR Portal. This starter assigns none. |
| [Copilot Studio harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses are described: GitHub Copilot, Customer Conversation, and standard. This experiment ships the standard harness and the GitHub Copilot harness. It does not use the Customer Conversation harness. |

Not opened, and not applied: POCA sections 333B, 333C, 333D, 335, 336, 338, 339, 339A, and 342; Terrorism Act 2000 Parts 3 and the tipping-off section 21D; the NCA suspicious-activity-reports HTML page (the fetch timed out); UKFIU chapter 3 on defences; the SAR glossary; the Financial Crime Guide; JMLSG; Schedule 9 to POCA (regulated sector). Experiment 16's regulation 28 pin is reused only by calling that experiment. This starter did not re-open regulation 28.

## What the draft does

`src/investigate.py` reads one JSON case and writes one JSON document. The same case and the same as-of date produce the same JSON. `mlro_decision` is null. `sar_filed`, `nca_contacted`, and `daml_requested` are false. `actions_taken` is empty.

The evidence timeline lists hops and ledger rows whose addresses and hashes match `SYNTH-ADDR-` or `SYNTH-TX-`. A string that looks like a live chain address is omitted and is not copied into the output. Events after the as-of date are listed as not placed. They are not treated as having happened.

Where the case includes a Travel Rule transfer, the draft calls Experiment 10 and keeps the exception categories and whether hold, return, or escalate was proposed. It does not copy the party names, and it does not take the analyst's decision. Where the case includes a KYC file, the draft calls Experiment 16 and keeps whether items are missing. It does not copy that experiment's customer-facing note. An analyst note is passed through Experiment 08. The excerpt in the draft is the redaction proposal. `output_is_anonymised` stays false.

The SAR narrative is written for the nominated officer. It says it is not a disclosure and it has not been submitted. It does not say "we suspect". It does not select a glossary code. If the drafted reason exceeds 8,000 characters it is marked over the UKFIU field limit. The usual cases in this folder are far shorter.

A record that is not marked synthetic is refused. The refusal does not echo the body.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 10, 12, and 16 need to be beside this folder. Experiment 16 will not read a KYC file if Experiment 12 is missing.

```bash
cd experiments/22-onchain-alert-sar-drafter
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/investigate.py --input examples/sample_alert.json --as-of 2026-10-29
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

The exit code is 0 when a draft is produced. A missing customer block is not a failed run, and it is not a decision to file or not to file.

## Limitations

- A timeline is not a finding that money laundering occurred, and it is not a finding that a disclosure is required.
- The core does not see the chain. Later hops are not retrieved.
- It does not decide the section 330 or section 331 test, and it does not apply the statutory defences. Those defences were not encoded.
- Section 333A turns on whether a disclosure is likely to prejudice an investigation. The agent does not make that judgement. It avoids the question by writing nothing for a customer.
- The UKFIU chapter is guidance to reporters. It is not a substitute for the Act. Chapter 3, which covers defences, was not opened. The seven-working-day notice period is mentioned in chapter 2 and is not calculated here.
- The MARC on-chain sentence on the 30 June 2026 overview is not an AML monitoring rule. The Financial Crime Guide consultation named on that page was not checked for a later publication.
- The POCA pages warn that the revised text may not be fully up to date. The MLR pages are pinned to changes known to be in force on or before 25 October 2026, which is before this opening.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).

This is not legal advice and it is not a statement of any firm's compliance.

## Two Copilot Studio harnesses

Both call `src/investigate.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness files, requests a defence, freezes a wallet, or writes to a customer. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The analyst pastes a case, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The Customer Conversation harness is described on the overview opened on 29 October 2026 and is not used. A customer must not chat with this agent.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- Experiment 04, the authorisation-readiness pack: [../04-fca-cryptoasset-readiness/](../04-fca-cryptoasset-readiness/).
- Experiment 10, the Travel Rule checklist this draft can call: [../10-travel-rule-exception-triage/](../10-travel-rule-exception-triage/).
- Experiment 16, the KYC checklist this draft can call: [../16-kyc-evidence-intake/](../16-kyc-evidence-intake/).
- Experiment 08, the identifier gateway: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/22-onchain-alert-sar-drafter/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── investigate.py
│   ├── sources.py
│   ├── injection.py
│   ├── addresses.py
│   ├── customer_guard.py
│   └── reuse.py
├── copilot-studio/
├── skills/
├── schema/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 29 October 2026

- [Proceeds of Crime Act 2002, section 330](https://www.legislation.gov.uk/ukpga/2002/29/section/330)
- [Proceeds of Crime Act 2002, section 331](https://www.legislation.gov.uk/ukpga/2002/29/section/331)
- [Proceeds of Crime Act 2002, section 333A](https://www.legislation.gov.uk/ukpga/2002/29/section/333A)
- [Money Laundering Regulations 2017, regulation 19](https://www.legislation.gov.uk/uksi/2017/692/regulation/19)
- [Money Laundering Regulations 2017, regulation 21](https://www.legislation.gov.uk/uksi/2017/692/regulation/21)
- [FCA, cryptoasset registration expectations](https://www.fca.org.uk/firms/cryptoassets/application-registration)
- [FCA, overview of the cryptoassets regime policy statements](https://www.fca.org.uk/publications/policy-statements/cryptoasset-regime)
- [UKFIU, Submitting a SAR, chapter 2 (December 2025, version 1.1)](https://www.nationalcrimeagency.gov.uk/who-we-are/publications/775-ukfiu-chapter-2-submitting-a-sar/file)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
