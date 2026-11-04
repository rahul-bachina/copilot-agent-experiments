# Copilot Studio GitHub Copilot harness

A build guide, not a solution you can import.

This is the **GitHub Copilot harness** in Copilot Studio. Microsoft's harness overview, opened 4 November 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. Customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement.

The same page says agents and workflows on this harness use Copilot Credits. The billing article it links to was not opened. No price is copied here. The page did not mark the harness as preview. Confirm the release state in the tenant.

The standard harness is [../copilot-studio/README.md](../copilot-studio/README.md). Read [harness-comparison.md](harness-comparison.md) before choosing. Do not upload these skills onto the standard-harness agent.

## Skills

| Skill | When to use it |
|---|---|
| [propose-employee-case-intake](../skills/propose-employee-case-intake/SKILL.md) | The officer supplies a case and an as-of date and wants the draft. |
| [explain-case-proposal](../skills/explain-case-proposal/SKILL.md) | The draft is already on screen and the officer asks what one field means. |

Generative orchestration, where the tenant uses it, selects a skill from its description. These files do not assign trigger phrases or routing weights. The exact upload schema was not opened on 4 November 2026. The approval rules in the skills are the manifest's rules. They are not a Microsoft schema.

## Tools the skills may call

Only `draft_employee_case`, which is `draft_case()` in `src/draft.py`. It calls Experiment 15, Experiment 08, and, when attachments are present, Experiment 12. It does not confirm classification, confirm routing, decide an outcome, advise on merits, contact anyone, or write an HR system.

`record_hr_confirmation` is not a tool of the agent. The skills say the agent must not call it.

## Memory and files

The overview says this harness supports memory and file creation. Do not turn memory on for a case narrative. Do not write the narrative into a Word file. The draft already omits it. A file that repeated it would be a store the manifest does not allow.

## Approval points

| Act | Who |
|---|---|
| Read the draft | No separate approval |
| Confirm the classification | HR officer. Not a tool. |
| Confirm the routing | HR officer. Not a tool. |
| Contact the employee or a manager, or write to the HR system | Not this agent. |
