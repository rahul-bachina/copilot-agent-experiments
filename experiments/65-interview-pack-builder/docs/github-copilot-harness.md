# Microsoft Copilot harness

Catalogue row H008 names this harness first. The layout is the skills folder the common brief calls the GitHub Copilot harness.

The overview opened on 19 November 2026 does not use those words. It calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and the prose says agents and workflows on that harness use Copilot Credits. No price is stated. Older wording that the harness is not the GitHub Copilot service was not on the page. That point is unverified.

The skills are:

| Skill | When it is used |
| --- | --- |
| `draft-interview-pack` | A recruiter wants a draft and nobody has approved the questions |
| `approve-questions` | That recruiter accepts or rejects the questions hash |
| `approve-rubric` | That recruiter accepts or rejects the rubric hash |
| `record-hr-route` | An HR partner records that they have seen one route |
| `approve-pack` | The recruiter approves the pack hash after the earlier steps |

Each skill says when to use it. This starter does not assign a weight to a skill. The overview does not describe a weight. Whether a tenant selects a skill from the description was not exercised.

Every skill calls the Python core. None of them contacts a candidate. A file the harness could create is not an invitation that has been sent. `contacted` stays false.

The same gates are in the standard harness. See [harness-comparison.md](harness-comparison.md).
