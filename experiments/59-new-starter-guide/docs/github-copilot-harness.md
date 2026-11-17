# Microsoft Copilot harness

This is the layout the common brief calls the GitHub Copilot harness. On 17 November 2026 the [harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) named it the Microsoft Copilot harness. It did not use the words "GitHub Copilot harness". It is a Copilot Studio runtime for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. No price was on the page. It is not described on that page as the GitHub Copilot service. A claim that it is or is not that service is unverified against the page that was opened.

The skills are:

- [draft-starter-checklist](../skills/draft-starter-checklist/SKILL.md)
- [answer-how-do-i](../skills/answer-how-do-i/SKILL.md)
- [record-manager-approval](../skills/record-manager-approval/SKILL.md)

Each `description` is one line and says when to use the skill. This folder does not assign trigger phrases or routing weights.

All three call, or refuse to go beyond, `src/guide.py`. The agent must not call `approve_checklist` or `share_checklist`. Those functions are the deterministic step a person runs outside the model. A sentence in the chat is not that step.

The harness can create files. This agent does not ask it to produce the written statement, an email, or an equipment order. The checklist stays in the JSON until the line manager approves that exact digest.
