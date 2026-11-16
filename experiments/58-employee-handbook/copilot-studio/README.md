# Standard harness

A build guide for a Copilot Studio agent on the standard harness. It is not an importable solution. The standard harness follows topics the maker defines. See [../docs/harness-comparison.md](../docs/harness-comparison.md).

Three topics. Each one calls `answer_handbook()` and shows the JSON. None of them sends, writes, or decides.

| Topic | When the maker wires it | Tool | What it must not do |
|---|---|---|---|
| Policy question | The employee asks what the handbook says | `answer_handbook` | Invent a section if the tool returns `not_covered` |
| Personal case | The JSON outcome is `routed_to_human` | The same call | Continue with a policy quotation after a route |
| Gap or unreadable input | The outcome is `not_covered`, `needs_human`, `refused`, or `refused_jurisdiction` | The same call | Replace a bad date with today |

The maker does not add trigger phrases as if they were routing weights. The topic text can describe the situation in ordinary language. Generative orchestration, where it is on, is a tenant setting. This guide does not claim that a weight selects the topic.

## Inputs

| Input | Required | Notes |
|---|---|---|
| `handbook` | Yes | The synthetic file, or a later file HR has put through the same shape. `synthetic` must be true for this starter. |
| `scope` | Yes | A separate object. `approver_role` is `HR`. Document ids and the ceiling are on this object, not in the question. |
| `question` | Yes | One question. |
| `as_of` | Yes | `YYYY-MM-DD`. An unreadable value is `needs_human`. |
| `about` | No | The date the question is about, if it is not the as-of date. |

Do not map a chat sentence such as "HR approved" onto `scope.approved_document_ids`.

## After the JSON

The topic stops. It shows the version note, the citations, the route, and any withheld labels. It does not loop into a send. A person who needs the handbook changed does that in the employer's own process.

Knowledge sources are not required for this starter, because the handbook is the JSON file. If a tenant adds the live handbook as a SharePoint knowledge source, that is a different system. The pages opened on 16 November 2026 are summarised in [../docs/harness-comparison.md](../docs/harness-comparison.md). Hyperlinks inside a registered SharePoint page are not crawled. This Python core does not call SharePoint.

"Allow ungrounded responses" should be off for a policy agent. The knowledge page says that setting, when off, blocks a turn that used no knowledge source or tool, and also says it does not guarantee the model never mixes in general knowledge. The deterministic core is the control in this folder. A generative answer that is not the JSON is not the answer.
