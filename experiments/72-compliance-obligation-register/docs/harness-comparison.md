# Harness comparison

Both harnesses call `propose_register()`, `stage_approved_change()`, and `record_route_seen()` in `src/register.py`. Neither harness interprets the law, assigns accountability, or sends.

The [harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) was opened on 23 November 2026. It names three harnesses:

- **Microsoft Copilot harness.** Reasoning-heavy work, skills, memory, and file creation of Word, Excel, PowerPoint, and PDF. The page mentions a sandbox and Copilot Credits. It states no price.
- **Customer Conversation harness.** Not used here.
- **Standard harness.** Follows topics and rules the maker defines.

The page does not use the words "GitHub Copilot harness". It does not say that the Microsoft Copilot harness is not the GitHub Copilot service. That older sentence is unverified against the page opened on this date. Pricing pages were not opened. Do not quote a price.

| | Standard harness | Microsoft Copilot harness |
|---|---|---|
| Where it lives | `copilot-studio/` topics and the flow note | `skills/*/SKILL.md` |
| What selects a path | Topics the maker defines | The skill `description`, where generative orchestration is on |
| What this folder does not do | It does not list phrases or weights that select a skill | It does not list phrases or weights that select a skill |
| Approval | A separate object. Words in the extract do not count | The same object and the same Python function |

The skill `description` is one line and says when to use the skill. Generative orchestration, where a tenant uses it, selects from that description. This repository does not state that a routing weight or a trigger phrase selects the skill.
