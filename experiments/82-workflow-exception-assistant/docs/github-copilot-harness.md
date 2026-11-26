# Microsoft Copilot harness

The skills in `skills/` are the layout for the Microsoft Copilot harness. The harness overview opened on 26 November 2026 uses that name. It does not use the words GitHub Copilot harness. See [harness-comparison.md](harness-comparison.md).

Each skill has one description line that says when to use it. The files do not list phrases for selection and do not assign weights.

| Skill | When |
|---|---|
| `diagnose-workflow-exception` | A process owner wants a draft reading of synthetic runs. |
| `record-route-seen` | The outcome is a human route and the named owner has seen it. |
| `record-owner-decision` | The named owner chooses retry, route, or cancel for the held hash. |

The tools call `src/workflow.py`. They do not call Power Automate. The page says the Microsoft Copilot harness retries and finds alternative paths. These skills do not.

Catalogue row O009 names Power Platform and Copilot Studio. Shipping this harness as well is the common-brief requirement. It is not a claim that the catalogue row names this harness.
