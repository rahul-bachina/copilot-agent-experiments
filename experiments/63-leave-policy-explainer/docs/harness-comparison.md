# Which harness

Both harnesses call `src/explain.py`. The scope, the tests, and the manifest are the same. Neither harness decides an entitlement, books leave, records leave, or calculates pay.

Opened on 18 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page names three harnesses.

- **Standard harness.** Rule-based agents and structured conversations. The maker defines the topics and the paths. Skills and memory are "not a focus". Billing is described on a licensing page that was not opened. No price is stated here.
- **Microsoft Copilot harness.** Reasoning-heavy, multi-step work. The page says it can take a goal, call tools, and adjust when a step fails. It says the harness creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox governed by Copilot Studio. Agents and workflows on this harness use Copilot Credits. No price was on the page.
- **Customer Conversation harness.** Voice and chat for customers, with a path to a person. This leave explainer is not that product. It is an internal policy explanation.

The page does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. Whether Microsoft renamed an earlier "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page that was opened. Those points are unverified against that page.

This file does not say that routing weights or trigger phrases select a skill. The skill `description` says when to use it. Generative orchestration, where the tenant uses it, can select from that description. This starter does not assign a weight.

## Which one to use

Use the **standard harness** when the paths are known: a policy question, a care route, a gap, a stale or superseded version. The topics are in [../copilot-studio/README.md](../copilot-studio/README.md).

Use the **Microsoft Copilot harness** when a person needs to follow the same JSON across a route, a withheld marking, and a statutory pin in one task. The skills are in [../skills/](../skills/). It still cannot approve a policy, book leave, or decide entitlement. File creation on that harness is a platform capability. This agent does not ask it to write a policy or a letter.

## Knowledge sources

This starter does not call Copilot Studio knowledge, SharePoint, or Microsoft 365 Copilot. Experiment 58 opened the knowledge-source pages on 16 November 2026. Those pages were not re-opened on 18 November 2026. The limits recorded there are not restated here as current.
