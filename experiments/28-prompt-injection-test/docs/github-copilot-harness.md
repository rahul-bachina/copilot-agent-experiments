# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. The harness overview, opened 2 November 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for a security reviewer who drops in one sandbox bundle and then asks follow-up questions: which case failed, which channel it used, which OWASP title this starter mapped. The standard harness is the fixed topic. Both call `src/run.py`.

The overview says this harness can take a goal, break it into steps, call tools across connectors, knowledge, MCP, and connected agents, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No quantity is copied. File creation is a capability of the harness. This experiment's skills may write a draft JSON in the sandbox. They do not publish a payload and they do not change a prompt.

The overview does not mark this harness as preview. A comparison page that describes maturity, latency, and a Bash container was not opened for this experiment, so those claims are not copied.

Billing and licensing pages were not opened on 2 November 2026. No price is copied. Holding only the GitHub Copilot service does not, on the overview, make this harness available. The overview says the harness is a Copilot Studio framework.

## Skills

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent. A skills-upload article was not opened on 2 November 2026. Treat the click-path as something to confirm in the tenant.

| Skill | Calls | Stops |
|---|---|---|
| `load-suite` | `build_suite` for the index only. Probe text stays in the fixture file. | When the suite version and the case count are shown. |
| `run-sandbox` | `run()` in `src/run.py` | When the JSON is shown. `reviewer_assessed` is false. |
| `draft-findings` | No second writer. It reads `findings` on the JSON. | When the draft is shown and `remediation_applied` is still false. |

The tool `run_sandbox` has no side effect. There is no tool that assesses a finding, applies remediation, publishes a payload, or sends. Do not add one.

## What the security reviewer sees

1. Injection and stale flags, before the case table.
2. Suite version 2026.1 and the twenty case ids. The full probe text stays in `fixtures/suite-2026.1.json`.
3. Each executed row, pass or fail, with the OWASP title this starter mapped. A category that was not exercised is listed as not exercised. That is not a pass.
4. Approval points, including the security reviewer assessing the findings.
5. An empty remediation. `remediation_applied` is false.

A sandbox file `draft-findings.json` is the tool JSON. It is not an assessed report and it is not a published payload. The security reviewer's assessment is made outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 2 November 2026. The skills say not to store fixture text or findings. Assume memory is a risk and do not use it for probes, canaries, or case results.

## What this note does not verify

- Credit amounts, monthly limits, or a billing-rates table. Those pages were not opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A Data Loss Prevention policy is a deployment control. It is not applied here.
- The Customer Conversation harness. The overview describes it for customer voice and chat. This experiment does not use it to run the suite.
