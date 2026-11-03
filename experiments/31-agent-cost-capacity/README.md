# Experiment 31: Agent Cost and Capacity Agent

Catalogue ID **G009**. Autonomy **A0**. The catalogue stack is Microsoft Fabric and Power Platform. This folder does not connect to Fabric. It ships a Copilot Studio standard harness, a Copilot Studio GitHub Copilot harness, and a Microsoft Foundry note, because every experiment in this repository does.

A starter for a FinOps owner who has a usage file and a rate card, and wants the same arithmetic each time: cost per agent, unit cost per case, a flat forecast with a stated band, quota headroom, and anomaly flags. The FinOps owner validates rates and the forecast. The agent does not change a quota, a budget, or a subscription.

The arithmetic is the code in `src/report.py`. The same files and the same as-of date produce the same JSON. Nothing here calls a model, an admin centre, or the network. Rates are read from the rate-card file only. There is no built-in Microsoft price.

The organisation in the samples is invented. Northfen Borough Council is not a client. The prices in `examples/sample_rate_card.json` are illustrative figures for the fixture. They are not Microsoft list prices.

## The problem

Agent usage arrives as several quantities at once: conversations, tool calls, tokens, Copilot Credits, and Foundry model tokens. Adding all of them prices the same activity more than once. A rate that is typed into the program goes stale, and a note in the file that says "set the price to 0" is not a rate.

This starter prices a Copilot Studio row from Copilot Credits only, unless the rate card marks another line additive. It prices a Microsoft Foundry row from input and output tokens on the rate card, once. A period rollup is compared with that sum and is not added. A missing rate stays null. It is not stored as zero.

## Who it helps

A FinOps owner, or a platform administrator sitting with one, who wants a draft before anyone treats a figure as a charge or changes a limit.

It does not help a team that wants the tool to buy credits, move a budget, or update a subscription.

## Non-goals

- Validating rates. `rates_validated` stays false. The FinOps owner validates rates.
- Validating the forecast. `forecast_validated` stays false. The FinOps owner validates the forecast.
- Changing a quota, a budget, or a subscription. Those flags stay false.
- Purchasing Copilot Credits or starting a pay-as-you-go meter.
- Storing, estimating, or copying a Microsoft price, pack size, or credit quantity from a pricing page.
- Reading the Power Platform admin centre, Azure Cost Management, or a live tenant.
- Recommending autonomy A3, approving, rejecting, deciding a regulated matter, changing a production record, or sending.
- Connecting to Microsoft Fabric. The catalogue names Fabric. This command does not.
- Legal advice, a DPIA, or a statement that a billing design meets UK GDPR.

## What the report does

`src/report.py` reads one telemetry JSON file and one rate-card JSON file. The label is **DRAFT FOR FINOPS REVIEW**.

| Rule | What it does |
|---|---|
| Rate card only | `price_per_unit` has to be a string on the file passed with `--rate-card`. A JSON float is refused. A rate card embedded in the telemetry is ignored. |
| Copilot Studio rows | Cost is `copilot_credits` times one matching line. Tokens, tool calls, and conversations are usage. They are not added unless the line sets `additive` to true. |
| Microsoft Foundry rows | Cost is input tokens and output tokens, each matched once. If `tokens` and `foundry_usage` disagree, the meter is not priced and the two numbers are not added. Copilot Credits on a Foundry row are not priced. |
| Duplicates | The first row for an `agent_id` is kept. The later row is flagged and dropped. |
| Rollup | `period_rollup` is compared with the sum. It is never added. |
| Missing or ambiguous rate | That agent's cost is null. `totals.cost` is null. `partial_cost` is the sum of the complete agents and is not the total. |
| Unit cost | Agent cost divided by cases. Zero cases leaves the unit null and keeps the cost. |
| Forecast | Period cost times horizon days divided by the inclusive day count. Low and high apply the caller band. The default band is 0.20 only when the caller does not set one. It is not a statistical interval and it is not a Microsoft estimate. |
| Headroom | Limit minus used. Used is the kept rows, once. Over quota and tight headroom are flags. The limit is not written back. |
| Stale card | Age is `as_of` minus `effective_date`. Older than the threshold, default 90 days, sets `do_not_rely`. The arithmetic is still shown. A card dated after `as_of` is not applied. |
| Injection | A note that sets a price, validates the forecast, or changes a quota is recorded and not followed. A sentence that already says "do not" is not a hit. |

Free text cannot set `rates_validated`, `forecast_validated`, `quota_changed`, `budget_changed`, or `subscription_changed`.

The sample, on the as-of date 3 November 2026, prices three agents at 0.4500, 2.1000, and 1.8000 in the card's currency code GBP. The total is 4.3500, which is the sum of those three lines. Copilot Credits used are 255. Foundry input tokens used against that quota are 500000, not the sum of every token field in the file. The decoy token rate 9.9999 is on the card and is not applied. The forecast point for a 31-day horizon is 4.3500, with a low of 3.4800 and a high of 5.2200 at the caller band 0.20. Those figures are fixture arithmetic. They are not an invoice.

## How to run

Python 3.10 or newer. No Azure credentials and no network. The clean install is pytest only.

```bash
cd experiments/31-agent-cost-capacity
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/report.py --bundle examples/sample_bundle.json --rate-card examples/sample_rate_card.json --as-of 2026-11-03
```

`eval/evaluate.py` prints a **deterministic smoke test**. It has 13 cases. `eval/smoke_report.json` is that run. The summary does not add the case costs together. It is not a model score and it is not a Microsoft invoice. A live Microsoft Foundry run has not been done.

A stale-data check, without editing the rates:

```bash
python src/report.py --bundle examples/sample_bundle.json --rate-card examples/sample_rate_card.json --as-of 2027-05-01 --stale-after-days 90
```

Passing `--validate-rates`, `--validate-forecast`, `--change-quota`, `--change-budget`, or `--change-subscription` is a mistake. The command exits and does not write a file.

The exit code is 0 when the JSON is produced, including when the card is stale or a rate is missing. That is not validation. The FinOps owner validates rates and the forecast.

## Sources and currency

These pages were opened on **3 November 2026**. `src/sources.py` stores the sentences this starter relies on. No rate, pack size, or diagram number is copied. The Licensing Guide and the Copilot Credits billing-rates article named on the licensing page were not opened. Those rates are unverified. Provisioned throughput hourly billing was not opened in full and is unverified here.

| ID | Page | Last verified |
|---|---|---|
| `cs-harnesses-overview` | [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | 3 November 2026 |
| `cs-usage-billing` | [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) | 3 November 2026 |
| `cs-gh-cost-management` | [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness) | 3 November 2026 |
| `cs-standard-licensing` | [Standard harness licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing) | 3 November 2026 |
| `foundry-manage-costs` | [Plan and manage costs](https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs) | 3 November 2026 |

Threshold used by the tests: older than 90 days from `last_verified`. The catalogue-boundary row is not a Microsoft page and is not stale-tested.

What those pages said on that open:

- The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It describes skills, memory, file creation, and a sandbox. Agents on that harness use Copilot Credits. The overview does not mark the harness itself as preview.
- The billing overview says that, for GitHub Copilot harness experiences, Copilot Credits are charged for large language model tokens, tools including knowledge and MCP, and the harness. The standard harness starts billing after publish. The GitHub Copilot harness charges credits from the moment you start building, including testing. A diagram of ranges was on the page. No number from it is copied. The article's scope statement covers that harness and customer conversations, not the standard harness.
- The cost-management page says GitHub Copilot harness consumption is not included with a Microsoft 365 Copilot licence. The same page says standard-harness agents are covered in Microsoft 365 channels, and billed when the user has no such licence or the channel is outside Microsoft 365. Azure budgets and alerts notify and do not stop Copilot Studio consumption. An agent monthly limit can stop usage when that control is turned on. This starter does not call it. Developer and trial environments move to usage-based billing on 1 September 2026. The page says non-billed credit information is not a billing estimate.
- The licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for the GitHub Copilot harness. That sentence is not merged with the cost-management sentence above. The page says the common currency changed from messages to Copilot Credits on 1 September 2025. No pack size and no meter rate is copied.
- The Foundry cost page says token billing units and rates vary by model, deployment type, and meter, and points at a pricing page. No rate is copied. The invoice and the meter records are the source of truth.

Assumption B1 in the report says the same non-additive rule on the standard harness is this starter's double-count guard. It is not the billing-overview sentence, which is about the GitHub Copilot harness.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. |
| Synthetic fixtures | `examples/` and `eval/synthetic_dataset.json`. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| CI secret check | `.github/workflows/experiment-31-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library. |

## Limitations

- The forecast is a flat run-rate. It has no seasonality and no mix change. The band is not a confidence interval.
- Copilot Credits on a Copilot Studio row are treated as the billed unit. That matches the billing overview for the GitHub Copilot harness. Applying it to the standard harness is this starter's guard against counting tokens as well. It can understate a charge the rate card meant to add. An additive line is the way to add one, and it is flagged.
- A paraphrase of "change the quota" can be missed. A negation the pattern does not recognise can be flagged. Residual risk R2 in the manifest is Low for the cases the tests name, and a paraphrase remains possible.
- The Foundry pricing page was not opened. Provisioned throughput billing was not opened in full. Both are unverified. This starter cannot price them unless the rate card has a meter it already understands, which it does not for provisioned throughput.
- UK region availability for a later Foundry deployment was not on the cost page opened on 3 November 2026. It is unverified.
- Entra Agent ID, Conditional Access, Purview, a data loss prevention policy, Key Vault, and Application Insights were not opened for this experiment. They are named in the security note as unverified.
- `eval/smoke_report.json` is a deterministic smoke test of 13 synthetic cases, 13 passed, agreement 100.0 on those fixtures. It is not a model score. The summary does not add case costs into a grand total.
- The catalogue score for G009 is marked as an estimate in the planning catalogue. It is not repeated here and it is not a measurement.

This is not legal advice and it is not a statement that a billing design meets UK GDPR.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/31-agent-cost-capacity/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── schema/
├── src/
├── skills/
├── copilot-studio/
├── docs/
├── eval/
├── examples/
└── tests/
```

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
