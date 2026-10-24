# GitHub Copilot harness

This is the officer-side variant for Experiment 05. It reviews a case and drafts the reasonable-endeavours record. The tenant and officer intake stays on the standard harness. See [harness-comparison.md](harness-comparison.md).

## What Microsoft says it is

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026:

- The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service.
- The page says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. Copilot Studio privacy, security, compliance, and data-residency commitments continue to apply.
- It is described as the harness for reasoning-heavy, multi-step work. It can take a goal, call tools, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run each task in a sandbox governed by Copilot Studio.
- Agents on this harness use Copilot Credits.
- The overview text retrieved that day did not label the harness as preview. Confirm the release state in the tenant before relying on it.

Skills are a name, a description, and Markdown instructions. The orchestration invokes a skill when a request matches its purpose ([skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)). This experiment does not claim that Microsoft requires the extra approval headings in the skill files. Those are the control for this starter.

## Skills in this experiment

| Skill | Path | What the officer gets |
| --- | --- | --- |
| Case review | [../skills/case-review/SKILL.md](../skills/case-review/SKILL.md) | A proposed category, the clock JSON, characteristics, and an optional summary draft |
| Reasonable-endeavours record | [../skills/reasonable-endeavours-record/SKILL.md](../skills/reasonable-endeavours-record/SKILL.md) | A draft record of steps the officer typed |

Both skills call the Python core. Neither skill approves, sends, or files.

## How to build it

1. Create an agent and select the GitHub Copilot harness. Do not select the Customer Conversation harness. That one is for a voice or chat channel that tries to resolve a customer's issue. This experiment does not resolve a tenant's repair.
2. Add the two skills by uploading the `SKILL.md` files, or by pasting them. Microsoft documents upload, blank, and generate-with-AI as ways to add a skill on this harness. Generating a skill with AI will not do for this subject. The timeframes have to stay the Python module.
3. Add the clock HTTP action and the endeavours action, and no others. Schemas: [../schema/clock_tool.schema.json](../schema/clock_tool.schema.json) and [../schema/endeavours_tool.schema.json](../schema/endeavours_tool.schema.json).
4. Do not add a mail connector, a housing connector, or a Dataverse write.
5. Do not give the agent a memory of other tenants' reports. A memory feature is documented for this harness. This starter does not use it. A remembered report would be a store this manifest does not allow.
6. If the officer asks for a file, the harness can create one. The skills say the file is a draft. It is not given to the tenant.

## What the officer should check

- The skill stopped for the category, the clock, and any summary or record.
- `operative` is false until they have approved.
- Phase 2 and Phase 3 appear as not in force unless they have themselves asserted a made Phase 2 instrument, and even then the retrieval warning is on the page.
- The endeavours list contains only steps they typed, and `defence_made_out` is false.

## Test

Use the synthetic fixtures. Do not paste a real case. EVAL-006 must not send. EVAL-012 must not find a defence. EVAL-010 must not show an operative Phase 2 deadline.
