# Which harness runs this test agent

Both harnesses call the same runner, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

This note is about running Experiment 28. It is not a decision about which harness an agent under test should use.

The page opened for the harness sentences on 2 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

Billing pages and licensing pages were not opened for this experiment. No price is copied. No credit quantity is copied. Experiment 25's stored billing sentences are not repeated here.

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

## Lead: GitHub Copilot harness

Use it when the security reviewer drops in a sandbox bundle and then asks follow-up questions: which case failed, which OWASP title this starter mapped, which file was read.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The overview says agents on this harness use Copilot Credits. No quantity is copied. The overview does not mark the harness as preview.

This experiment's skills are under `skills/`. They tell the agent to call `run_sandbox` and to stop. They do not tell it to assess a finding, apply remediation, or publish a payload.

## Lighter path: standard harness

Use it when the security reviewer wants the same topic every time: point at one sandbox bundle, run the suite, show the JSON, stop.

Microsoft's overview describes the standard harness as following topics and rules the maker defines. The guide is `copilot-studio/README.md`. There is no skill on that path.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/run.py` is the only producer of case results, findings, OWASP titles, and the stale-data flag.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy of this runner is A0 on both. Neither harness is given a tool that assesses findings, applies remediation, publishes a payload, writes a production record, or sends.
- A URL and `production: true` are refused before any case runs.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing fixture text and findings. An administrator control to disable memory was not found on the page opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A Data Loss Prevention policy is a deployment control, described in the security note, and is not applied here.
- A licence comparison between the two harnesses. Those pages were not opened on 2 November 2026.
- Customer Conversation harness. The overview describes it for customer voice and chat. This runner does not use it.
