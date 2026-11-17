# Which harness

Both harnesses call `src/prepare.py`. The selection, the tests, and the manifest are the same. Neither harness rates a person, reads a mailbox, or sends a message.

Opened on 17 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page names three harnesses.

- **Standard harness.** Rule-based agents and structured conversations. The maker defines the topics and the paths. Skills and memory are described as not a focus. Billing is described on a licensing page that was not opened. No price is stated here.
- **Microsoft Copilot harness.** Reasoning-heavy, multi-step work. It can take a goal, call tools, and adjust when a step fails. The page says it creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No price was on the page.
- **Customer Conversation harness.** Voice and chat for customers, with a path to a person. This prep note is not that product. The user is the line manager.

The page does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. Whether Microsoft renamed an earlier "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page that was opened. Those points are unverified against that page.

This file does not say that routing weights or trigger phrases select a skill. The skill `description` says when to use it. Generative orchestration, where the tenant uses it, can select from that description.

## Which one to use

Use the **standard harness** when the paths are known: a selected meeting, a human flag, a refusal. The topics are in [../copilot-studio/README.md](../copilot-studio/README.md).

Use the **Microsoft Copilot harness** when a person needs to follow the same JSON across a quotation, a withheld marking, and a human flag in one task. The skills are in [../skills/](../skills/). It still cannot rate performance or read a mailbox. File creation on that harness is a platform capability. This agent does not ask it to write a personnel record.

Knowledge-source limits for SharePoint were not re-opened on 17 November 2026. They are not restated here. This starter does not call SharePoint, Microsoft Graph, or Work IQ.
