# Harness comparison

Opened on 26 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page says everything built in Copilot Studio runs on a harness. It names three:

- The Microsoft Copilot harness powers agents and workflows built for reasoning-heavy, multi-step work. Agents and workflows on this harness use Copilot Credits. The page says this harness can create and edit Word, Excel, PowerPoint, and PDF files, and that it supports skills and memory. This starter does not enable file editing. The review tools do not overwrite a document.
- The Customer Conversation harness powers agents that answer questions and resolve issues for customers over voice and chat. Agents on this harness use Copilot Credits. This starter is not a customer-conversation agent.
- The standard harness powers rule-based agents and agent flows. The page says it follows the topics and rules the maker defines. Billing for the standard harness is described on a licensing page. That licensing page was not opened on 26 November 2026. Do not treat a price as known.

The page does not use the words "GitHub Copilot harness". Catalogue row O006 uses that name for the second harness. This folder ships the Microsoft Copilot harness, using the skills in `skills/`, as that catalogue harness. The common-brief sentence that this harness is not the GitHub Copilot service was not on the page. That sentence is unverified.

The page does not label the Microsoft Copilot harness as preview. The page states no price.

Both harnesses in this folder call the same Python core. The core does not call a model. No Foundry resource is deployed. A short note, if someone adds one later, may use only fields already in the JSON. See [foundry.md](foundry.md).
