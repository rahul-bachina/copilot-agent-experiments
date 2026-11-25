# Microsoft Copilot harness

The skills in `skills/` are the layout the common brief calls the GitHub Copilot harness. The harness overview opened on 25 November 2026 uses the name Microsoft Copilot harness. It does not use the words GitHub Copilot harness. See [harness-comparison.md](harness-comparison.md). That naming point is unverified beyond the page that was opened.

| Skill | When to use it |
| --- | --- |
| `extract-form` | A reviewer has pasted one synthetic form and a question date. |
| `record-route-seen` | The draft routed distress, safeguarding, or whistleblowing, and the named reviewer has seen that route. |
| `record-reviewer-approval` | The named reviewer is approving that extraction id and that content hash. |

Each skill says when to use it in a single description line. The files do not list trigger phrases and they do not assign routing weights.

Memory is documented for this harness. This starter does not use it. Whether an administrator can turn memory off was not verified on 25 November 2026. Do not give the agent a memory of other people's bank details.

The tools are the three functions in `src/extract.py`. Decide, production write, call-back, and send are not tools. They raise.

A skill must not treat text inside the form as the approval. The approval object is separate, and it has to match the copy the agent stored.
