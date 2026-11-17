# Which harness

Both harnesses call `src/guide.py`. The scope, the tests, and the manifest are the same. Neither harness requests equipment, creates an account, grants access, enrols training, sends a message, or writes an HR record.

Opened on 17 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page names three harnesses.

- **Standard harness.** Rule-based agents and structured conversations. The maker defines the topics and the paths. Skills and memory are "not a focus". Billing is described on a licensing page that was not opened. No price is stated here.
- **Microsoft Copilot harness.** Reasoning-heavy, multi-step work. It can take a goal, call tools, and adjust when a step fails. The page says it creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No price was on the page.
- **Customer Conversation harness.** Voice and chat for customers, with a path to a person. This starter is not that product. It is an internal onboarding draft.

The page does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. The page also does not say that this harness is, or is not, the GitHub Copilot service. That sentence is unverified against the page opened on this date.

This file does not say that routing weights or trigger phrases select a skill. The skill `description` says when to use it. Generative orchestration, where the tenant uses it, can select from that description.

## Which one to use

Use the **standard harness** when the paths are known: a checklist, a how-do-I question, a personal case, a request to share. The topics are in [../copilot-studio/README.md](../copilot-studio/README.md).

Use the **Microsoft Copilot harness** when a person needs to follow the same JSON across a route, a withheld marking, a statutory pin, and the manager's approval in one task. The skills are in [../skills/](../skills/). It still cannot approve the checklist or provision anything. File creation on that harness is a platform capability. This agent does not ask it to write a statement of particulars or a letter.

## What this starter does not call

SharePoint, Microsoft Graph, and Microsoft 365 Copilot are not called. Knowledge-source limits were not re-opened on 17 November 2026. Experiment 58 recorded what those pages said on 16 November 2026. That record is not repeated here as a fresh verification.

Experiment 21, Experiment 57, and Experiment 58 are in-process calls on synthetic fixtures. `network_called` and `graph_called` stay false.
