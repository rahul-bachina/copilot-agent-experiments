# Which harness

Both harnesses in this experiment are Copilot Studio. The GitHub Copilot harness is not the GitHub Copilot product. The same `src/triage_agent.py`, the same `agent-manifest.yaml`, and the same tests sit behind both. A classification in the JSON is the core's classification. The harness does not get a second one.

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026, describes three harnesses. This experiment uses two of them.

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Role here | Lead intake. Staff paste one submission. A topic calls the triage flow, shows the JSON, and stops. | Staff ask follow-up questions about the same JSON: the asks, the classification, and the draft letter, including a sandbox file if they want one. |
| Why this one | The path is known. Topics and one flow are easier to review than a free goal. Learn calls this harness the one for rule-based agents and structured conversations. | The follow-up is multi-step, and the letter may be a file. Learn describes skills, memory, and Word, Excel, PowerPoint, and PDF files on this harness. |
| Where it lives | [../copilot-studio/README.md](../copilot-studio/README.md) | [github-copilot-harness.md](github-copilot-harness.md) and [../skills/](../skills/) |
| Triage | The Power Automate flow described in `copilot-studio/power-automate-flow.md`, which calls Microsoft Foundry. The tested core in this repository is `src/triage_agent.py --mock`. | The same `triage()` function. The skill forbids the model from inventing the JSON. |
| Sends and writes | Off in the manifest. The topics display a draft. They do not send it. | Off in the manifest. A created file is a draft, not a send and not a case-system write. |
| Approval | The five mandatory points in the manifest. Viewing and re-running do not need a separate approval. | The same five points, written into the skills. No point was added or removed. |

The Customer Conversation harness is the third one on the Learn page. It is for voice and chat that try to resolve a customer's issue, with escalation to a person, and it uses Copilot Credits. This experiment does not use it. A requester's FOI response is not resolved in a chat. Staff approve the classification, the routing, the cost-limit view, any safeguarding escalation, and the letter.

Two Microsoft tables, read the same day, do not use the same words for skills on the standard harness. The harness overview says skills and memory are "Not a focus". The [agents overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview) comparison says Skills and Memory are "Not supported" on the standard harness and "Supported" on the GitHub Copilot harness. This note does not reconcile those cells. Do not upload these skills onto the standard-harness agent.

The same agents page says an agent created on one harness cannot be transferred to the other.

## Cost and licensing

Only what the pages retrieved on 24 October 2026 said. No price is stated here. A pound figure, or a number from Microsoft's credit-range diagram, would be unverified. The diagram was not transcribed.

- **GitHub Copilot harness.** Learn says agents and workflows on this harness use Copilot Credits. The [usage-based billing overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) says credits are charged for large language model tokens, tools (including knowledge and MCP), and the harness. It also says that, unlike the standard harness, which starts billing after publish, this harness charges credits from the moment you start building, including testing and evaluation. Confirm that in the tenant. This repository has not measured a credit cost.
- **Microsoft 365 Copilot licence.** [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness) says GitHub Copilot harness agents are not covered. Creation and runtime consume Copilot Credits regardless of the user's licence. The same page says standard-harness agents are covered in Microsoft 365 channels, and billed when the user has no such licence or the agent is used outside Microsoft 365. The article "Licensing for agents powered by the standard harness", linked from the harness overview, was not opened. Do not treat this paragraph as a complete licence opinion.
- **Stopping spend.** That costs page says an administrator can set an agent monthly limit and turn on stop-usage. Azure budgets and alerts on pay-as-you-go notify. The page says they do not stop Copilot Studio consumption. The capacity controls are described as applying across Copilot Studio, not only to one harness.
- **Preview billing.** The costs page has a section titled "Prepare for the end of preview billing". It says developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before this retrieval. Confirm the tenant. This starter does not know a tenant's billing state.
- **Power Automate.** The standard-harness flow needs whatever licence the tenant uses for the HTTP connector. The existing guide says Power Automate Premium. Confirm it at build time.
- **Microsoft Foundry.** Optional on the live path, and not called by the mock tests. Its own metering is separate.

The overview text retrieved that day did not mark the GitHub Copilot harness itself as preview. Treat that as "not marked on the page we read", and confirm the release state in the tenant. Describing an agent in natural language, agent instructions, Memory, and triggers are marked preview on the agents page. The Microsoft Entra admin center wizard for creating an agent identity is recorded in the security note as announced, with availability unverified. This comparison did not re-check that announcement.

## What does not change with the harness

- Autonomy A1. The FOI/Complaints Officer accepts the classification, the routing, the cost-limit assessment, and the letter. A safeguarding flag is for that officer or the Safeguarding Lead.
- The agent does not approve, reject, or close a request, and it does not auto-reject because of wording, origin, or a guess that the text was generated.
- `tests/test_triage_agent.py` and `eval/evaluate.py` test the Python core. They do not score a harness model. `eval` output is a mock-mode pipeline smoke test.
- Synthetic submissions only, in this repository.

## What this folder does not verify

- Copilot Credit prices, message-pack prices, and which licence includes which harness beyond the sentences cited above.
- Whether Memory (preview), triggers (preview), or the natural-language authoring preview had left preview after 24 October 2026.
- That memory can be switched off. The skills forbid storing the submission. An administrator control was not found on the pages opened.
- The internal design of the sandbox, beyond the sentence on the harness overview.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control, described in the security note, and is not applied here.
- Customer data-residency behaviour for a submission that contains special-category data. The overview says existing Copilot Studio commitments continue to apply. Confirm them for the tenant. The manifest's UK-region assumption is for the deploying organisation.
