# Microsoft Copilot harness

The skills in `skills/` are the second harness. The harness overview, opened on 27 November 2026, calls this runtime the Microsoft Copilot harness. It does not call it the GitHub Copilot harness. See [harness-comparison.md](harness-comparison.md).

Each skill has a single-line `description` that says when to use it. The files do not list trigger phrases and do not assign routing weights.

| Skill | Calls | Approval |
|---|---|---|
| `draft-visit-note` | `draft_note` | Not required to read the draft. The note is not written. |
| `record-route-seen` | `record_route_seen` | The named practitioner, for this hash. |
| `record-practitioner-approval` | `record_practitioner_approval` | The named practitioner, for this hash. |

The page says this harness retries and finds alternative paths, and that it can create and edit files. This starter does not enable either behaviour. A skill must not add a tool that writes a case record, shares the note, or assesses eligibility, risk, or need.

The deterministic tests in `tests/` are the check. They do not call Copilot Studio.
