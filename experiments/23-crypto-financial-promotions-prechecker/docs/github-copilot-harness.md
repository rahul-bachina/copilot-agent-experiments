# GitHub Copilot harness

A Copilot Studio authoring and orchestration framework for the follow-up on the same JSON. It is not the GitHub Copilot service. The harness overview, opened 30 October 2026, says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

This experiment does not use the Customer Conversation harness. A customer must not chat with this agent about whether a promotion may be communicated.

Three skills:

| Skill | When |
|---|---|
| [read-promotion-draft](../skills/read-promotion-draft/SKILL.md) | The reviewer supplies one draft and an as-of date. The skill checks the record is synthetic and does not score the text itself. |
| [build-promotion-checklist](../skills/build-promotion-checklist/SKILL.md) | The skill calls `precheck()`. |
| [stop-before-sign-off](../skills/stop-before-sign-off/SKILL.md) | The JSON is already on screen. The skill explains a row and stops. It does not recompute the checklist and it does not sign off. |

All three skills use the approval gates in `agent-manifest.yaml`. None of them approves a promotion, publishes one, rewrites copy, or gives a compliance opinion. `approve_promotion`, `publish_promotion`, and `give_compliance_opinion` always raise. There is no rewrite tool. `rewrite_drafted` stays false.

The sandbox file, if one is written, is `draft-promotion-checklist.json`. It is the tool JSON. Creating it does not approve or publish anything.

Microsoft's overview says agents and workflows on this harness use Copilot Credits. The billing pages opened the same day are summarised in [harness-comparison.md](harness-comparison.md). No price is copied here. The overview did not use the word preview for the harness. The upload page still points at "Create an agent (preview)", which was not opened.

The tool list is [schema/tools.json](../schema/tools.json). `precheck_promotion` is the only tool the agent may call.
