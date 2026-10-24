# Which harness

Both harnesses in this experiment are Copilot Studio. The GitHub Copilot harness is not the GitHub Copilot product. The same `src/pipeline.py`, the same `agent-manifest.yaml`, and the same tests sit behind both. A count is a count because the Python said so, not because a harness reasoned it out.

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 24 October 2026, describes three harnesses. This experiment uses two of them.

| | Standard harness | GitHub Copilot harness |
| --- | --- | --- |
| Role here | Intake and status. How many responses, what was redacted, which rows look like a campaign, which rows contain an instruction, whether the export is stale. No theme codes. | Lead analyst workflow over the set. Propose a framework, code every response, show uncertainty and minority views, wait for every sampled row. |
| Why this one | The path is known. Topics are easier to review than a free goal. Learn calls this harness the one for rule-based agents and structured conversations. | The work is multi-step, the set is large, and the analyst may want a draft file. Learn describes skills, memory, and Word, Excel, PowerPoint, and PDF files on this harness. |
| Where it lives | [../copilot-studio/README.md](../copilot-studio/README.md) | [github-copilot-harness.md](github-copilot-harness.md) and [../skills/](../skills/) |
| Coding | Not called. | `analyse` in `src/pipeline.py`. The skill forbids the model from inventing a proportion. |
| Sends and writes | Off in the manifest. No mail action in the guide. | Off in the manifest. A created file is a draft, not a publication and not a filing. |
| Who it is for | An analyst, or a colleague checking whether an export has been loaded. Not a respondent. | The consultation analyst. Not a respondent. |

The Customer Conversation harness is the third one on the Learn page. It is for voice and chat that try to resolve a customer's issue, with escalation to a person, and it uses Copilot Credits. This experiment does not use it. A consultation respondent is not served by this agent.

## Cost and licensing

Only what the page retrieved on 24 October 2026 said. No price is stated here. A pound figure would be unverified.

- **GitHub Copilot harness.** Learn says agents and workflows on this harness use Copilot Credits. The overview points to "Overview of billing for agents powered by the GitHub Copilot harness" for the detail. This repository has not measured a credit cost. Confirm the bill in the tenant, including for building and testing. Experiment 05's note, from the billing overview retrieved the same day, says this harness charges credits from the moment you start building, unlike the standard harness which starts billing after publish. That billing page was not re-opened for this experiment. Treat the "from the moment you start building" sentence as carried from that note, and check it.
- **Standard harness.** The harness overview points to "Licensing for agents powered by the standard harness" and does not set the price in the overview. This note does not guess a message pack, a session, or a conversion into credits.
- **ThemeFinder and Microsoft Foundry.** Optional, and not deployed. Their metering is separate. See [foundry.md](foundry.md).
- **The Python core.** No licence beyond this repository's MIT licence. It does not call a paid API.

The overview text retrieved that day did not mark the GitHub Copilot harness itself as preview. Treat that as "not marked on the page we read", and confirm the release state in the tenant. It is not a finding that every related feature is generally available. The skills overview and the instructions page should be checked in the tenant. Memory on that harness is a documented capability. This starter does not turn memory on, because a remembered consultation would be a store the manifest does not allow.

Natural-language agent creation is described as preview on the [GitHub Copilot harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview) ("you describe your agent in natural language (preview)"). This experiment does not use that path. The skills are written by hand.

## What does not change with the harness

- Autonomy A1. The analyst approves the framework and every sampled assignment.
- Minority themes and campaign copies stay in the audit.
- `tests/test_pipeline.py` rejects a self-approved framework, a publish flag, and a leaked identifier.
- Synthetic responses only, in this repository.
