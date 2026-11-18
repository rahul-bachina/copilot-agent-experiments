# Which harness

Both harnesses call `src/explore.py`. The vacancy feed, the tests, and the manifest are the same. Neither harness applies, nominates, shortlists, or contacts anyone.

Opened on 18 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page names three harnesses.

- **Standard harness.** Rule-based agents and structured conversations. The maker defines the topics and the paths. Skills and memory are "not a focus". Billing is described on a licensing page that was not opened. No price is stated here.
- **Microsoft Copilot harness.** Reasoning-heavy, multi-step work. It can take a goal, call tools, and adjust when a step fails. The page says it creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No price was on the page.
- **Customer Conversation harness.** Voice and chat for customers, with a path to a person. This explorer is not that product. It is an internal advisory note.

The page does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same human gates. That layout is what this folder ships for the reasoning-heavy harness. Whether Microsoft renamed an earlier "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page that was opened. Those points are unverified against that page.

This file does not say that weights or selection phrases choose a skill. The skill `description` says when to use it. Generative orchestration, where the tenant uses it, can select from that description.

## Which one to use

Use the **standard harness** when the paths are known: explore, HR seen-step, and a human route. The topics are in [../copilot-studio/README.md](../copilot-studio/README.md).

Use the **Microsoft Copilot harness** when a person needs the same JSON across a vacancy list, a stale date, a discrepancy, and the statutory note in one task. The skills are in [../skills/](../skills/). It still cannot apply or contact anyone. File creation on that harness is a platform capability. This agent does not ask it to file an application or a message to a manager.

## Cost

The overview says the Microsoft Copilot harness and the Customer Conversation harness use Copilot Credits. It does not state a price. The licensing page linked from the overview was not opened on 18 November 2026. Any figure for a credit is unverified here. This repository does not deploy a harness.
