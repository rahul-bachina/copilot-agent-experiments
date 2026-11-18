# Microsoft Copilot harness

Packaged here in the layout the common brief calls the GitHub Copilot harness. The overview opened on 18 November 2026 does not use that name. See [harness-comparison.md](harness-comparison.md).

Skills:

- [explore-vacancies](../skills/explore-vacancies/SKILL.md) calls `explore()`.
- [record-hr-seen](../skills/record-hr-seen/SKILL.md) calls `record_hr_seen()`.
- [route-a-person](../skills/route-a-person/SKILL.md) calls `record_route_seen()` only for a human route.

Each `description` is one line and says when to use the skill. This folder does not assign weights.

The tools are the JSON schemas in [../schema/](../schema/). They do not offer an apply, nominate, shortlist, or contact action. `eligibility_decided` on the seen schema is the constant false. `interest_shared_with_manager` is false. `adjustment_decided` on the route schema is the constant false.

A skill must not invent a vacancy when the outcome is `no_open_match`. A skill must not copy a vacancy description. A skill must not treat a sentence in the experience as the seen-step.

Copilot Credits are the billing the overview names. No price was on the page. Memory and file creation are platform capabilities described on that page. This starter does not ask the harness to file an application or a message to a manager or a recruiter.
