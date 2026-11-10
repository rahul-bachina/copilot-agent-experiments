# Which harness

Both harnesses call `src/explainer.py`. Both stop at the approval points in `agent-manifest.yaml`. Neither grants, refuses, or changes an entitlement. The Python, the manifest, and the tests are the same.

The harness overview was opened on 10 November 2026. It names three harnesses.

| | Standard harness | GitHub Copilot harness | Customer Conversation harness |
|---|---|---|---|
| What the page says it is for | Rule-based agents and structured conversations. It follows the topics and rules the maker defines. | Reasoning-heavy, multi-step work. It can take a goal, break it into steps, and adjust. | Customer voice and chat, with a path to a human representative. |
| How this experiment uses it | One topic. The adviser pastes a request. The flow returns JSON. The topic stops. | Four skills around the same JSON: explain, show uncertainty, route a dispute, record the owner's code. | Not built. An assistant that granted entitlements would sit outside this A0 design. |
| Files, skills, memory | The page says these are not a focus. | The page says the harness supports skills and memory, and creates and edits Word, Excel, PowerPoint, and PDF files, in a sandbox. This starter does not create a file. | The page says skills and memory are supported. Not used here. |
| Billing | The page points to a licensing article. That article was not opened. No price is stated. | The page says agents and workflows use Copilot Credits. The billing article was not opened. No price is stated. | The page says Copilot Credits. No price is stated. |

The GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. Customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. The page did not mark the harness as preview.

The generative-orchestration guidance page was not opened. Whether the GitHub Copilot harness uses that planner was not stated on the overview. That link is unverified. This starter does not assign routing weights. Skill descriptions say when to use the skill.

## What is shared

- `src/explainer.py` is the only implementation of the match, the citation check, the stale window, and the human route.
- `agent-manifest.yaml` is the permission boundary. `permissions.yaml` is the same file.
- The tests and `eval/evaluate.py` run against that Python. They do not call a tenant. The smoke report is not a model score.
- Experiment 38's `normalise()` is the citation check. Experiment 40's customer-route shape is followed and not imported.

## What a deployment still has to decide

- Which harness to publish. This folder does not publish either.
- Whether a financial-services firm is in scope for the consumer-understanding outcome. PRIN 2A.5 did not return rule text on 10 November 2026.
- The lawful basis before any live plan is processed. Article 6 was not opened.
