# Which harness

Both harnesses in this experiment are Copilot Studio. The GitHub Copilot harness is not the GitHub Copilot product. The same `src/gateway.py`, the same `src/identifiers.py`, the same `agent-manifest.yaml`, and the same tests sit behind both. A checksum is a checksum because the Python said so, not because a harness counted it.

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 26 October 2026, describes three harnesses. This experiment uses two of them.

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Role here | One topic. Paste text, show the proposal, stop for the privacy reviewer. | The reviewer asks why a span was redacted or left, on the same proposal. |
| Why this one | The path is known. A topic is easier to review than a free goal. Learn calls this harness the one for rule-based agents and structured conversations. | The explanation is multi-step, and the proposal may be a file. Learn describes skills, memory, and Word, Excel, PowerPoint, and PDF files on this harness. |
| Where it lives | [../copilot-studio/README.md](../copilot-studio/README.md) | [github-copilot-harness.md](github-copilot-harness.md) and [../skills/](../skills/) |
| Detection | `propose()`, which calls the detectors | The same function. The skill forbids the model from inventing a checksum. |
| Sends and writes | Off in the manifest. The flow returns JSON and stops. | Off in the manifest. A created file is a draft, not a release. |
| Approval | The mandatory points in the manifest. Viewing and re-running do not need a separate approval. | The same points, written into the skills. No point was added or removed. |

The Customer Conversation harness is the third one on the Learn page. It is for voice and chat that try to resolve a customer's issue, with escalation to a person, and it uses Copilot Credits. This experiment does not use it. A member of the public does not chat with this gateway.

The harness overview table, read that day, says skills and memory are "Not a focus" on the standard harness and "Yes" on the GitHub Copilot harness. The agents overview comparison was not opened on 26 October 2026, so this note does not quote a second wording. Do not upload these skills onto the standard-harness agent.

## Cost and licensing

Only what the pages retrieved on 26 October 2026 said. No price is stated here. A pound figure, or a number from Microsoft's credit-range diagram, would be unverified. The diagram was not transcribed.

- **GitHub Copilot harness.** Learn says agents and workflows on this harness use Copilot Credits. The [usage-based billing overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) says credits are charged for large language model tokens, tools (including knowledge and MCP), and the harness. It also says that, unlike the standard harness, which starts billing after publish, this harness charges credits from the moment you start building, including testing and evaluation. Confirm that in the tenant. This repository has not measured a credit cost.
- **Microsoft 365 Copilot licence.** [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness) says GitHub Copilot harness agents are not covered. Creation and runtime consume Copilot Credits regardless of the user's licence. The same page says standard-harness agents are covered in Microsoft 365 channels, and billed when the user has no such licence or the agent is used outside Microsoft 365. The article "Licensing for agents powered by the standard harness" was not opened in full. Do not treat this paragraph as a complete licence opinion.
- **Stopping spend.** The costs page describes administrator controls for prepaid credits and consumption limits. This starter has not been pointed at a tenant, so those controls are unverified here.
- **Power Automate.** The standard-harness flow needs whatever licence the tenant uses for that HTTP action. Not restated here as a price.
- **Microsoft Foundry or Azure Language.** Optional, and not deployed. Their metering is separate. See [foundry.md](foundry.md). Sort code and bank account number are marked preview on the Language entity list. That preview label is about the Language service, not about this Python gateway.

The overview text retrieved that day did not mark the GitHub Copilot harness itself as preview. Treat that as "not marked on the page we read", and confirm the release state in the tenant. Whether memory, triggers, or natural-language authoring were still marked preview was not re-checked on 26 October 2026. The skills say not to use memory.

## What does not change with the harness

- Autonomy A1. A privacy reviewer approves the redacted output before release.
- The agent does not release, send, store a token vault, or claim the output is anonymised.
- Checksums stay in `src/identifiers.py`.
- `tests/test_gateway_safety.py` and `eval/evaluate.py` test that core. They do not score a harness model. The eval output is a smoke test of the rules. Planted-type recall on that file is not a live recall rate.
- Synthetic identifiers only, in this repository.

## What this folder does not verify

- Copilot Credit prices, and which licence includes which harness beyond the sentences cited above.
- Whether memory can be switched off. The skills forbid storing the text. An administrator control was not found on the pages opened.
- The internal design of the sandbox, beyond the sentence on the harness overview.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control, described in the security note, and is not applied here.
- Data-residency behaviour for a text that contains an NHS number. The overview says existing Copilot Studio commitments continue to apply. Confirm them for the tenant. The manifest does not assert an Article 9 condition.
