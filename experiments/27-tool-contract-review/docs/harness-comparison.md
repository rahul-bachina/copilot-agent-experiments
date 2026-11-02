# Which harness runs this reviewer

Both harnesses call the same reviewer, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

This note is about running Experiment 27. It is not a decision about which harness the agent whose contract is under review should use. If the bundle includes a structured use case, Experiment 14 may draft options. `platform_selected` stays null. The architect confirms that draft. This folder does not.

Pages opened for this experiment on 2 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Compare Copilot Studio agent harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness)

The billing overview and the cost-management page were not opened. They are not cited as if they had been.

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

## Lead: GitHub Copilot harness

Use it when the security or API owner drops in a contract and then asks follow-up questions: which check failed, which operation was cited, what the proposed policy XML would contain.

Microsoft's overview says this harness can take a goal, break it into steps, call tools across connectors, knowledge, MCP, and connected agents, create and edit Word, Excel, PowerPoint, and PDF files, and support skills and memory. Agents and workflows on it use Copilot Credits. No quantity is copied. The comparison page says to choose it when the task is long-running or reasoning-intensive, and that customers should validate required features and channels as the experience matures. That is a maturity caveat. The overview does not mark the harness itself as preview.

This experiment's skills are under `skills/`. They tell the agent to call `review_tool_contract` and to stop. They do not tell it to apply the diff or publish a policy.

## Lighter path: standard harness

Use it when the owner wants the same topic every time: point at one contract, run the reviewer, show the JSON, stop.

The comparison page says to choose the standard harness when the work is relatively short and bounded. The guide is `copilot-studio/README.md`. There is no skill on that path.

## Cost and licensing

Only what the comparison page said on 2 November 2026. No prices are copied. The billing overview was not opened, so no diagram of ranges is transcribed.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What the comparison page says it is for | Long-running or reasoning-intensive tasks | Work that is relatively short and bounded |
| Billing, on that page | Usage-based billing for AI-based creation and use | Retains the pre-existing Copilot Studio licensing model |
| What this note does not claim | A credit quantity, a price, or a sentence from a billing page that was not opened | The same |

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/review.py` is the only producer of scores, findings, the proposed diff, and the stale-data flag.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy of this reviewer is A0 on both. Neither harness is given a tool that applies a diff, publishes a policy, approves a contract, deploys, writes a production record, or sends.
- The security/API owner approves the contract. The draft does not record that approval.

## Microsoft Foundry and API Management

The catalogue stack for G005 is Microsoft Foundry plus Azure API Management. `docs/foundry.md` is that path. It does not replace either harness. No Foundry resource and no API Management instance are created by this folder. The proposed policy is a sketch. It is not published.
