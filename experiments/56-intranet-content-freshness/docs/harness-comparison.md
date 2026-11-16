# Harness comparison

Both harnesses call `src/freshness.py`. Neither edits a page.

| | Standard harness | Microsoft Copilot harness |
| --- | --- | --- |
| Where it is described | `copilot-studio/` | `skills/` and this note |
| What the overview says | Rule-based. The comparison table says it follows the topics and rules you define | Reasoning-heavy, skills, memory, file creation, a secure sandbox, Copilot Credits. No price was stated |
| What this starter does | The maker follows the topic text and calls the core | The skill text tells the model when to call the core |
| Approval | `record_approval` only | The same function |
| Unverified | The overview opened on 16 November 2026 does not use the words "GitHub Copilot harness" | Older wording that this harness is not the GitHub Copilot service was not on that page |

A routing weight is not part of either harness in this starter. Do not describe a weight as a trigger phrase.

Microsoft Foundry, if used, only turns JSON the core already produced into a short note. It does not decide a finding and it does not approve a task. No Foundry resource is deployed here. See `foundry.md`.
