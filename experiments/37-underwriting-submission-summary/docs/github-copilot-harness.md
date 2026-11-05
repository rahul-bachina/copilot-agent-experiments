# GitHub Copilot harness

This is a build note for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service. The harness overview opened on 5 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents and workflows on this harness use Copilot Credits. The overview says that. It does not state a price. The billing page was not opened on 5 November 2026. The overview did not mark the harness as preview.

This experiment's skills tell the agent to call `summarise()` and to stop. They do not tell it to accept a risk, suggest a price, email a broker, or write an underwriting system.

## Skills

| Skill | When |
|---|---|
| `skills/summarise-submission/SKILL.md` | The underwriter wants the cited draft. |
| `skills/check-submission-citations/SKILL.md` | The underwriter pasted a fact and wants the pinpoint checked. |
| `skills/list-missing-information/SKILL.md` | The underwriter wants the fields that are not stated, without a message to the broker. |

Each description is one line and starts with "Use when". The generative-orchestration guidance opened on 5 November 2026 says a topic can be selected when its described purpose matches the need, and also by trigger phrases, and that tool names carry more weight than descriptions. These skills do not list trigger phrases and do not assign routing weights. Whether that guidance is the selector for this harness was not on the harness overview.

## What the agent must not do

- Accept, decline, or refer the risk.
- Suggest a price, a premium, a rate, or terms.
- Contact the broker.
- Write to an underwriting system or bind cover.
- Infer a value that is not a contiguous copy of cited lines. The field is `not stated`.
- Call `record_underwriter_review`. That function is not an agent tool, and it still cannot set coverage or price.
- Recommend autonomy A3.
- Store the submission in harness memory.
- Call Microsoft Foundry.

## Same core as the standard harness

The topic in `copilot-studio/` calls the same `summarise()`. The manifest and the tests are the same. A difference in the harness does not add a tool.
