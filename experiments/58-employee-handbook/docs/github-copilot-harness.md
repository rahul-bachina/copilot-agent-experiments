# Microsoft Copilot harness

This is the skills layout for the reasoning-heavy harness. Microsoft Learn, opened 16 November 2026, calls that harness the Microsoft Copilot harness. The common brief calls the same layout a GitHub Copilot harness. The overview page did not use that name. It is not the GitHub Copilot coding product. See [harness-comparison.md](harness-comparison.md).

The harness can plan a task, use skills, and keep memory. Those are platform features. This agent still has one deterministic core. A skill must not invent a section when `answer_handbook()` is unavailable.

## Skills

| Skill | When |
|---|---|
| [answer-handbook-question](../skills/answer-handbook-question/SKILL.md) | The employee asks what the handbook says. |
| [explain-handbook-route](../skills/explain-handbook-route/SKILL.md) | Someone asks what a route or a withheld row, already on screen, means. |

Each `description` is a single line and says when to use the skill. This folder does not assign trigger phrases or routing weights.

## Gates the skills do not remove

- HR approves document ids on the scope object before the run.
- `acknowledge` is not a tool of the agent. A seen-step does not decide entitlement.
- `decide_entitlement`, `send_answer`, `write_record`, and `approve_source` raise.
- A distress or safeguarding phrase is a route, not a policy quotation.
- A stale statutory pin is marked and is not refreshed.

## Memory and files

The harness overview says the Microsoft Copilot harness supports memory and file creation. This starter does not ask it to remember a person's leave balance or to write a letter. If a tenant turns memory on, that is the tenant's setting. It is not a feature of `src/answer.py`, which keeps no store.

Copilot Credits are the billing unit named on the overview. No rate was on the page. A rate copied from somewhere else would be unverified.
