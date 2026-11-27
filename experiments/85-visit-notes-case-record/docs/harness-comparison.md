# Harness comparison

Opened on 27 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page says everything built in Copilot Studio runs on a harness. It names three:

- The Microsoft Copilot harness powers agents and workflows built for reasoning-heavy, multi-step work. Agents and workflows on this harness use Copilot Credits. The page says this harness can create and edit Word, Excel, PowerPoint, and PDF files, and that it retries and finds alternative paths. This starter does not enable file editing and does not enable that retry behaviour. The draft tools do not write a case record.
- The Customer Conversation harness powers agents that answer questions and resolve issues for customers over voice and chat. Agents on this harness use Copilot Credits. This starter is not a customer-conversation agent.
- The standard harness powers rule-based agents and agent flows. The page says it follows the topics and rules the maker defines. Billing for the standard harness is described on a licensing page. That licensing page was not opened on 27 November 2026. Do not treat a price as known.

The page does not use the words "GitHub Copilot harness". Catalogue row UK13 names Azure, Microsoft Foundry, and Power Platform. This folder ships the Microsoft Copilot harness, using the skills in `skills/`, as the second harness the common brief requires. The common-brief sentence that this harness is not the GitHub Copilot service was not on the page. That sentence is unverified.

The page does not label the Microsoft Copilot harness as preview. The page states no price in figures.

Both harnesses in this folder call the same Python core. The core does not call a model. No Foundry resource is deployed. A short note, if someone adds one later, may use only fields already in the JSON. See [foundry.md](foundry.md).

| | Standard harness | Microsoft Copilot harness, skills in this folder |
|---|---|---|
| What the page says it is for | Rule-based agents and agent flows | Reasoning-heavy, multi-step work |
| What this starter uses it for | A topic guide that calls `draft_note` | The same calls, from `skills/*/SKILL.md` |
| Who approves | The named practitioner, on the separate object | The same object and the same hash |
| Writes a case record | No | No |
