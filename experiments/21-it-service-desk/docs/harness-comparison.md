# Which harness

Both harnesses call the same desk, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 29 October 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The page also says the harness shares underlying technology and SDK components with GitHub Copilot.

These were not opened on 29 October 2026:

- Usage-based billing
- The billing overview for agents powered by the GitHub Copilot harness
- Licensing for agents powered by the standard harness
- Skills overview, and the page for adding an uploaded skill
- The Customer Conversation harness article linked from the overview
- Compare Copilot Studio agent harnesses, beyond the table on the overview itself

## When to use the standard harness

Use it when every ticket goes through the same topic: paste the JSON, run the desk, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". The same page gives an internal help-desk experience, answering common questions and routing simple requests through a workflow, as an example of this harness. That matches this intake. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is described in a licensing article the overview links to. That article was not opened. This is not a licence opinion.

## When to use the GitHub Copilot harness

Use it when the analyst wants to work through one awkward ticket: run the desk, then ask which diagnostic is missing, why the phone channel was not trusted, or which sentence is the article and which is the fixed script.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's skills tell the agent to call the desk and to stop. They do not tell it to reset a password or to message anyone.

The overview did not use the word preview for the harness on the page opened on 29 October 2026. The skills page it links to was not opened. Treat the authoring click-path as something to confirm in the tenant. This folder does not promote that silence into a general-availability claim.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, including contact centres, with a route to a human representative. Agents on it use Copilot Credits. Publishing, on the comparison table, is "Website chat or a phone number".

This starter does not implement that harness. The users of this agent are a signed-in member of staff and a service desk analyst. Publishing an unattended password-reset line on that harness would sit outside this A1 design. The detail of that harness beyond the overview is unverified in this folder.

## Cost and licensing

Only what the overview itself says. No prices are copied here.

| | GitHub Copilot harness | Standard harness | Customer Conversation harness |
|---|---|---|---|
| What the overview says it is for | Complex, multi-step work, tools, files, skills | Rule-based agents and structured conversations, including an internal help desk | Customer voice and chat, with escalation to a person |
| Billing, on the overview | Copilot Credits | Described in a separate licensing article, which was not opened | Copilot Credits (usage-based) |
| Microsoft 365 Copilot licence | Not stated on the overview page opened 29 October 2026. Unverified. | Not stated on that page. Unverified. | Not stated on that page. Unverified. |
| Files, skills, memory | Yes, in a sandbox | Not a focus | Skills and memory yes. Files are "not a focus". |
| Built in this experiment | Yes | Yes | No |

Credit ranges and stop-usage controls were on pages that were not opened for this experiment. Confirm them in the tenant before a build consumes credits.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both built harnesses.
- `src/desk.py` is the only producer of the quoted article, the identity flag, the stale flag, and the empty approval.
- Experiment 08 is the only redactor. This experiment does not ship a second one.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy is A1 on both. Neither harness is given a tool that resets a password, changes MFA, grants access, writes a ticket, sends, or spends.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the ticket.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector.
- Behaviour of the Customer Conversation harness beyond the sentences on the overview page.
- The exact skill-upload schema. The skills page was not opened.
