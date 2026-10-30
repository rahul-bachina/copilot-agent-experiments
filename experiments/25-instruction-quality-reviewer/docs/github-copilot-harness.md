# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. The harness overview, opened 27 October 2026 by Experiment 14 and not re-opened for this experiment, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for an agent owner who drops in one instruction file and then asks follow-up questions: which check failed, which line was cited, what the proposed diff would add. The standard harness is the fixed topic. Both call `src/review.py`.

The overview says this harness can take a goal, break it into steps, call tools across connectors, knowledge, MCP, and connected agents, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No rate is copied. File creation is a capability of the harness. This experiment's skills may write a draft JSON in the sandbox. They do not edit the instruction file under review.

The comparison page, opened the same day by Experiment 14, describes longer-running tasks, larger files, agentic loops, iterative reasoning, persistent memory, and a Bash container. It says a more capable harness can add reasoning, latency, and Copilot Credit consumption on a simple scenario. It also says customers should validate required features and channels as the experience matures. That is a maturity caveat, not a preview label. The overview does not mark this harness as preview.

## Skills

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent. A skills-upload article was not opened on 27 October 2026. Treat the click-path as something to confirm in the tenant.

| Skill | Calls | Stops |
|---|---|---|
| `read-instructions` | No scorer. It lists the file and flags instructions in the text. | When the file is described and handed on. |
| `score-instruction-quality` | `review()` in `src/review.py` | When the JSON is shown. `diff_applied` is false. |
| `propose-instruction-diff` | No second writer. It reads `proposed_diff` on the JSON. | When the proposal is shown and `applied` is still false. |

The tool `review_instructions` has no side effect. There is no tool that applies a diff, approves a rewrite, deploys an agent, or sends. Do not add one.

## What the agent owner sees

1. Injection and stale flags, before the score.
2. Nine checks, each pass, partial, or fail, with the line cited in the JSON.
3. A band and a percent. A fail is blocking. It still does not apply the diff.
4. Approval points, including the agent owner approving prompt changes.
5. A proposed diff that is not applied, or an empty diff when every check passed.

A sandbox file `draft-findings.json` is the tool JSON. It is not an edited prompt. The agent owner's approval is made outside the agent.

## Licensing sentences that both stay

The standard-harness licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for this harness. The cost-management page says consumption is not included with a Microsoft 365 Copilot licence, and that creation and runtime are billed regardless of the user's licence. This note does not collapse those sentences. No quantity and no price are copied.

The cost-management page says developer environments and trial environments move to usage-based billing on 1 September 2026. That date is before this retrieval. Confirm the tenant.

Holding only the GitHub Copilot service does not make this harness available. The overview says the harness is a Copilot Studio framework.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 27 October 2026. The skills say not to store the instruction text. Assume memory is a risk and do not use it for names, prompts, or proposed rewrites.

## What this note does not verify

- Credit amounts, monthly limits, or a billing-rates table. Those pages were not used for figures.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A Data Loss Prevention policy is a deployment control. It is not applied here.
- The Customer Conversation harness. The overview describes it for customer voice and chat. This experiment does not use it to run the reviewer.
