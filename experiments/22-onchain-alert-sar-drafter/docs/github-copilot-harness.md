# GitHub Copilot harness

A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON. It is not the GitHub Copilot service. The harness overview, opened 29 October 2026, says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

This experiment does not use the Customer Conversation harness. A customer must not chat with this agent.

Two skills:

| Skill | When |
|---|---|
| [investigate-alert](../skills/investigate-alert/SKILL.md) | The analyst supplies a case and an as-of date. The skill calls `investigate()`. |
| [explain-draft](../skills/explain-draft/SKILL.md) | The JSON is already on screen. The skill explains a flag. It does not recompute the draft. |

Both skills use the approval gates in `agent-manifest.yaml`. Neither skill files, requests a defence, freezes a wallet, moves a cryptoasset, or drafts customer text. `file_with_nca`, `request_daml`, `contact_customer`, `freeze_account`, `move_crypto`, `record_mlro_decision`, `record_suspicion`, and `assign_glossary_code` always raise.

The sandbox file, if one is written, is `draft-investigation-note.json`. It is the tool JSON. Creating it does not file anything.

Microsoft's overview says agents and workflows on this harness use Copilot Credits. The billing overview linked from the comparison table was not opened on 29 October 2026. No price is copied here. The overview did not use the word preview for the harness. The skills upload schema was not on the overview page.

The tool list is [schema/tools.json](../schema/tools.json). `investigate_alert` is the only tool the agent may call.
