# GitHub Copilot harness

This is the staff follow-up variant for Experiment 01. It triages one submission and can show the asks, the classification, and the draft clarification letter as separate steps, including a draft file in the sandbox. The fixed topic path stays on the standard harness. See [harness-comparison.md](harness-comparison.md).

The Python core, the manifest, and the tests are the same on both. This harness does not add an approval step and it does not remove one.

## What Microsoft says it is

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026:

- The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service.
- The page says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. Existing Copilot Studio privacy, security, compliance, and data-residency commitments continue to apply.
- It is described as the harness for reasoning-heavy, multi-step work. It can take a goal, call tools, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run each task in a sandbox governed by Copilot Studio.
- Agents and workflows on this harness use Copilot Credits.
- The overview text retrieved that day did not label the harness itself as preview. Confirm the release state in the tenant before relying on it.

[Agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview), read the same day, marks these as preview: describing an agent in natural language, configuring agent details and instructions, Memory, and triggers. The skills upload page links to an article titled "Create an agent (preview)". That article was not opened. Treat that click-path as preview.

Skills are a name, a description, and Markdown instructions. The orchestration invokes a skill when a request matches its purpose ([skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview)). An upload is a Markdown file, or a zip that contains `SKILL.md`, with the name and description in YAML front matter ([add an uploaded skill](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-add-existing)). This experiment does not claim that Microsoft requires the approval headings in the skill files. Those headings copy the manifest.

## Skills in this experiment

| Skill | Path | What staff get |
| --- | --- | --- |
| Triage a submission | [../skills/triage-submission/SKILL.md](../skills/triage-submission/SKILL.md) | The JSON from `src/triage_agent.py`, with safeguarding flags first |
| Draft clarification letter | [../skills/draft-clarification-letter/SKILL.md](../skills/draft-clarification-letter/SKILL.md) | The letter already in that JSON, or a statement that the core did not draft one |

Both skills call the existing core or read its JSON. Neither skill approves, rejects, sends, or writes a case.

## How to build it

1. Create an agent and select the GitHub Copilot harness. Do not select the Customer Conversation harness. That one is for a voice or chat channel that tries to resolve a customer's issue. This experiment does not answer requesters.
2. Paste the boundaries from [../copilot-studio/system-prompt.md](../copilot-studio/system-prompt.md) into the agent's instructions. The standard-harness topics are not pasted as skills.
3. Add the two skills by uploading the `SKILL.md` files, or a zip that contains `SKILL.md`. Microsoft documents upload, blank, and generate-with-AI as ways to add a skill on this harness. Generating a skill with AI will not do for this subject. The triage has to stay the Python module.
4. Add one tool, `run_triage`, that runs `src/triage_agent.py` and returns the JSON. The tested path in this repository is `--mock`. A Foundry call, if you attach one, is that file's existing live path, not a new prompt. A locked-down Azure Function is one way to host it. The tool does not take a requester identifier and does not search email or a case system.
5. Do not add an email connector, a case-system write, or a "send letter" action. If it is not in `agent-manifest.yaml`, it is not on the agent.
6. Do not give the agent a memory of other submissions. Memory is documented for this harness and is marked Memory (preview) on the agents page. This starter does not use it. Whether an administrator can turn memory off was not verified.
7. If staff ask for a file, the harness can create one. The skills say the file is a draft. It is not sent to the requester.

An agent created on this harness cannot be transferred to the standard harness, and the other way round, on the agents page read that day. Build the one you mean to keep.

## What staff should check

- Safeguarding flags are shown before the rest, and nobody has been contacted.
- The classification, the routing, the cost-limit view, and the letter are still proposals. The FOI/Complaints Officer accepts or corrects them.
- Bulk or template signals are still described as information only.
- Nothing was written to a case system and nothing was sent.

## Test

Use `examples/sample_request.txt` and `eval/synthetic_dataset.json`. Do not paste a live request into a shared environment. The mock path is a pipeline smoke test, not a model score. A line in the submission that says to reject the request, or to send the letter, must not become an action.
