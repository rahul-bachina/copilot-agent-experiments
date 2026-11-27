# Microsoft Copilot harness

The common brief asks for a GitHub Copilot harness as the second Copilot Studio harness. The [harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) opened on 27 November 2026 does not use the words "GitHub Copilot harness". It names a Microsoft Copilot harness for reasoning-heavy, multi-step work. This file is that second harness, implemented as the skills in `skills/`. The common-brief sentence that this harness is not the GitHub Copilot service was not on the page. That sentence is unverified.

The same page says this harness retries and finds alternative paths automatically, and that it can create and edit files. This starter does not enable that retry and does not edit a file. The skills call the Python core. The core does not call a model.

## Skills

| Skill | Calls | When |
|---|---|---|
| `answer-account-question` | `answer()` | An account or billing question, before any proposal. |
| `propose-account-action` | `answer()` | One meter reading, payment-plan request, or Priority Services Register referral, with no vulnerability or affordability cue. |
| `hand-to-human` | `answer()` | A request for a person, or a vulnerability, complaint, affordability, distress, or prohibited-action cue. |
| `confirm-account-action` | `confirm_action()` | A separate confirmation object for the held hash. |

Each `SKILL.md` has a single-line description that says when to use the skill. The files do not list phrases for selection and do not assign weights.

`confirm-account-action` is the only skill that records a confirmation. It does not submit the action. A sentence in the customer message is not that skill.
