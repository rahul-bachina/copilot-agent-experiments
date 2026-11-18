# Microsoft Copilot harness

Catalogue row H007 names this harness first. The layout is the skills folder the common brief calls the GitHub Copilot harness.

Opened on 18 November 2026, the [harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox. The prose says agents on that harness use Copilot Credits. It states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service was not on that page. That point is unverified.

The skills are:

| Skill | When |
| --- | --- |
| `review-job-description` | A recruiter wants prompts and nobody has accepted a suggestion yet. |
| `record-suggestion-decision` | The directory recruiter accepts or rejects one suggestion hash. |
| `route-to-hr` | The draft may be an occupational requirement, positive action, a health question, or a distress cue. |
| `record-final-wording` | The recruiter has written the final wording and every suggestion has a decision. |

Each `description` is one line and says when to use the skill. This folder does not assign a weight and does not list selection phrases.

All four call `src/review.py`. None of them publishes, posts, or sends. File creation on the harness is a platform capability. This agent does not ask it to post an advert.

The same approval gates are in the standard harness. See [harness-comparison.md](harness-comparison.md).
