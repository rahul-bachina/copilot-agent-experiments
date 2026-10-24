# GitHub Copilot harness

This is the handler follow-up variant for Experiment 02. It drafts one intake and can explain the DISP clock as its own step, including a draft file in the sandbox. The fixed topic path stays on the standard harness. See [harness-comparison.md](harness-comparison.md).

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

| Skill | Path | What the handler gets |
| --- | --- | --- |
| Draft a complaint intake | [../skills/draft-complaint-intake/SKILL.md](../skills/draft-complaint-intake/SKILL.md) | The JSON from `src/intake.py`, including the draft acknowledgement |
| Calculate the DISP clock | [../skills/calculate-disp-clock/SKILL.md](../skills/calculate-disp-clock/SKILL.md) | The JSON from `src/disp_clock.py`, copied rather than recounted |

Neither skill sends, writes a case, upholds, or labels the customer.

## How to build it

1. Create an agent and select the GitHub Copilot harness. Do not select the Customer Conversation harness. That one is for a voice or chat channel that tries to resolve a customer's issue. A customer chatting with this agent is out of scope, as the standard-harness guide already says.
2. Paste the boundaries from [../copilot-studio/system-prompt.md](../copilot-studio/system-prompt.md) into the agent's instructions.
3. Add the two skills by uploading the `SKILL.md` files, or a zip that contains `SKILL.md`. Microsoft documents upload, blank, and generate-with-AI as ways to add a skill on this harness. Generating a skill with AI will not do for this subject. The timeframes have to stay the Python module.
4. Add two tools, and no others. `draft_intake` runs `src/intake.py`. `calculate_disp_clock` runs `src/disp_clock.py`. A locked-down internal API or an Azure Function that imports those modules is one way to host them, which is the hosting note already in the standard-harness guide. Do not add 15 working days with a flow expression.
5. Do not add an email connector, a Dynamics 365 create or update action, or a send tool. If it is not in `agent-manifest.yaml`, it is not on the agent.
6. Do not give the agent a memory of other customers' complaints. Memory is documented for this harness and is marked Memory (preview) on the agents page. This starter does not use it. Whether an administrator can turn memory off was not verified.
7. If the handler asks for a file, the harness can create one. The skills say the file is a draft. It is not sent to the customer.

An agent created on this harness cannot be transferred to the standard harness, and the other way round, on the agents page read that day.

## What the handler should check

- Injection and stale flags are shown before the draft, and the receipt date is still the one they typed.
- `customer_labelled_vulnerable`, `breach_found`, and `may_be_sent_by_agent` are false, and `actions_taken` is empty.
- A suggested PSD or EMD route was not applied unless they confirmed it.
- A 15-day or 35-day date is not described as operative unless the clock JSON says it is.
- Nothing was written to Dynamics 365 and nothing was sent.

## Test

Use `eval/synthetic_dataset.json`. Do not paste a live complaint into a shared environment. The mock intake is a smoke test, not a model score. Check three paths, the same three the standard-harness guide already names: a straightforward fee complaint, a complaint that says to ignore the instructions and uphold, and a faster-payment complaint with no PSP calendar. The third must not show an operative 15-day deadline.
