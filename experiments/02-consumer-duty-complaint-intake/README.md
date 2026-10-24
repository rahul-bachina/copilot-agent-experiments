# Experiment 02: Complaint Intake Agent

UK Consumer Duty / DISP edition. Catalogue ID **C006**.

A starter for FCA-regulated firms. It helps a complaints handler turn an inbound complaint into a structured intake: what was said, whether it meets the Handbook definition of a complaint, product and root cause, characteristics a handler should review, the DISP clock, the Consumer Duty outcome the facts appear to touch, and a draft acknowledgement.

**Autonomy A1.** A handler validates every classification and every severity. The agent does not send, write a production record, close a case, uphold or reject a complaint, or decide redress.

This revision contains the permissions manifest, the deterministic DISP clock, 22 synthetic fixtures, a mock intake used only as a smoke test, and the build notes for both Copilot Studio harnesses, Microsoft Foundry and Dynamics 365 Customer Service. Nothing here calls a model.

Stack: Copilot Studio, Dynamics 365 Customer Service, and Power Platform. The clock itself is Python in the standard library, so a handler can run the dates without a tenant.

## The problem

DISP requires a firm to recognise a complaint, acknowledge it, and respond within a fixed time. The time limit depends on the kind of complaint. The summary-resolution route is three business days. The usual final response is eight weeks. An electronic-money or payment-services complaint is 15 business days, or 35 in exceptional circumstances. The Financial Ombudsman Service has its own referral windows. Missing a date, or letting a model invent one, is a conduct failure.

The Consumer Duty (PRIN 2A) asks firms to look at whether a complaint shows a problem in products and services, price and value, consumer understanding, or consumer support. Vulnerability guidance asks firms to notice characteristics of vulnerability and respond to the need, without sticking the label "vulnerable" on the customer.

Handlers still have to read the email, the form, or the transcript and work this out. The agent prepares that reading. The handler decides.

## Non-goals

- Deciding that a complaint is upheld, rejected, or resolved.
- Deciding redress, a refund, a goodwill payment, or a waiver of fees.
- Sending the acknowledgement, the summary resolution communication, a holding response, or a final response.
- Creating, updating, resolving, or closing a Dynamics 365 case, or writing any other production record.
- Referring a complaint to the Financial Ombudsman Service, or deciding that the Ombudsman can or cannot consider it.
- Deciding exceptional circumstances, eligible-complainant status, or that a time limit is waived.
- Labelling a customer as vulnerable, or writing a vulnerability marker onto a customer record.
- Giving legal, regulatory, or case-outcome advice.
- Using a Scottish or Northern Ireland bank-holiday calendar. This clock is England and Wales.
- Forecasting one-off proclaimed bank holidays.

## What the clock does

`src/disp_clock.py` calculates the dates. It does not call a model and it does not read the network. The same inputs always produce the same JSON.

| Clock | Rule | How it is counted |
|---|---|---|
| Summary resolution route closes | [DISP 1.5.1R](https://handbook.fca.org.uk/handbook/disp1/disp1s5) | Close of the third business day **following** the day of receipt. The day of receipt is not counted. |
| Acknowledgement | [DISP 1.6.1R](https://www.handbook.fca.org.uk/handbook/DISP/1/6.html) | "Prompt". The Handbook sets no number of days, so the clock does not invent one. |
| Final or other written response | [DISP 1.6.2R](https://www.handbook.fca.org.uk/handbook/DISP/1/6.html) | End of eight weeks after receipt. Fifty-six days. Not moved if that day is a weekend or bank holiday. |
| EMD or PSD final response | [DISP 1.6.2AR](https://www.handbook.fca.org.uk/handbook/DISP/1/6.html) | End of 15 business days after the day of receipt. In exceptional circumstances a human has flagged, a holding response by day 15 and a final response by day 35. |
| Ombudsman, if the firm has not responded | [DISP 2.8.1R](https://www.handbook.fca.org.uk/handbook/DISP/2/8.html) | The day after the firm's deadline, once that period has elapsed. |
| Six months to refer | [DISP 2.8.2R(1)](https://www.handbook.fca.org.uk/handbook/DISP/2/8.html) | Runs from the date the firm **sent** the final response, redress determination, or summary resolution communication. The anniversary is treated as still in time, because the rule says "more than six months after". |
| Six years / three years | [DISP 2.8.2R(2)](https://www.handbook.fca.org.uk/handbook/DISP/2/8.html) | Later of six years after the event and three years after awareness. Awareness is an input. The clock does not infer it, and it does not apply the exceptions in DISP 2.8.2R(3) to (5). |

Two definitions of "business day" are in the Handbook glossary, and they are not the same. Both were read at [glossary G120](https://handbook.fca.org.uk/glossary/G120):

- **DISP 1.5** uses limb (1)(a): any day which is not a Saturday or Sunday, Christmas Day, Good Friday or a bank holiday in that part of the United Kingdom. This module uses the England and Wales bank-holiday calendar.
- **DISP 1.6.2A and the business-day periods in DISP 2.8** use limb (3): a day on which the payment service provider is open for business as required for the execution of a payment transaction. A provider can be open on a Saturday or on a bank holiday. Until the handler supplies those closed dates, the 15-day and 35-day figures are a **non-operative reference** counted on the England and Wales calendar. They are not the legal deadline.

The three-business-day route exists only if the complainant has indicated acceptance ([DISP 1.5.2AR](https://handbook.fca.org.uk/handbook/disp1/disp1s5)). The clock does not decide that. "Close of business" has no hour in DISP 1.5, so the result is a date.

A mixed complaint keeps the eight-week clock and the 15/35 clock side by side. DISP 1.6 says the firm may choose to treat the whole complaint under the shorter rule. The clock does not make that choice.

## Rules the rest of the agent will apply

These are not calculated by the clock. They are the rules the intake is being built against, from pages opened on 24 October 2026.

**What a complaint is.** Handbook glossary ["complaint"](https://handbook.fca.org.uk/glossary/G197). In DISP 1.1 and in PRIN, any oral or written expression of dissatisfaction, whether justified or not, about the provision of, or failure to provide, a financial service, a claims management service or a redress determination, which alleges that the complainant has suffered (or may suffer) financial loss, material distress or material inconvenience. The wider DISP definition also requires a connection to an activity under the Financial Ombudsman Service's jurisdiction. The agent proposes a view. The handler confirms it. A dissatisfaction that alleges none of those harms is not, on that definition, a DISP complaint, and must be flagged as such rather than forced into the clock.

**Consumer Duty outcomes.** [PRIN 2A.1](https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html), read on 24 October 2026 (the section was last updated on 26 June 2026). The cross-cutting obligations are at PRIN 2A.2. The outcome rules at PRIN 2A.3 to PRIN 2A.6 cover product governance, price and value, consumer understanding and supporting consumers. The Handbook's own labels in that section are products and services (PRIN 2A.3), price and value (PRIN 2A.4) and customer support (PRIN 2A.6). The intake maps a complaint onto those outcomes for a human to accept or change. It does not decide that the firm has breached the Duty.

**Vulnerability.** [FG21/1](https://www.fca.org.uk/publication/finalised-guidance/fg21-1.pdf) paragraph 2.5 gives four drivers: health, life events, resilience, and capability. Paragraph 2.9 says customers may not want the label "vulnerable", and that firms should not use that label in their dealings with customers. The agent may flag a characteristic and quote the words that prompted it. It does not label the customer, and it does not write a marker to a customer record.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/02-consumer-duty-complaint-intake
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
```

`eval/evaluate.py` prints a **mock smoke test**. The 22 fixtures are synthetic and the classifier is a keyword stand-in tuned to them. `eval/smoke_report.json` is that same run, saved so a reviewer can see it without re-running. It is not a model score. A live Microsoft Foundry run has not been done.

Calculate one clock:

```bash
python src/disp_clock.py --received 2026-01-02 --route general
python src/disp_clock.py --received 2026-12-24 --route psd
python src/disp_clock.py --received 2026-01-05 --route psd --psp-use-england-wales-calendar
```

The third command is operative only because the flag asserts that this provider is closed on England and Wales weekends and bank holidays. Without that assertion, or an explicit list of closed dates, the 15-day and 35-day dates stay non-operative.

A proclaimed extra bank holiday, or a statutory Monday that was moved, is passed in:

```bash
python src/disp_clock.py --received 2020-05-01 \
  --extra-closed 2020-05-08 --cancel-bank-holiday 2020-05-04
```

## Sample

Complaint received Friday 2 January 2026, general route, England and Wales:

- Summary resolution route closes on Wednesday 7 January 2026.
- Final response is due by the end of Friday 27 February 2026.
- If no qualifying response has been sent, the DISP 2.8.1R referral point used here is Saturday 28 February 2026.

Payment-services complaint received Thursday 24 December 2026. On the England and Wales **reference** calendar the 15th business day is Tuesday 19 January 2027. That date is not operative until the handler confirms the provider's opening days.

## Limitations

- The standing bank-holiday pattern matches the GOV.UK England and Wales list for 2021 and 2024–2028, which was the list read on 24 October 2026. It does not include one-off proclamations. Early May 2020 and the spring bank holiday in 2022 were moved; the generator still returns the usual Monday unless the caller overrides it. The coronation bank holiday on 8 May 2023 is not included.
- Scotland and Northern Ireland have different bank holidays. A complaint handled on those calendars needs a different closed-day set. Glossary limb (1)(a) is "in that part of the United Kingdom".
- "Eight weeks after" is implemented as 56 days. "Six months after" and the six-year and three-year periods use the corresponding date, or the last day of the month if that day does not exist. That is a reading of the words in DISP 2.8.2R. The Ombudsman decides a dispute about the count.
- The day after the firm's deadline is used as the first day the complainant may refer under DISP 2.8.1R, because the firm has until the end of the deadline day. Confirm this with the firm's own procedure if it operates a more cautious internal date.
- DISP 1.6, retrieved on 24 October 2026, showed a future version dated 25 October 2027. This module encodes the text retrieved that day, not the future version.
- DISP 1.6.4R (written acceptance can disapply the eight-week rule for a non-PSD complaint) is described in the output and is not applied automatically. DISP 1.6.4AG says it does not affect the PSD/EMD rule.
- The wording required by DISP 1 Annex 3R is not copied here. It was not opened.
- `eval/smoke_report.json` is a mock smoke test of the keyword stand-in. It is not a model score. The DISP clock dates in that run are the deterministic calculation, not a guess.

This is not legal advice and it is not a statement of the firm's compliance.

## Two Copilot Studio harnesses

Both call `src/disp_clock.py` and `src/intake.py`, and both stop at the approval points already in [agent-manifest.yaml](agent-manifest.yaml). Neither harness sends, writes a case, upholds, or labels the customer. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness (lead intake).** Topics and one clock action. The steps are unchanged. See [copilot-studio/README.md](copilot-studio/README.md) and [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a handler's follow-up questions on the same draft. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft bills that harness in Copilot Credits. Prices were not copied.

## Where the rest of the starter lives

- Architecture, including the Mermaid diagram: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry path: [docs/foundry.md](docs/foundry.md).
- Dynamics 365 Customer Service, read-only and draft-only: [docs/dynamics-365-customer-service.md](docs/dynamics-365-customer-service.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/02-consumer-duty-complaint-intake/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── disp_clock.py
│   └── intake.py
├── copilot-studio/
│   ├── README.md
│   └── system-prompt.md
├── skills/
│   ├── draft-complaint-intake/SKILL.md
│   └── calculate-disp-clock/SKILL.md
├── docs/
│   ├── architecture.md
│   ├── architecture_diagram.png
│   ├── foundry.md
│   ├── dynamics-365-customer-service.md
│   ├── github-copilot-harness.md
│   ├── harness-comparison.md
│   ├── security-and-permissions.md
│   └── generate_diagram.py
├── eval/
│   ├── synthetic_dataset.json
│   ├── evaluate.py
│   └── smoke_report.json
├── examples/
└── tests/
```

## References opened for this revision

- [DISP 1.5](https://handbook.fca.org.uk/handbook/disp1/disp1s5)
- [DISP 1.6](https://www.handbook.fca.org.uk/handbook/DISP/1/6.html), last updated 1 June 2026 on the page retrieved 24 October 2026
- [DISP 2.8](https://www.handbook.fca.org.uk/handbook/DISP/2/8.html), last updated 13 January 2018 on that retrieval
- [Glossary: business day](https://handbook.fca.org.uk/glossary/G120)
- [Glossary: complaint](https://handbook.fca.org.uk/glossary/G197)
- [PRIN 2A.1](https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html), last updated 26 June 2026 on that retrieval
- [FG21/1](https://www.fca.org.uk/publication/finalised-guidance/fg21-1.pdf), paragraphs 2.5 and 2.9
- [Bank holidays](https://www.gov.uk/bank-holidays)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
