# GitHub Copilot harness

The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework for a wording specialist who wants a comparison explained in steps. It is not the GitHub Copilot service. The harness overview opened on 6 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. It says this harness can take a goal, break it into steps, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run in a sandbox. Agents and workflows on it use Copilot Credits. The billing page was not opened. The overview did not mark the harness as preview.

This experiment does not ask the harness to create an endorsement file.

## Skills

| Skill | When |
|---|---|
| `compare-policy-wordings` | The specialist wants the cited comparison, including every not stated cell. |
| `list-material-differences` | The specialist wants the rows whose normalised text differs, or where a topic is absent from one wording. |
| `explain-comparison-row` | The specialist wants one row restated with its clause citations. |

Each description is one line and says when to use the skill. The generative-orchestration guidance opened on 6 November 2026 says the planner can invoke a topic when its described purpose matches the need, and also by trigger phrases, and that tool names carry more weight than descriptions. These skills do not list trigger phrases and do not assign routing weights. Whether that planner selects this harness was not stated on the harness overview. That link is unverified.

## Tool contract

The callable tools are `compare_policy_wordings`, `list_material_differences`, and `explain_comparison_row`. All three read. None writes or sends. `interpret_favourability`, `recommend_buy_sell_renew`, `draft_endorsement`, `contact_broker`, `write_policy_admin`, `decide_coverage`, and `release_evaluation` always raise. `record_specialist_review` is not an agent tool.

## Approval gates

Producing the JSON does not need approval. Validating every interpretation does. The wording specialist does that outside the skills. A buy, sell, or renew decision, an endorsement, a broker message, and a policy-administration write stay outside the harness.

## Memory

Do not store the wordings or the draft. The overview says the harness supports memory. A control to turn memory off was not on that page.

## Stop

When the JSON is shown, stop. Autonomy A3 is never a recommendation.
