# Harness comparison

Opened on 27 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page says everything built in Copilot Studio runs on a harness. It names three:

- The Microsoft Copilot harness powers agents and workflows built for reasoning-heavy, multi-step work. The page says this harness can take a goal and break it into steps, can create and edit Word, Excel, PowerPoint, and PDF files, supports skills and memory, runs each task in a secure sandbox governed by Copilot Studio, and uses Copilot Credits. The comparison table says it retries and finds alternative paths automatically. This starter does not enable file editing and does not enable that retry. The tools do not submit an account action.
- The Customer Conversation harness powers agents that answer questions and resolve issues for customers over voice and chat, and it can escalate to a person. This folder does not implement that harness. The human route here is the handover record in the Python core.
- The standard harness follows the topics and rules the maker defines. Skills and memory are not a focus. That is the harness in `copilot-studio/`. Billing for the standard harness is described on a licensing page. That licensing page was not opened on 27 November 2026. Do not treat a price as known.

The page does not use the words "GitHub Copilot harness". Catalogue row UK12 names Copilot Studio, Dynamics 365, and Microsoft Foundry. This folder ships the standard harness and, as the second harness the common brief requires, the Microsoft Copilot harness using the skills in `skills/`. The common-brief sentence that this harness is not the GitHub Copilot service was not on the page. That sentence is unverified.

The page does not label the Microsoft Copilot harness as preview. The page states no price. The linked billing articles were not opened.

Both harnesses in this folder call the same Python core. The core does not call a model. No Foundry resource is deployed. A short note, if someone adds one later, may use only fields already in the JSON. See [foundry.md](foundry.md).
