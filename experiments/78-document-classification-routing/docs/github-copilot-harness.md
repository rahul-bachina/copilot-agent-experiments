# Microsoft Copilot harness

The skills in `skills/` are the layout the common brief calls the GitHub Copilot harness. The harness overview opened on 25 November 2026 uses the name Microsoft Copilot harness. See [harness-comparison.md](harness-comparison.md).

Each skill has a single-line `description` that says when to use it. The files do not list trigger phrases and they do not assign weights.

| Skill | When |
| --- | --- |
| `propose-document-class` | A synthetic document needs a class and a destination. |
| `record-route-seen` | The outcome is the human queue and the named reviewer has seen that route. |
| `confirm-routing` | The named reviewer is confirming that held hash, that class, and that destination. |

All three call `src/classify.py`. The file tools the harness can use are not used to move the document or to send. No mailbox connector is enabled.

An approval marker inside the document is not a skill input. The approval object is separate, and it has to match the agent-held copy.
