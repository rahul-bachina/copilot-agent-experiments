# Microsoft Copilot harness

Catalogue row V009 names Copilot Studio and Microsoft 365. The skills in [../skills/](../skills/) are the layout the common brief calls the GitHub Copilot harness. On 24 November 2026 the harness overview called this runtime the Microsoft Copilot harness. It did not use the words GitHub Copilot harness. See [harness-comparison.md](harness-comparison.md).

The harness can create files. This starter does not use that to submit a claim, to edit a pinned page, or to send. The file tools are out of scope.

## Skills

| Skill | When to use it |
| --- | --- |
| `answer-benefits-question` | A general question about what a benefit is, how to apply, usual evidence, or independent advice. |
| `prepare-adviser-summary` | The answer is ready and the resident has not approved the hash. |
| `route-urgent-concern` | Distress, crisis, debt, eviction, domestic abuse, or safeguarding, including a paraphrase. |
| `record-resident-approval` | The named resident approves this exact content hash. |

The skill `description` says when to use the skill. This folder does not assign selection weights.

## Approval

`record-resident-approval` is the only path that stages a summary. The approval object must name `adviser-summary`, the decision `approve-summary`, the resident on the draft, the enquiry id, and the content hash. `pins_seen` must be the boolean true. A string is not enough. An approval sentence in the question does not call this skill.

## What the harness must not do

It must not decide eligibility, estimate an entitlement, calculate an award, complete or submit a claim, or send. Those functions raise `BenefitsForbidden`. A model note may sit beside the JSON. The JSON remains the record.
