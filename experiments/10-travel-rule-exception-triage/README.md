# Experiment 10: Travel Rule exception triage

Catalogue ID **UK05**. A follow-on to [Experiment 04](../04-fca-cryptoasset-readiness/) (UK02, FCA cryptoasset authorisation readiness) for the same kind of buyer.

UK cryptoasset businesses have had to collect, verify, and share information on cryptoasset transfers since 1 September 2023. The awkward cases are the ones with a missing field, a name that does not match the firm's own customer record, or a counterparty in a jurisdiction that has not implemented the Travel Rule. The industry, and the JMLSG annex opened for this starter, calls that last situation the sunrise issue. The FCA statement does not use the word sunrise. It says "a jurisdiction without the Travel Rule".

**Autonomy A1.** The agent triages one transfer and proposes hold, return, or escalate, with reasons. An analyst decides. The agent does not hold, return, reject, or release a transfer. It does not file a suspicious activity report. It does not contact a counterparty.

Stack in the catalogue: Power Platform, Microsoft Foundry, and Copilot Studio. The checklist itself is Python in the standard library, so an analyst can run it without a tenant.

The firm in the samples is Harbourline Markets Ltd, the invented firm from Experiment 04. Counterparties, jurisdictions, and wallet strings are synthetic and labelled as such.

## The problem

Part 7A of the Money Laundering, Terrorist Financing and Transfer of Funds (Information on the Payer) Regulations 2017 requires specified information to accompany an inter-cryptoasset business transfer, and it tells the beneficiary's cryptoasset business what to do when that information is missing or does not correspond. It does not tell a piece of software to take the decision.

An analyst still has to see which limb applies, which field is absent, and which of the statutory options is even in play. This starter prepares that reading.

## Non-goals

- Holding, delaying, returning, rejecting, or releasing a transfer.
- Making a cryptoasset available to a beneficiary.
- Sending a Travel Rule message, or contacting a counterparty, a customer, the FCA, or law enforcement.
- Filing, drafting, or suppressing a suspicious activity report. The narrative drafter is a different catalogue item (UK07).
- Reporting repeated failure to the FCA under regulation 64D(5) or 64E(5).
- Deciding that the firm has breached the Money Laundering Regulations.
- Confirming that regulation 64A takes a transfer outside Part 7A.
- Converting a cryptoasset into sterling or into euros. The firm supplies a sterling figure, or the threshold is not applied.
- Deciding that two transfers are linked.
- Treating the FCA statement on jurisdictions without the Travel Rule as a waiver of regulation 64D.
- Using the August 2023 JMLSG figure of €1,000 as the operative threshold. The revised regulation says £800.
- Re-scoring the Experiment 04 authorisation pack.
- Giving legal, regulatory, or sanctions advice.

## What was opened

Opened on 26 October 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [MLRs Part 7A](https://www.legislation.gov.uk/uksi/2017/692/part/7A) | Regulations 64A to 64H, as revised. The page says it is up to date with all changes known to be in force on or before 25 October 2026. |
| [SI 2022/860](https://www.legislation.gov.uk/uksi/2022/860/introduction), made 21 July 2022 by the Treasury | Regulation 1(3): regulation 5 (cryptoasset transfers) comes into force on 1 September 2023. The Part 7A annotation says the Part was inserted then by regs 1(3) and 5(5). |
| [SI 2026/621 regulation 32](https://www.legislation.gov.uk/uksi/2026/621/regulation/32) | In regulation 64C(4), "1,000 euros" is replaced with "£800". The Part 7A annotation dates that substitution, and the same substitution in regulation 64G(1)(b), at 30 June 2026. |
| [FCA Travel Rule statement](https://www.fca.org.uk/news/statements/fca-sets-out-expectations-uk-cryptoasset-businesses-complying-travel-rule) | First published 17 August 2023, last updated 6 February 2026. Sunrise sending and receiving expectations. Firms remain responsible when they use a supplier. |
| [JMLSG Sector 22 Annex I](https://www.jmlsg.org.uk/wp-content/uploads/2023/08/Board-approved_JMLSG-Guidance_Part-II-Sector-22-Annex-I_Aug2023.pdf) (August 2023) | Uses "sunrise issue" at paragraph 10 and points firms to FCA communications. Paragraphs 13 and 45 still say €1,000. That figure is not used. |
| [JMLSG revisions](https://www.jmlsg.org.uk/revisions/) | The August 2023 annex is still the annex listed. The September 2026 revisions on that page are Part I paragraphs, not a new Annex I. |
| [JMLSG ministerial approval note](https://www.jmlsg.org.uk/latest-news/ministerial-approval-of-jmlsg-guidance-6/) | Says HM Treasury has approved Sector 22 including Annex 1. The fetched page showed no date. The date is unverified. |

Regulation 14A (the definition of a cryptoasset business) was not opened. JMLSG paragraph 1 cites it. This starter does not restate that definition.

## What the checklist does

`src/triage.py` reads one JSON record and writes one JSON document. The same record and the same as-of date produce the same JSON. `analyst_decision` is null. `actions_taken` is empty.

**Information that must accompany an inter-cryptoasset business transfer.** Regulation 64C(5): the name of the originator and of the beneficiary; if either is a firm, the registered name or, if none, the trading name; the account number of each, or a unique transaction identifier where there is no account number.

**Further originator information.** Regulation 64C(6). It must accompany the transfer when regulation 64C(3) does not apply (not every executing cryptoasset business is carrying on business in the United Kingdom) and the transfer, taken together with any other that appears to be linked, is equal to or exceeds the equivalent of £800. Where every executing business is in the United Kingdom, that further information is not required to accompany the transfer unless the beneficiary's business requests it, in which case regulation 64C(2) gives the originator's business three working days. This core states that rule. It does not calculate the day. "Working day" in regulation 64B covers a bank holiday in any part of the United Kingdom, and that calendar is not encoded.

**If the firm has not supplied a sterling equivalent, or has not said that linkage was assessed, the £800 limb is not applied.** The core does not assume the transfer is over or under.

**Beneficiary, before making the cryptoasset available.** Regulation 64D(1): check that the required information arrived, and that the beneficiary information corresponds with information verified under Part 3. This core compares the beneficiary name on the transfer with the Part 3 name the analyst typed, ignoring case and extra spaces. It does not fuzzy-match. JMLSG paragraph 24 says a truncated name can have a reasonable explanation. That is left to the analyst. A mismatch is not cleared by the core.

**If something is missing or does not correspond.** Regulation 64D(2) requires the firm to request the missing information, to consider enquiries, and to consider whether to delay making the cryptoasset available and, if the gap is not resolved within a reasonable time, to return it. "Reasonable time" is not defined in the text opened. No number of days is invented. The core proposes hold (the delay limb) and return, and lists the request as a step for a person. It does not send the request.

**Intermediary.** Regulation 64E has the request, delay, and return considerations, and does not contain the Part 3 correspondence limb. Regulation 64F requires information to travel onward. The core does not send it.

**Unhosted wallet.** Regulation 64G(1) says the business may request information. Regulation 64G(4) says that if it does request and does not receive the information, it must not make the cryptoasset available. The core does not decide the "may". If the record says a request was made and not answered, hold is proposed and return is not, because 64G as opened has no return limb.

**Sunrise.** When the firm's register says the counterparty jurisdiction does not have the Travel Rule, and that record is inside the stale threshold, the core cites the FCA statement. On a send, the firm must still collect and verify, and should store the information before making the transfer, if the counterparty cannot receive it. On a receipt with missing or incomplete information, the firm takes that status into account in a risk-based assessment of whether to make the cryptoassets available. The core does not treat the statement as a waiver of regulation 64D. A register entry older than the threshold, default 90 days, is not relied on.

**Out of scope only if an analyst confirms it.** Regulation 64A(2) and 64A(3) are flagged when the record asserts them. The core does not confirm them and does not release the transfer. JMLSG paragraph 8 (both customers at the same cryptoasset business) is cited and is not applied, because that exclusion was not in regulation 64A as opened.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/10-travel-rule-exception-triage
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/triage.py --input examples/sample_transfer.json --as-of 2026-10-26
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

A record that is not marked synthetic is refused. The exit code is 0 when a draft is produced, including when fields are missing. A missing field is not a failed run, and it is not a decision to hold.

## Limitations

- A field comparison is not a finding that the firm has complied or breached.
- The core does not see the firm's whole book, so it cannot decide that another transfer "appears to be linked".
- It does not convert prices. JMLSG paragraphs 45 and 46 still describe a euro conversion. Those paragraphs matched the pre-amendment words "1,000 euros". They are not used.
- It does not encode the Banking and Financial Dealings Act 1971, so it does not return a date for the three-working-day rule in regulation 64C(2).
- Regulation 14A, the Funds Transfer Regulation article 3.9, the sanctions regime, and POCA were not opened. A firm marker for suspicion or a sanctions hit is passed through as a reason to escalate. It is not a legal analysis.
- The JMLSG approval note's date was not on the page. Whether a later Annex I exists off the revisions page was not proved by the page not listing one.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. Licence coverage beyond the harness overview opened on 26 October 2026 is unverified. See [docs/harness-comparison.md](docs/harness-comparison.md).

This is not legal advice and it is not a statement of any firm's compliance.

## Two Copilot Studio harnesses

Both call `src/triage.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness holds, returns, releases, files, or contacts anyone. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The analyst pastes a record, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry, narrative only: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- Experiment 04, the authorisation-readiness pack for the same invented firm: [../04-fca-cryptoasset-readiness/](../04-fca-cryptoasset-readiness/).

## Project structure

```
experiments/10-travel-rule-exception-triage/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── triage.py
│   ├── sources.py
│   └── injection.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 26 October 2026

- [Money Laundering Regulations 2017, Part 7A](https://www.legislation.gov.uk/uksi/2017/692/part/7A)
- [SI 2022/860, introduction](https://www.legislation.gov.uk/uksi/2022/860/introduction) and [regulation 1](https://www.legislation.gov.uk/uksi/2022/860/regulation/1)
- [SI 2026/621, regulation 1](https://www.legislation.gov.uk/uksi/2026/621/regulation/1) and [regulation 32](https://www.legislation.gov.uk/uksi/2026/621/regulation/32)
- [FCA Travel Rule statement](https://www.fca.org.uk/news/statements/fca-sets-out-expectations-uk-cryptoasset-businesses-complying-travel-rule)
- [JMLSG Sector 22 Annex I, August 2023](https://www.jmlsg.org.uk/wp-content/uploads/2023/08/Board-approved_JMLSG-Guidance_Part-II-Sector-22-Annex-I_Aug2023.pdf)
- [JMLSG revisions](https://www.jmlsg.org.uk/revisions/)
- [JMLSG ministerial approval note](https://www.jmlsg.org.uk/latest-news/ministerial-approval-of-jmlsg-guidance-6/)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
