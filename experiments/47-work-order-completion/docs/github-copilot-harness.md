# GitHub Copilot harness

This is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 11 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. Agents on this harness use Copilot Credits. The page states no price. The billing article was not opened.

Three skills call `src/complete.py`. They do not close a job.

| Skill | When |
|---|---|
| `draft-completion-record` | The technician needs proposed fields and has not approved any. |
| `approve-completion-fields` | The technician is approving named fields. Nothing is written. |
| `stub-write-approved-fields` | The technician wants the in-memory stub to record fields already approved. |

Each skill says when to use it. This starter does not assign a weight to a skill. The overview does not describe a weight. Whether a tenant selects a skill from the description was not exercised.

The standard harness does not use these skills. See [harness-comparison.md](harness-comparison.md).

## Approval gates

1. `draft_completion` returns `human_approval` null and `stub_write.executed` false.
2. `technician_approve_fields` approves only the field ids on the review object.
3. `technician_stub_write` writes only fields approved earlier, inside the returned JSON.
4. Close, charge, order, and contact are refused. `job_closed` stays false.

A sentence in the notes is not a review object.
