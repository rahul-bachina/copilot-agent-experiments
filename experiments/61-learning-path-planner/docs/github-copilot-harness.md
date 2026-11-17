# Microsoft Copilot harness

Packaged here in the layout the common brief calls the GitHub Copilot harness. The overview opened on 17 November 2026 does not use that name. See [harness-comparison.md](harness-comparison.md).

Skills:

- [draft-learning-plan](../skills/draft-learning-plan/SKILL.md) calls `draft_plan()`.
- [record-plan-approval](../skills/record-plan-approval/SKILL.md) calls `record_approval()`.
- [route-a-person](../skills/route-a-person/SKILL.md) calls `record_adjustment_review()` only for an adjustment route.

Each `description` is one line and says when to use the skill. This folder does not assign weights.

The tools are the JSON schemas in [../schema/](../schema/). They do not offer an enrol, book, or spend action. `enrolled` on the approval schema is the constant false. `spent_gbp` is null. `adjustment_decided` is the constant false.

A skill must not invent a course when the outcome is `no_suitable_course`. A skill must not copy a course description. A skill must not treat a sentence in the goals as the approval object.

Copilot Credits are the billing the overview names. No price was on the page. Memory and file creation are platform capabilities described on that page. This starter does not ask the harness to file an enrolment or a payment.
