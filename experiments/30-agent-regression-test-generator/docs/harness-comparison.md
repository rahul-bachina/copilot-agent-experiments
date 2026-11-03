# Which harness runs this generator

Both harnesses call the same generator, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

This note is about running Experiment 30. It is not a decision about which harness an agent under test should use.

The page opened for the harness sentences on 3 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

Billing pages and licensing pages were not opened for this experiment. No price is copied. No credit quantity is copied.

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

## Lead: GitHub Copilot harness

Use it when the maintainer drops in a bundle and then asks follow-up questions: which case was skipped, which requirement a case traces to, what the pull-request text says.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The overview says agents and workflows on this harness use Copilot Credits. No quantity is copied. The overview does not mark the harness as preview.

This experiment's skills are under `skills/`. They tell the agent to call the generator and to stop. They do not tell it to merge, push, or edit the agent under test.

## Lighter path: standard harness

Use it when the maintainer wants the same topic every time: point at one bundle, draft the cases, show the JSON, stop.

Microsoft's overview describes the standard harness as following topics and rules the maker defines. The guide is `copilot-studio/README.md`. There is no skill on that path.

The page "Orchestrate agent behavior with generative AI", also opened on 3 November 2026, says it describes the standard harness. Generative orchestration selects topics based on the description of their purpose. Classic orchestration selects topics based on matching a user query with trigger phrases. This generator does not assign a routing weight. Whether the GitHub Copilot harness uses that selection rule was not on the generative-orchestration page. Unverified for that harness.

## What stays the same

- `agent-manifest.yaml` is the permission boundary for both.
- `src/generate.py` is the only producer of cases, fingerprints, traces, and the stale-data flag.
- `tests/` and `eval/evaluate.py` test that core. They do not score a harness model.
- Autonomy of this generator is A1 on both. Neither harness is given a tool that approves tests, opens a pull request, merges, pushes, edits the agent under test, writes a production record, or sends.
- A path that climbs, or an output directory inside the agent path, is refused before any file is written there.

## What this folder does not verify

- That memory can be switched off. The overview says the GitHub Copilot harness supports memory. The skills forbid storing the pack and the case inputs. An administrator control to disable memory was not found on the page opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A Data Loss Prevention policy is a deployment control, described in the security note, and is not applied here.
- A licence comparison. Those pages were not opened on 3 November 2026.
