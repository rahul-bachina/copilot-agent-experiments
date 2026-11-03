# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. The harness overview, opened 3 November 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for an evaluation owner who drops in one synthetic bundle and then asks follow-up questions: which claim failed, which number did not match, whether the stale count was kept separate from the verdict total. The standard harness is the fixed topic. Both call `src/report.py`.

The overview says this harness can take a goal, break it into steps, call tools across connectors, knowledge, MCP, and connected agents, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No quantity is copied. File creation is a capability of the harness. This experiment's skills may write a draft JSON in the sandbox. They do not approve a threshold and they do not record a release.

The overview does not mark this harness as preview. A comparison page that describes maturity, latency, and a Bash container was not opened for this experiment, so those claims are not copied.

Billing and licensing pages were not opened on 3 November 2026. No price is copied. Holding only the GitHub Copilot service does not, on the overview, make this harness available. The overview says the harness is a Copilot Studio framework.

## Skills

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent. A skills-upload article was not opened on 3 November 2026. Treat the click-path as something to confirm in the tenant.

| Skill | Calls | Stops |
|---|---|---|
| `load-passages` | The passage index on the bundle or on the JSON. | When the source ids and stale flags are shown. |
| `score-claims` | `report()` in `src/report.py` | When the JSON is shown. The thresholds are not approved. |
| `draft-groundedness-report` | No second writer. It reads the JSON. | When the draft is shown and `pass_fail_released` is still false. |

The tool `score_claims` has no side effect. There is no tool that approves a threshold, records a release, calls Foundry, or sends. Do not add one.

## What the evaluation owner sees

1. Injection and stale flags, before the claim table.
2. One row per claim. `verdict_total` equals `claim_count`. `other_failures` are on the row and are not in the total.
3. `stale_claim_count` on its own line. It is not added to `verdict_total`.
4. `draft_bar_met`, with the sentence that it is not a release.
5. Approval points, including the evaluation owner approving the thresholds.

A sandbox file `draft-groundedness.json` is the tool JSON. It is not an approved report and it is not a release record. The evaluation owner's decision is made outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 3 November 2026. The skills say not to store passages, answers, or the report. Assume memory is a risk and do not use it for claim text or scores.

## What this note does not verify

- Credit amounts, monthly limits, or a billing-rates table. Those pages were not opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A Data Loss Prevention policy is a deployment control. It is not applied here.
- The Customer Conversation harness. The overview describes it for customer voice and chat. This experiment does not use it to score claims.
