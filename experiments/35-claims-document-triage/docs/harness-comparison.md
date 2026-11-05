# Which harness

Both harnesses call the same `triage()`, the same manifest, and the same tests. The difference is how much reasoning sits around that call. Neither harness accepts, declines, or settles a claim, and neither speaks to a customer.

Page opened on 5 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The billing overview and the standard-harness licensing article linked from that page were not opened. No price is copied. A last-updated date was not in the text retrieved.

The overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement.

The overview describes three harnesses. This experiment uses two of them. It does not use the Customer Conversation harness. That harness is for customer voice and chat. This agent does not tell the customer anything.

| Harness | Used here | What the overview says it is for |
|---|---|---|
| GitHub Copilot harness | Yes. Three skills around `triage()` and `score_supplied_summary`. | Reasoning-heavy, multi-step work. Files, skills, and memory. |
| Standard harness | Yes. One topic and one flow, for a handler. | Rule-based agents. You define the topics and paths. |
| Customer Conversation harness | No. | Customer voice and chat, with escalation to a person. |

A separate Learn page on generative orchestration was not opened. This note does not assign a weight to a phrase. Where generative orchestration is on, a topic is selected from its description. The exact behaviour was not checked on 5 November 2026, so it is unverified.

## When to use the GitHub Copilot harness

Use it when the handler wants to work through one awkward pack: run the draft, then ask why a prompt is not a finding, why a score missed a threshold, or why a file was withheld.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The overview says agents and workflows on this harness use Copilot Credits. The comparison table points at a billing overview. That article was not opened. No price is copied here.

The overview did not use the word preview for the harness. The skills page it links to was not opened. Treat the authoring click-path as something to confirm in the tenant.

## When to use the standard harness

Use it when every pack goes through the same topic: paste the JSON, run the draft, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "Not a focus" on that overview. That matches the one-topic draft. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing, on the overview | The harness section says Copilot Credits. The linked billing overview was not opened. | Described in a separate licensing article, which was not opened |
| Microsoft 365 Copilot licence | Not stated on the overview page opened on 5 November 2026. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus |

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both. `permissions.yaml` is the same file.
- `src/triage.py` is the only producer of the summary, the prompts, the class, and the scorecard.
- Experiment 12 is called from that core, Experiment 08 is called from Experiment 12, and Experiment 29 scores the quotes. Neither harness reimplements them.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A1 on both. A claims handler approves the class. Neither harness is given a tool that accepts, declines, settles, tells the customer, or writes a claims system.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the pack.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector.
- Customer Conversation harness. Publishing this draft as a customer bot would be a different product. This folder does not do that.
