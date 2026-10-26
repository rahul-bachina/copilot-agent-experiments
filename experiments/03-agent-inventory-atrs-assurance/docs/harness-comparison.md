# Which harness

Both guides in this experiment call the same Python core, the same manifest schema, and the same tests. The harness is the Copilot Studio runtime in front of that core. It is not a second implementation of the ATRS rules.

Pages below were read on 24 October 2026.

## What Microsoft documents

[Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) describes three harnesses. This experiment uses two of them.

**Standard harness.** Rule-based agents and structured conversations. You define the topics, prompts, and paths. Microsoft's example is an internal help desk. Billing is described in a separate article, "Licensing for agents powered by the standard harness". This note does not restate prices. Prices and message allowances were **not copied** from that article.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for reasoning-heavy, multi-step work. It is **not** the GitHub Copilot service. The harness overview says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio, and that existing Copilot Studio privacy, security, compliance, and data residency commitments continue to apply. The harness can take a goal, break it into steps, call tools, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run each task in a secure sandbox governed by Copilot Studio. Agents and workflows on this harness use Copilot Credits. Credit rates were **not copied**.

[Agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview), read the same day, also says:

- You describe the agent in natural language **(preview)**, and the system generates the configuration.
- "Configure agent details and instructions" is marked **(preview)**.
- Memory is linked as **Memory (preview)**.
- Triggers are marked **(preview)**.
- An agent created on this harness cannot be transferred to the standard harness, and the other way round.

Skills are a name, a description, and Markdown instructions. The orchestration runtime invokes a skill when a request matches the description. See [Skills overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/skills-overview). The standard-harness comparison table says skills and memory are "Not a focus" for the standard harness. It does not say the words "unsupported". This note does not upgrade that cell.

The Customer Conversation harness is the third option on the overview page. It is for customer voice and chat. This experiment does not use it. A public user chatting with an inventory agent would be a different product.

## Which one fits this work

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Shape | Topics for "draft a pack", "propose a status", "stop". One Power Automate action returns the Python JSON and stops. | Skills under `skills/*/SKILL.md` for the same steps, with the approval gate written into each skill. |
| Why you would pick it | The path is the same every time: one record in, one draft out, then a person. Predictable. | A governance owner asks a broader question ("what is missing on these three rows?") and the runtime plans the steps. The Python tools still do the ATRS fields and the status gate. |
| Approval | An Approval action can record the governance owner's decision. The topic must not update Dataverse on the approval branch. | The skill says the same. Memory, while preview, is not an approval. A generated file is a draft. |
| What both refuse | Sending, publishing, marking approved, autonomy A3, and writing lifecycle status without an external decision. | The same, because both call `src/`. |

Use the standard harness when the maker wants a fixed topic and a locked-down flow. Use the GitHub Copilot harness when the maker wants skills and multi-step questions, and accepts Copilot Credits and the preview labels above. Do not plan to move the agent from one harness to the other. Microsoft says that transfer is not available.

## What this repository did not verify

- Copilot Credit prices, message-pack prices, and which licence includes which harness.
- Whether Memory (preview) or triggers (preview) had left preview after 24 October 2026.
- The internal design of the sandbox, beyond the sentence on the harness overview.
- Data-residency behaviour for a pack that contains an inventory narrative. The overview says existing Copilot Studio commitments continue to apply. Confirm them for the tenant.
- That a Power Automate flow running this Python is in general availability. The flow is a design in [copilot-studio/README.md](../copilot-studio/README.md), not a packaged flow.
