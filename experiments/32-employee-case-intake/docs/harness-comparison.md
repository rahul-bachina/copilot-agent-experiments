# Which harness

Both harnesses call the same `draft_case()`, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 4 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

A last-updated date was not in the text retrieved for this experiment.

The page says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The same paragraph says existing Microsoft Copilot Studio privacy, security, compliance, and data residency commitments continue to apply.

The overview describes three harnesses. This experiment uses two of them. It does not use the Customer Conversation harness. That harness is for voice and chat that try to resolve a customer's issue. An employee or a manager is not the user of this agent.

| Harness | Used here | What the overview says it is for |
|---|---|---|
| GitHub Copilot harness | Yes. Two skills around `draft_case()`. | Reasoning-heavy, multi-step work. Files, skills, and memory. |
| Standard harness | Yes. One topic and one flow, for an HR officer. | Rule-based agents. You define the topics and paths. |
| Customer Conversation harness | No. | Customer voice and chat, with escalation to a person. |

These were not opened on 4 November 2026:

- The billing overview linked from the GitHub Copilot harness row
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill

The overview text retrieved that day did not mark the GitHub Copilot harness itself as preview. Treat that as "not marked on the page we read", and confirm the release state in the tenant.

## When to use the GitHub Copilot harness

Use it when the HR officer wants the draft explained: which keyword matched, why a tie stayed unresolved, why whistleblowing language kept the designated route, or why a sentence was treated as an instruction.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The page says agents and workflows on this harness use Copilot Credits. The comparison table points at a separate billing overview. That article was not opened. No price is copied here.

Generative orchestration, where the tenant uses it, selects a skill from its description. These skills do not assign trigger phrases or routing weights.

## When to use the standard harness

Use it when every case goes through the same topic: paste the JSON, run the draft, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "Not a focus". The guide is [../copilot-studio/README.md](../copilot-studio/README.md). There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing, on the overview | The harness section says Copilot Credits. The comparison table points at a billing overview, which was not opened. | Described in a separate licensing article, which was not opened |
| Microsoft 365 Copilot licence | Not stated on the overview page opened on 4 November 2026. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus |

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both. It is the permissions manifest for this repository's schema.
- `src/draft.py` is the only producer of the category, the urgency flag, the time references, the route, and the empty decisions.
- Experiment 15, Experiment 12, and Experiment 08 are called from that core. Neither harness reimplements them.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model. `eval/smoke_report.json` counts cases once.
- Autonomy is A1 on both. An HR officer confirms classification and routing. Neither harness is given a tool that does that, contacts anyone, or writes an HR system.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the narrative.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector.
- Customer Conversation harness. Publishing this intake as an employee bot would be a different product. This folder does not do that.
