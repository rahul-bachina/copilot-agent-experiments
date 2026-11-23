# Microsoft Copilot harness

The common brief asks for a GitHub Copilot harness. The skills in `skills/` are that layout: one description line, when to use the skill, a tool contract, and the same approval gates as the standard harness.

The harness overview was not re-opened for this experiment. Experiment 70 recorded, on 20 November 2026, that the page calls the reasoning-heavy harness the Microsoft Copilot harness, describes skills, memory, file creation, and a sandbox, and says that harness uses Copilot Credits. It did not use the words GitHub Copilot harness. It stated no price. Those points are unverified against a fresh opening. See [harness-comparison.md](harness-comparison.md).

## Skills

| Skill | When |
| --- | --- |
| `prepare-control-test` | A tester wants a plan, a seeded sample, and a draft working paper. |
| `route-to-tester` | The draft has routed a distress, grievance, or safeguarding cue. |
| `record-tester-approval` | The named tester is approving this content hash. |
| `record-tester-result` | That tester is recording their own words on a staged hash. |

The description in each `SKILL.md` is the field a maker would show. This starter does not assign a weight to a skill, and it does not list trigger phrases.

File tools that the harness can offer are not used to edit evidence, to pass a control, or to send. Memory is not used to store a previous approval. An approval is only the object passed to `record_tester_approval` or `record_tester_result`.

If the core is unavailable, the skill says so and stops. It does not invent an exception or a result.
