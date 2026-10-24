# Which harness

Both harnesses in this experiment are Copilot Studio. The GitHub Copilot harness is not the GitHub Copilot product. The same `src/disp_clock.py`, the same `src/intake.py`, the same `agent-manifest.yaml`, and the same tests sit behind both. A date is a date because the Python said so, not because a harness counted it.

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026, describes three harnesses. This experiment uses two of them.

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Role here | Lead intake. The handler pastes one complaint, confirms the inputs, and a topic shows the draft and stops. | The handler asks a broader question across the same draft: the classification, the characteristics, the acknowledgement, and why a date came back. |
| Why this one | The path is known. Topics and a single clock action are easier to review than a free goal. Learn calls this harness the one for rule-based agents and structured conversations. | The review is multi-step, and the acknowledgement may be a file. Learn describes skills, memory, and Word, Excel, PowerPoint, and PDF files on this harness. |
| Where it lives | [../copilot-studio/README.md](../copilot-studio/README.md) | [github-copilot-harness.md](github-copilot-harness.md) and [../skills/](../skills/) |
| Clock | `calculate_disp_clock`, called only with inputs the handler typed | The same function. The skill forbids the model from counting. |
| Intake | The topic shows what the core returns. In this repository that core is the mock intake. | `draft_intake`, the same `intake()` function. |
| Sends and writes | Off in the manifest. No mail connector and no Dynamics 365 write in the guide. | Off in the manifest. A created file is a draft, not a send and not a case write. |
| Approval | The mandatory points in the manifest. Viewing, re-running, and calculating from typed inputs do not need a separate approval. | The same points, written into the skills. No point was added or removed. |

The Customer Conversation harness is the third one on the Learn page. It is for voice and chat that try to resolve a customer's issue, with escalation to a person, and it uses Copilot Credits. This experiment does not use it. A customer's complaint is not resolved in a chat with this agent. The handler validates every classification and the severity.

Two Microsoft tables, read the same day, do not use the same words for skills on the standard harness. The harness overview says skills and memory are "Not a focus". The [agents overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview) comparison says Skills and Memory are "Not supported" on the standard harness and "Supported" on the GitHub Copilot harness. This note does not reconcile those cells. Do not upload these skills onto the standard-harness agent.

The same agents page says an agent created on one harness cannot be transferred to the other.

## Cost and licensing

Only what the pages retrieved on 24 October 2026 said. No price is stated here. A pound figure, or a number from Microsoft's credit-range diagram, would be unverified. The diagram was not transcribed.

- **GitHub Copilot harness.** Learn says agents and workflows on this harness use Copilot Credits. The [usage-based billing overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) says credits are charged for large language model tokens, tools (including knowledge and MCP), and the harness. It also says that, unlike the standard harness, which starts billing after publish, this harness charges credits from the moment you start building, including testing and evaluation. Confirm that in the tenant. This repository has not measured a credit cost.
- **Microsoft 365 Copilot licence.** [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness) says GitHub Copilot harness agents are not covered. Creation and runtime consume Copilot Credits regardless of the user's licence. The same page says standard-harness agents are covered in Microsoft 365 channels, and billed when the user has no such licence or the agent is used outside Microsoft 365. The article "Licensing for agents powered by the standard harness", linked from the harness overview, was not opened. Do not treat this paragraph as a complete licence opinion.
- **Stopping spend.** That costs page says an administrator can set an agent monthly limit and turn on stop-usage. Azure budgets and alerts on pay-as-you-go notify. The page says they do not stop Copilot Studio consumption. The capacity controls are described as applying across Copilot Studio, not only to one harness.
- **Preview billing.** The costs page has a section titled "Prepare for the end of preview billing". It says developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before this retrieval. Confirm the tenant. This starter does not know a tenant's billing state.
- **Power Automate.** The standard-harness clock flow needs whatever licence the tenant uses for that HTTP action. Not restated here as a price.
- **Microsoft Foundry.** Optional, and not deployed. Its own metering is separate. See [foundry.md](foundry.md).

The overview text retrieved that day did not mark the GitHub Copilot harness itself as preview. Treat that as "not marked on the page we read", and confirm the release state in the tenant. Describing an agent in natural language, agent instructions, Memory, and triggers are marked preview on the agents page.

## What does not change with the harness

- Autonomy A1. The handler validates every classification and every severity.
- The agent does not send, write a production record, uphold, reject, close, decide redress, refer to the Financial Ombudsman Service, or label the customer.
- A 15-day or 35-day date stays non-operative until the handler has supplied the provider's opening days, which is what `src/disp_clock.py` already does.
- `tests/test_disp_clock.py`, `tests/test_intake_safety.py`, and `eval/evaluate.py` test that core. They do not score a harness model. The eval output is a mock smoke test.
- Synthetic complaints only, in this repository. The fictional firm is Northbridge Mutual.

## What this folder does not verify

- Copilot Credit prices, message-pack prices, and which licence includes which harness beyond the sentences cited above.
- Whether Memory (preview), triggers (preview), or the natural-language authoring preview had left preview after 24 October 2026.
- That memory can be switched off. The skills forbid storing the complaint. An administrator control was not found on the pages opened.
- The internal design of the sandbox, beyond the sentence on the harness overview.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control, described in the security note, and is not applied here.
- Data-residency behaviour for a complaint that contains special-category data. The overview says existing Copilot Studio commitments continue to apply. Confirm them for the tenant. The manifest does not assert an Article 9 condition.
