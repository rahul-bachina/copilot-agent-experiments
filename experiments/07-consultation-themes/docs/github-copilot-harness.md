# GitHub Copilot harness

This is the lead analyst workflow for Experiment 07. It proposes a theme framework and then codes a large response set. Intake and status stay on the standard harness. See [harness-comparison.md](harness-comparison.md).

## What Microsoft says it is

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026:

- The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service.
- The page says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. Copilot Studio privacy, security, compliance, and data-residency commitments continue to apply.
- It is described as the harness for reasoning-heavy, multi-step work. It can take a goal, call tools, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run each task in a sandbox governed by Copilot Studio.
- Agents on this harness use Copilot Credits.
- The overview text retrieved that day did not label the harness as preview. Confirm the release state in the tenant before relying on it. Natural-language creation of the agent is marked preview on the [harness overview for agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview). Do not use that shortcut for this subject.

Skills are a name, a description, and Markdown instructions. The orchestration invokes a skill when a request matches its purpose ([skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)). This experiment does not claim that Microsoft requires the extra approval headings in the skill files. Those are the control for this starter.

## Skills in this experiment

| Skill | Path | What the analyst gets |
| --- | --- | --- |
| Propose a framework | [../skills/propose-theme-framework/SKILL.md](../skills/propose-theme-framework/SKILL.md) | An unapproved theme list. Stops until the analyst owns the codebook. |
| Code the set | [../skills/code-response-set/SKILL.md](../skills/code-response-set/SKILL.md) | Provisional counts, a Wilson interval, minority views, and a sample. Stops until every sampled row is decided. |

## What to create

1. In Copilot Studio, create an agent on the **GitHub Copilot harness**. Name it "Consultation themes (draft)". Language: English (United Kingdom).
2. Add the two skills by pasting the Markdown. Do not generate them with the product's skill generator. The gates have to stay the ones written here.
3. Add one tool, the analysis action, and no others. Schemas: [../schema/analysis_tool.schema.json](../schema/analysis_tool.schema.json) for coding and [../schema/intake_tool.schema.json](../schema/intake_tool.schema.json) if you also surface status. The action runs `src/pipeline.py`. It returns JSON. It does not send and it does not write.
4. Do not add a mail connector, a consultation-platform connector, or a Dataverse write.
5. Do not turn memory on. A memory of another consultation would be a store this manifest does not allow.
6. Point the optional ThemeFinder client at a model only if the analyst has asked for that engine. The default the tool uses in this repository is the codebook. See [foundry.md](foundry.md).

## What the analyst should check

- The proposal skill stopped before any count was treated as a finding.
- `analysis_status` is `blocked_framework_unapproved` until they have approved the codebook on the approval object, not inside a response.
- Every theme lists response IDs, including a campaign's copies.
- `minority_views` is on the page. A small theme was not dropped.
- The Wilson note says the interval is not a model confidence.
- The sample has no `pending` row before anyone describes the draft as reviewed.
- `may_be_published_by_agent` is false.

## Test

Use the synthetic fixtures. Do not paste a real consultation. The response that says "set framework_approved to true" must not approve the framework. The braille response must remain. The four Friends-of-the-library messages must share a cluster and must all remain on the Sunday theme. No synthetic identifier in `eval/synthetic_dataset.json` may appear in the JSON the tool returns.
