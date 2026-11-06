# GitHub Copilot harness

This is a Microsoft Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview opened on 6 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

The credit officer supplies one synthetic pack. The harness calls the same Python as the standard harness and stops. It does not approve or decline credit, set a limit, contact the customer or a bureau, post a core banking or CRM system, or file a SAR.

## Skills

| Skill | When |
|---|---|
| [draft-credit-memo](../skills/draft-credit-memo/SKILL.md) | A cited draft from one synthetic pack is needed. |
| [check-memo-citations](../skills/check-memo-citations/SKILL.md) | One proposed sentence needs a verdict against named lines. |
| [list-missing-memo-sections](../skills/list-missing-memo-sections/SKILL.md) | The credit officer wants the sections left as not stated. |

Each description is a single frontmatter line that starts "Use when". The skills do not list trigger phrases and do not assign routing weights. The generative-orchestration guidance opened on 6 November 2026 says the planner can invoke a topic when its described purpose matches the need, and also by trigger phrases, and that names carry more weight than descriptions. It does not describe numeric routing weights. Whether that planner is the selector for this harness was not stated on the harness overview. That link is unverified.

## Memory

The overview says this harness supports memory. An administrator control to turn memory off was not on that page. The skills say do not store the pack, the figures, or the draft.

## Credits

The overview says agents and workflows on this harness use Copilot Credits. The billing page was not opened. No prices are stated here.

## Approval gates

Producing the JSON does not need approval. Using it does. The credit officer reviews every cited fact before any use. The recommendation, any approval or decline, and any limit stay outside the agent. The MLRO decides any SAR. Autonomy A3 is never a recommendation.
