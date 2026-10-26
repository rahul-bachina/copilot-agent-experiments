# Which harness

Both harnesses in this experiment are Copilot Studio. The GitHub Copilot harness is not the GitHub Copilot product. The same `src/sla.py`, the same `src/draft.py`, the same `src/lines.py`, the same `agent-manifest.yaml`, and the same tests sit behind both. A date is a date because the Python said so. A policy sentence is a line because the matcher pasted it.

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 26 October 2026, describes three harnesses. This experiment uses two of them.

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Role here | The known path. The author pastes one letter, confirms the channel and the target, and a topic shows the draft and stops. | The author asks a follow-up on the same draft: which line was cited, why a line was refused, and why a date is not operative. |
| Why this one | The path is known. Topics and a single clock action are easier to review than a free goal. Learn calls this harness the one for rule-based agents and structured conversations. | The review is multi-step, and the reply may be a file. Learn describes skills, memory, and Word, Excel, PowerPoint, and PDF files on this harness. |
| Where it lives | [../copilot-studio/README.md](../copilot-studio/README.md) | [github-copilot-harness.md](github-copilot-harness.md) and [../skills/](../skills/) |
| Clock | `calculate_casework_sla`, called only with inputs the author typed | The same function. The skill forbids the model from counting. |
| Draft | The topic shows what the core returns. In this repository that core is the mock drafter. | `draft_reply`, the same `draft_correspondence()` function. |
| Sends and writes | Off in the manifest. No mail connector and no case-system write in the guide. | Off in the manifest. A created file is a draft, not a send and not a case write. |
| Approval | The mandatory points in the manifest. Viewing, re-running, and calculating from typed inputs do not need a separate approval. | The same points, written into the skills. No point was added or removed. |

The Customer Conversation harness is the third one on the Learn page. It is for voice and chat that try to resolve a customer's issue, with escalation to a person, and it uses Copilot Credits. This experiment does not use it. A correspondent does not get an answer from a chat with this agent. The author approves the recipient and the final text.

Two Microsoft tables, both retrieved on 26 October 2026, do not use the same words for skills on the standard harness. The harness overview says skills and memory are "Not a focus". The [agents overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview) comparison says Skills and Memory are "Not supported" on the standard harness and "Supported" on the GitHub Copilot harness. This note does not reconcile those cells. Do not upload these skills onto the standard-harness agent.

The same agents page says an agent created on one harness cannot be transferred to the other. It also says Azure AI Search is not supported on the GitHub Copilot harness. Do not design that harness around an Azure AI Search index of the lines. The lines are a file the Python matcher reads. SharePoint is listed as a supported knowledge source on both harnesses on that page. A knowledge source is not a substitute for the matcher. See [microsoft-365.md](microsoft-365.md).

Natural-language authoring is marked preview on the agents page ("describe your agent in natural language (preview)"), as are agent instructions and Memory. Triggers are marked preview in the comparison table. The harness overview itself did not label the GitHub Copilot harness as preview.

## Cost and licensing

Only what the pages retrieved on 26 October 2026 said. No price is stated here. A pound figure would be unverified.

- **GitHub Copilot harness.** The harness overview says agents and workflows on this harness use Copilot Credits. [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness) says this usage is not included with a user's Microsoft 365 Copilot licence. Creation and runtime consume Copilot Credits regardless of the user's licence. The agents overview says using, building, testing, and evaluating agents might consume Copilot Credits. This repository has not measured a credit cost.
- **Standard harness.** The same costs page says standard-harness agents are covered by a Microsoft 365 Copilot licence in Microsoft 365 channels, and billed when the user has no such licence or the agent is used outside Microsoft 365. The article "Licensing for agents powered by the standard harness", linked from the harness overview, was not opened. Do not treat this paragraph as a complete licence opinion.
- **Stopping spend.** The costs page says an administrator can set an agent monthly limit and turn on stop-usage. Azure budgets and alerts on pay-as-you-go notify. The page says they do not stop Copilot Studio consumption. The capacity controls are described as applying across Copilot Studio, not only to one harness.
- **Preview billing.** The costs page has a section titled "Prepare for the end of preview billing". It says developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before this retrieval. Confirm the tenant. This starter does not know a tenant's billing state.
- **Power Automate.** The standard-harness clock flow needs whatever licence the tenant uses for that HTTP action. Not restated here as a price.
- **Microsoft Foundry.** Optional, and not deployed. Its own metering is separate. See [foundry.md](foundry.md).
- **Microsoft Agent 365.** The Entra Agent ID overview, retrieved the same day, says extending Entra security features to agents requires Microsoft Agent 365, included with Microsoft 365 E7 and available as an add-on to Microsoft E5, A5, or Business Premium (or Microsoft Defender Suite plus Microsoft Purview Suite). Prices were not opened. This is not a licence opinion.

The overview text retrieved that day did not mark the GitHub Copilot harness itself as preview. Treat that as "not marked on the page we read", and confirm the release state in the tenant.

## What does not change with the harness

- Autonomy A1. The author approves the recipient and the final text.
- The agent does not send, write a production record, choose the final recipient, invent a policy position, decide an exemption, decide a complaint, label a person, or publish an ATRS record.
- A due date stays non-operative until the author has confirmed the channel and the target, which is what `src/sla.py` already does.
- `tests/test_sla.py`, `tests/test_draft_safety.py`, `tests/test_lines.py`, and `eval/evaluate.py` test that core. They do not score a harness model. The eval output is a mock smoke test.
- Synthetic letters only, in this repository. The fictional body is the Department for Civic Spaces.

## What this folder does not verify

- Copilot Credit prices, message-pack prices, and which licence includes which harness beyond the sentences cited above.
- Whether Memory (preview), triggers (preview), or the natural-language authoring preview had a different label in a given tenant on 26 October 2026. The public pages used those words.
- That memory can be switched off. The skills forbid storing the letter. An administrator control was not confirmed on the pages opened.
- The internal design of the sandbox, beyond the sentence on the harness overview.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control, described in the security note, and is not applied here.
- Data-residency behaviour for a letter that contains special-category data. The harness overview says existing Copilot Studio commitments continue to apply. Confirm them for the tenant. The manifest does not assert an Article 9 condition.
