# Which harness

Both harnesses in this experiment are Copilot Studio. The GitHub Copilot harness is not the GitHub Copilot product. The same `src/statutory_clock.py`, the same `agent-manifest.yaml`, and the same tests sit behind both. A date is a date because the Python said so, not because a harness reasoned it out.

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026, describes three harnesses. This experiment uses two of them.

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Role here | Lead intake. Capture a report. Officer confirms the category and the clock. Draft the summary and stop. | Officer reviews the case and drafts the reasonable-endeavours record. |
| Why this one | The path is known. Topics and a single clock action are easier to review than a free goal. Learn calls this harness the one for rule-based agents and structured conversations. | The review and the record are multi-step, and the record may be a file. Learn describes skills, memory, and Word, Excel, PowerPoint, and PDF files on this harness. |
| Where it lives | [../copilot-studio/README.md](../copilot-studio/README.md) | [github-copilot-harness.md](github-copilot-harness.md) and [../skills/](../skills/) |
| Clock | `calculate_statutory_clock` | The same function. The skill forbids the model from counting. |
| Sends and writes | Off in the manifest. No mail or housing action in the guide. | Off in the manifest. A created file is a draft, not a send and not a filing. |
| Tenant channel | Not published by this repository. A capture topic, if a landlord later publishes one, uses a fixed line and does not state a deadline. | Not a tenant channel. |

The Customer Conversation harness is the third one on the Learn page. It is for voice and chat that try to resolve a customer's issue, with escalation to a person, and it uses Copilot Credits. This experiment does not use it. A tenant's repair is not resolved in a chat. The officer approves the category, the clock, and every tenant-facing summary.

## Cost and licensing

Only what the pages retrieved on 24 October 2026 said. No price is stated here. A pound figure would be unverified.

- **GitHub Copilot harness.** Learn says agents and workflows on this harness use Copilot Credits. The [usage-based billing overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview) says credits are charged for large language model tokens, tools (including knowledge and MCP), and the harness. It also says that, unlike the standard harness, which starts billing after publish, this harness charges credits from the moment you start building, including testing and evaluation. Confirm that in the tenant. This repository has not measured a credit cost.
- **Standard harness.** The harness overview points to a separate page, "Licensing for agents powered by the standard harness", and does not set the price in the overview. This note does not guess a message pack, a session, or a conversion into credits. Confirm the licence before you build.
- **Power Automate.** The clock flow needs whatever licence the tenant uses for agent flows. Not stated here.
- **Microsoft Foundry.** Optional, and not deployed. Its own metering is separate. See [foundry.md](foundry.md).

The overview text retrieved that day did not mark the GitHub Copilot harness as preview. Treat that as "not marked on the page we read", and confirm the release state in the tenant. It is not a finding that every related feature is generally available. The Microsoft Entra admin center wizard for creating an agent identity was still labelled Preview on the Learn page read the same day. See [security-and-permissions.md](security-and-permissions.md).

## What does not change with the harness

- Autonomy A1. The officer approves the category, the clock, and every tenant-facing summary.
- Phase 2 and Phase 3 are not given an operative clock by default.
- `tests/test_triage_safety.py` rejects a send, a write, a label, a defence, a referral, and a moved awareness time.
- Synthetic reports only, in this repository.
