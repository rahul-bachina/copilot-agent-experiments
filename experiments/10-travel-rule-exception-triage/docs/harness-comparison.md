# Which harness

Both harnesses call the same checklist, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 26 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement.

These were not opened on 26 October 2026. Experiment 04 cites them from 24 October 2026. Do not treat that earlier retrieval as re-verified here:

- Usage-based billing
- Manage costs for agents powered by the GitHub Copilot harness
- Skills overview, and the page for adding an uploaded skill
- Licensing for agents powered by the standard harness

## When to use the GitHub Copilot harness

Use it when the analyst wants to work through one awkward transfer: run the checklist, then ask why a field was quarantined, why return was proposed, or which sentence is the FCA's and which is JMLSG's.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's skills tell the agent to call the checklist and to stop. They do not tell it to message a counterparty.

The overview did not use the word preview for the harness. The skills page it links to was not opened. Treat the authoring click-path as something to confirm in the tenant.

## When to use the standard harness

Use it when every transfer goes through the same topic: paste the JSON, run the checklist, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". That matches this intake. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations |
| Billing, on the overview | Copilot Credits | Described in a separate licensing article, which was not opened |
| Microsoft 365 Copilot licence | Not stated on the overview page opened 26 October 2026. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus |

Credit ranges, stop-usage controls, and any end of preview billing were on pages that were not opened for this experiment. Confirm them in the tenant before a build consumes credits.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/triage.py` is the only producer of missing fields, the £800 limb, the options, and the empty decision.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A1 on both. Neither harness is given a tool that holds, returns, releases, files, writes a production record, or sends.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the transfer.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector.
- Customer Conversation harness. It is for customer voice and chat. This experiment does not use it.
