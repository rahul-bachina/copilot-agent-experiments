# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. The harness overview, opened for this experiment on 2 November 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for a security or API owner who drops in one contract and then asks follow-up questions: which check failed, which operation was cited, what the proposed policy would contain. The standard harness is the fixed topic. Both call `src/review.py`.

The overview says this harness can take a goal, break it into steps, call tools across connectors, knowledge, MCP, and connected agents, create and edit Word, Excel, PowerPoint, and PDF files, and support skills and memory. Agents and workflows on it use Copilot Credits. No quantity is copied. The overview does not mark the harness itself as preview. File creation is a capability of the harness. This experiment's skills may write a draft JSON or a policy sketch in the sandbox. They do not modify the contract under review and they do not publish a policy.

The comparison page, opened the same day, says to choose this harness when the task is long-running or reasoning-intensive, and to choose the standard harness when the work is relatively short and bounded. It says customers should validate required features and channels as the experience matures. That is a maturity caveat, not a preview label.

## Skills

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent. A skills-upload article was not opened on 2 November 2026. Treat the click-path as something to confirm in the tenant.

| Skill | Calls | Stops |
|---|---|---|
| `read-tool-contract` | No scorer. It lists the file and flags instructions in the text. | When the file is described and handed on. |
| `score-tool-contract` | `review()` in `src/review.py` | When the JSON is shown. `diff_applied` and `policy_published` are false. |
| `propose-contract-diff` | No second writer. It reads `proposed_diff` on the JSON. | When the proposal is shown, `applied` is still false, and `published` is still false. |

The tool `review_tool_contract` has no side effect. There is no tool that applies a diff, publishes a policy, approves a contract, deploys an agent, or sends. Do not add one.

## What the security/API owner sees

1. Injection and stale flags, before the score.
2. Nine checks, each pass, partial, or fail, with the operation cited in the JSON.
3. A band and a percent. A fail is blocking. It still does not apply the diff.
4. Approval points. The security/API owner approves the contract, and approves an API Management policy change before it is published.
5. Proposed contract notes and, where a check is not a pass, policy XML that is not published. Placeholders stay as `SET_BY_API_OWNER` and `SET_RESOURCE_APPLICATION_ID`.

A sandbox file `draft-findings.json` is the tool JSON. It is not a modified contract. The owner's approval is made outside the agent.

## Licensing, as opened on 2 November 2026

The comparison page says GitHub Copilot harness solutions use usage-based billing for AI-based creation and use, and that standard harness agents retain the pre-existing Copilot Studio licensing model. No rate is copied. The billing overview and the cost-management page were not opened for this experiment. This note does not repeat sentences Experiment 14 stored on 27 October 2026 as if they had been re-opened.

Holding only the GitHub Copilot service does not make this harness available. The overview says the harness is a Copilot Studio framework.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 2 November 2026. The skills say not to store the contract, a key, or a proposed policy. Assume memory is a risk and do not use it.

## What this note does not verify

- Credit amounts, monthly limits, or a billing-rates table. Those pages were not opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A Data Loss Prevention policy is a deployment control. It was not opened and it is not applied here.
- The Customer Conversation harness. This experiment does not use it to run the reviewer.
