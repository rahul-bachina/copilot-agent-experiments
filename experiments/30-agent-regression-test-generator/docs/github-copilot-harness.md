# GitHub Copilot harness

The catalogue stack for G008 is Microsoft Foundry plus GitHub. The Copilot Studio GitHub Copilot harness is the reasoning-heavy build of this experiment. That harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service.

The harness overview was opened on 3 November 2026. It says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. This repository cannot see a tenant's traffic.

## Skills

| Skill | Job | Stops when |
|---|---|---|
| `read-agent-pack` | Read the bundle the maintainer supplied | The index is shown |
| `draft-regression-cases` | Call `draft_regression_cases` and show the JSON | The counts and traces are shown |
| `show-draft-pr` | Show `draft_pr` | The text is shown |

The skills do not tell the agent to merge, push, or edit a file. `maintainer_approved` stays false. The maintainer approves the tests outside the agent.

Skill descriptions are a single line and say when to use the skill. They are not trigger phrases, and this generator does not weight them. The standard-harness generative-orchestration page, opened the same day, says selection uses the description of a topic's purpose. That page says it describes the standard harness. It does not say the GitHub Copilot harness uses the same rule. Unverified for this harness.

## Tools

`schema/tools.json` is the contract. `draft_regression_cases` reads and returns JSON. The tools that would approve tests, open a pull request, merge, push, or edit the agent always raise, and the agent must not call them.

A file written with `--out-dir` is a copy of the draft for that command. It is not an edit of the agent under test. The command refuses an output directory inside that agent's path.

## Memory and files

The overview says this harness supports memory and file creation. An administrator control to turn memory off was not on the page opened on 3 November 2026. The skills say not to store the pack or the case inputs. The overview does not mark the harness as preview.

## What this harness does not decide

It does not decide that a drafted case passes. It does not open, push, or merge a pull request. It does not upload the Foundry queries file. It does not approve a manifest when Experiment 03 is called.
