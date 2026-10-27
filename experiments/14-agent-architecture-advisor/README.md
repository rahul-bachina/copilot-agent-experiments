# Experiment 14: Agent Architecture Advisor

Catalogue ID **G002**. Autonomy **A0**.

A starter for an architect who has a proposed agent and needs a first, cited pass over where it might sit. The architect describes the data, the users, the actions, the risk, and the licences the organisation says it holds. The advisor returns a draft list of options:

- Copilot Studio standard harness
- Copilot Studio GitHub Copilot harness
- Microsoft Foundry Agent Service
- Power Automate
- no agent at all

It also drafts a catalogue autonomy level (**A0, A1, or A2**), the human approval points, and a permissions-manifest skeleton. The skeleton is produced by Experiment 03's generator and checked against `schemas/agent-manifest.schema.json`.

The architect confirms every platform option. The advisor selects none of them. It does not deploy, publish, spend, or send. The output is labelled **DRAFT FOR ARCHITECT REVIEW**.

This folder is a deterministic scorer, a permissions manifest, synthetic use cases, and build notes for both Copilot Studio harnesses and for Microsoft Foundry Agent Service. Nothing here calls a model or the network.

Stack in the catalogue: Copilot Studio on the GitHub Copilot harness, and Microsoft Foundry. The runnable part is Python in the standard library, plus PyYAML and jsonschema for the manifest skeleton.

The organisations in the samples are invented. They are not clients and not licence holders.

## The problem

An architect is asked to "put an agent on it" before anyone has said what the agent would be allowed to do, which product the organisation already has, or whether an agent is the wrong shape. The five products and harnesses on this list do different jobs. Microsoft's own pages, opened for this starter on 27 October 2026, separate them. A draft that cites those pages is more useful than a preference.

The pages do not choose for a tenant. They also change. Each citation carries the date it was opened. If that date is older than the threshold (default 90 days) relative to `--as-of`, the draft says not to rely on it.

## Who it helps

An architect, or a governance owner sitting with one, who wants a repeatable first pass: which option the pinned rules mark as worth considering, which autonomy level the catalogue allows, where a person has to approve, and a manifest skeleton that is already invalid if someone asks for autonomy A3.

It does not help a team that wants the tool to pick the platform or to build it.

## Non-goals

- Selecting a platform. `platform_selected` stays null. Every option has `selected: false`.
- Recommending autonomy A3, or building an agent that approves, rejects, decides a regulated matter, changes a production record, sends, spends, or transacts without a person.
- Deploying or publishing anything in Copilot Studio, Microsoft Foundry, or Power Automate.
- Approving the permissions manifest. The generator refuses an approve flag.
- Quoting a price, a credit quantity, a pack size, or a currency amount. Pages that contain rates were opened only to see the mechanism. The rates are not copied.
- Checking a tenant's licences. The flags are the architect's statement.
- Legal advice, procurement advice, or a view that a body must buy a product.
- Reading Microsoft Learn at run time. Citations come from `src/sources.py`.
- Using real organisations, real people, or live use cases. The fixtures are synthetic.

## What the advisor does

`src/advise.py` reads one JSON use case and writes one JSON document. The same case and the same as-of date always produce the same JSON, apart from the manifest YAML key order, which is stable for a given generator. It does not call a model.

Free text, including the narrative, is not an input to the rules. Instructions in that text are detected and not followed. Structured fields are. A string cannot turn a Boolean on.

The decision table is the code in `src/rules.py`. The rows below are that table. A test fails if a rule id in the code is missing here.

| Rule | When it fires | What the draft does |
|---|---|---|
| R1 | Classification is `secret_or_above`. | Only **no agent** is suitable. The other four are not indicated. This is a catalogue rule, not a sentence from Microsoft Learn. |
| R2 | The channel is voice and the audience is customers, the public, or mixed. | **No agent** is suitable. This advisor does not select a production voice agent. Foundry voice-based prompt agents are preview on the overview opened 27 October 2026, so Foundry is conditional, not a selection. The Customer Conversation harness is described on the harness page and is not one of the five options. |
| R3 | The steps are a fixed workflow: bounded data, no open-ended reasoning, no long run, no file creation, no custom code. | **Power Automate** is suitable, subject to the licence rules. A cloud flow is not an agent. The agent harnesses are not indicated. |
| R4 | The work is long-running, multi-step, large or multi-source, creates files, or needs custom code. | The **GitHub Copilot harness** is suitable, subject to licence. The standard harness is conditional: the comparison page says complex scenarios can need extensive authored paths. Foundry is suitable when custom code, a chosen model, a private network, or evaluations were asked for, and conditional otherwise. Power Automate is conditional, as a deterministic step beside an agent, not as the reasoning runtime. |
| R5 | None of R1 to R4. The work is a short, bounded, rule-based agent. | The **standard harness** is suitable, subject to licence. The GitHub Copilot harness is not indicated: the comparison page says a simple scenario can add reasoning and consumption without a better result. No rate is copied. |
| R6 | Autonomy A3 was requested, or a consequential action has no named approver. | **No agent** is suitable for that unsupervised design. Any platform that was suitable becomes conditional, and only for a reduced scope that leaves the action off. |
| R7 | The organisation recorded `no` for the licence that option needs. | That option is not indicated. No purchase is recommended. |
| R8 | The licence was recorded as `unknown`, and the option would otherwise be suitable. | The option becomes conditional. The architect confirms the licence. |
| R9 | The record says the organisation has the GitHub Copilot service only, and not Copilot Studio. | Both Copilot Studio harnesses are not indicated. The harness overview says the GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. |
| R10 | No consequential action remains in scope, or the architect asked for A0. | Recommended autonomy is **A0**. |
| R11 | A consequential action remains, a named approver was recorded, and A2 was not requested. | Recommended autonomy is **A1**. A request for A3 is lowered to A1, not left at A3. |
| R12 | A2 was requested, a named approver was recorded, and a consequential action remains. | Recommended autonomy is **A2**. The skeleton still leaves the action disabled. |
| R13 | A3 was requested, or any path would have emitted A3. | A3 is refused. `a3_recommended` is false. |
| R14 | All four product options are not indicated. | **No agent** is suitable. |

Consequential actions are: a production write, an external send, spend, approve or reject, a regulated decision, or a significant automated decision.

Suitability values are `suitable_to_consider`, `possible_with_conditions`, and `not_indicated`. None of them means selected.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/14-agent-architecture-advisor
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/advise.py --case examples/sample_use_case.json --as-of 2026-10-27
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic and the scorer is the code under `src/`. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running. It is not a model score. A live Microsoft Foundry run has not been done.

A stale-data check, without editing the catalogue:

```bash
python src/advise.py --case examples/sample_use_case.json --as-of 2027-04-01 --stale-after-days 90
```

Passing `--approve` is a mistake. The command exits and does not write a manifest.

The exit code is 0 when the JSON is produced, including when no product is indicated or a source is stale. That is not a decision to build.

## Sample

Pebbleford Borough Council is fictional. The sample is an internal, bounded policy question on Teams, with Copilot Studio recorded as held. The draft marks the standard harness as suitable to consider and selects nothing. See `examples/sample_output.json`.

## Sources and currency

Pinned on **27 October 2026**. The advisor does not download these pages. Re-check them before anyone relies on a row. Threshold used by the tests: older than 90 days from `last_verified`.

| ID | Page | Last verified | Body opened |
|---|---|---|---|
| `cs-harnesses-overview` | [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | 27 October 2026 | Yes |
| `cs-choose-harness` | [Compare Copilot Studio agent harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness) | 27 October 2026 | Yes |
| `cs-assign-licences` | [Assign user licenses and manage access](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing) | 27 October 2026 | Yes |
| `cs-standard-licensing` | [Standard harness licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing) | 27 October 2026 | Yes |
| `cs-usage-billing` | [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) | 27 October 2026 | Yes |
| `cs-gh-cost-management` | [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness) | 27 October 2026 | Yes |
| `foundry-agent-service` | [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) | 27 October 2026 | Yes |
| `foundry-prompt-shields` | [Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields) | 27 October 2026 | Yes |
| `pa-cloud-flows` | [Overview of cloud flows](https://learn.microsoft.com/en-us/power-automate/overview-cloud) | 27 October 2026 | Yes |
| `pa-licence-types` | [Types of Power Automate licenses](https://learn.microsoft.com/en-us/power-platform/admin/power-automate-licensing/types) | 27 October 2026 | Yes. Quantities and price words on that page are not copied. |

The retrieved pages did not show a "last updated" line in the text this starter stored. `last_verified` is the day the body was opened, not a date Microsoft printed.

## Limitations

- The rules are a reading of those pages for this catalogue. Another architect can weigh the same sentences differently. The draft says so by refusing to select.
- The harness overview describes three harnesses, including a Customer Conversation harness. The comparison page compares the standard harness and the GitHub Copilot harness and says some agentic capabilities should be validated as the experience matures. The overview does not mark the GitHub Copilot harness itself as preview. This starter does not promote that silence into a general-availability claim.
- Two licensing pages opened the same day do not use the same list of what a Microsoft 365 Copilot licence covers. Both sentences are kept. They are not merged into one.
- The Power Automate licence page names user and capacity licences and links to a pricing page. The pricing page was not opened. A recorded `yes` does not say whether premium connectors are included.
- Foundry Agent Service describes prompt agents, voice-based prompt agents, and hosted agents. Voice-based agents are marked preview on that page. Agent optimizer is marked preview. A2A v0.3 is marked preview and v1.0 is described as generally available. This starter does not select the preview items.
- Prompt Shields are a Foundry control. User prompt attack detection is described as on by default, and document attack detection as off by default. Tool-response scanning for agents, and Spotlighting, are marked preview. This local scorer does not call Prompt Shields. Its own injection tests are the control on the use-case text.
- UK region availability was not on the Foundry overview. It is unverified.
- Entra Conditional Access, Purview, a Data Loss Prevention policy, and Key Vault were not opened for this revision. They are named in the security note as unverified.
- A procurement route (G-Cloud, DOS, RM6200) is not scored. Those pages were not opened for this run.
- `eval/smoke_report.json` is a deterministic smoke test. It is not a model score.

This is not legal advice and it is not a statement of any organisation's licensing.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use, for this advisor itself: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness (lead shape for the advisor): [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/14-agent-architecture-advisor/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── skills/
├── copilot-studio/
├── docs/
├── eval/
├── examples/
├── fixtures/
└── tests/
```

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
