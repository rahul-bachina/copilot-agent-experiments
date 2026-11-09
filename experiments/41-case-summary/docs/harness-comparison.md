# Which harness

Both harnesses call the same `summarise()`. Neither contacts the customer, changes the record, closes a complaint, or offers redress. The permissions manifest is the control if this note and the manifest disagree.

The comparison below uses [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), opened on 9 November 2026. Linked billing pages were not opened. No price is stated. The overview did not mark either harness as preview.

| | Standard harness | GitHub Copilot harness |
|---|---|---|
| What it is | A harness for rule-based agents. The maker defines the topics and rules. | A Copilot Studio authoring and orchestration framework for reasoning-heavy, multi-step agents. It supports skills and memory. It is not the GitHub Copilot service. |
| Fit for this starter | A representative pastes one case and reads one JSON draft. The path is fixed. | A representative wants the same JSON explained: which sentence failed, which event was stale, which line was withheld. |
| What this folder ships | [copilot-studio/README.md](../copilot-studio/README.md) and a system prompt. A build guide, not a solution import. | [github-copilot-harness.md](github-copilot-harness.md) and three skills. |
| Billing, as the overview states it | Described on a separate licensing page. That page was not opened. | Agents and workflows on this harness use Copilot Credits. The table cell points at another overview. That page was not opened. |
| This starter's use | One topic. Then stop. | Three skills. Then stop. No trigger phrases. No routing weights. |

The same overview describes a Customer Conversation harness for customer voice and chat, with escalation to a human representative, billed in Copilot Credits. This starter does not build that harness. The users of this agent are service representatives. Publishing an unattended line that contacted the customer would sit outside this A0 design. The detail page linked from the overview was not opened.

A separate page on generative orchestration was not opened on 9 November 2026. How a tenant selects a skill is unverified. This starter does not list trigger phrases and does not assign routing weights.

## What both harnesses refuse

- Contacting the customer.
- Writing a case record.
- Closing a complaint or offering redress.
- Deciding an outcome.
- Calling `record_accuracy_check`. That function is not an agent tool.
- Calling Microsoft Foundry. The Foundry note marks the deployment as unverified and not called.

## Cost

Building either harness in a tenant can consume Copilot Credits where the overview says so. This folder does not quote a price. Confirm the tenant's own billing page before a pilot. The Python core, run locally, does not call that tenant.
