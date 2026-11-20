# Harness comparison

Opened on 20 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page describes three harnesses. It does not use the words "GitHub Copilot harness". It does not say that the Microsoft Copilot harness is not the GitHub Copilot service. That older sentence is unverified against this page. The page states no price.

| Harness on the page | What the page says | How this experiment uses it |
| --- | --- | --- |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. It can take a goal, call tools, and adjust. It creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox. The prose says agents and workflows on this harness use Copilot Credits. | Catalogue row L002 names Microsoft Foundry and Azure first. The skills in this folder are the layout the common brief calls the GitHub Copilot harness. The same Python core and the same seen step sit behind it. |
| Standard harness | Rule-based agents and structured workflows. The maker defines the topics, prompts, and paths. Billing is described on a licensing page this experiment did not open. This page states no price. | Topics in `copilot-studio/` call `draft_briefing()` and stop. A second topic calls `record_owner_seen` with a separate object. |
| Customer Conversation harness | Voice and chat that try to resolve a customer's issue, with escalation to a person. The prose says agents on this harness use Copilot Credits. | Not used. This experiment is not a customer conversation. |

Both harnesses used here call the same deterministic core. Neither decides applicability, changes a policy, or sends. A Foundry note, if a tenant adds one, is written from the JSON. The hashes stay in Python.

Preview: the overview does not mark the Microsoft Copilot harness or the standard harness as preview. This experiment does not promote that silence into a general-availability claim for every feature on the page. File creation and memory are described on the page. This starter does not create a file and does not keep memory.

Anything not in the paragraph above is unverified for this folder.
