# Which harness runs this intake

Both harnesses call the same classifier, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

This note is about running Experiment 24. It is not a recommendation of a harness for the team's proposed agent. That question is not answered here. `platform_selected` stays null.

Page opened on 30 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The comparison page and the licensing article linked from the overview were not opened for this experiment. No price is copied. No licence quantity is copied. Sentences from those pages are not repeated here.

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

## Lead: GitHub Copilot harness

Use it when the team drops in a proposal and then asks follow-up questions: which Experiment 14 rule fired, why the DPIA flag is null, why a council is a recommendation and not a mandatory-scope finding.

Microsoft's overview says this harness is for reasoning-heavy, multi-step work. It can create and edit Word, Excel, PowerPoint, and PDF files, and it supports skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview does not mark this harness as preview. This note does not call it preview.

This experiment's skills are under `skills/`. They tell the agent to call `classify` and to stop. They do not tell it to approve a use case.

## Lighter path: standard harness

Use it when the team wants the same topic every time: paste or point at one proposal, run the classifier, show the JSON, stop.

Microsoft's overview describes the standard harness for rule-based agents and agent flows, and for structured, repeatable workflows. The guide is `copilot-studio/README.md`. There is no skill on that path.

## What the overview supports, and what it does not settle

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What Microsoft says it is for | Reasoning-heavy, multi-step work, with skills and memory | Rule-based agents and agent flows |
| Files | Create and edit Word, Excel, PowerPoint, and PDF | Not described as the file path on the overview |
| Skills and memory | Supported | Not a focus of the overview's description |
| Billing | Copilot Credits, as named on the overview | Not given a price on the page opened for this folder |
| What it is not | Not the GitHub Copilot service | Not a substitute for the governance team's approval |

The Customer Conversation harness is also on the overview. The page describes it for customer voice and chat, using Copilot Credits. This intake does not use it.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/classify.py` is the only producer of a classification, a risk tier, a DPIA indication, an ATRS indication, and a resemblance.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy of this intake agent is A1 on both. Neither harness is given a tool that approves a use case, provisions an agent, writes a production record, or sends.

## What this folder does not verify

- Cost, credit amounts, and whether a Microsoft 365 Copilot licence covers either harness. The licensing article was not opened on 30 October 2026.
- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the proposal. An administrator control to disable memory was not on the page opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids a send and a write. A data loss prevention policy was not opened.
- The comparison page. It was not re-opened on 30 October 2026.
