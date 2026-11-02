# GitHub Copilot harness

The catalogue stack for G004 is Copilot Studio on the GitHub Copilot harness. That harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service.

Experiment 14 opened the harness overview on 27 October 2026. Experiment 26 did not re-open it. The stored sentence says customer data is not sent to the GitHub Copilot service when the agent runs in Copilot Studio. This repository cannot see a tenant's traffic.

## Skills

| Skill | Job | Stops when |
|---|---|---|
| `read-skill-catalogue` | Read the files the maintainer supplied | The files are in hand |
| `score-skill-routing` | Call `evaluate_skill_routing` and show the JSON | The JSON is shown |
| `propose-description-diff` | Show `proposed_diff` | The diff is shown, or there is no diff |

The skills do not tell the agent to edit a skill. `applied` stays false. The maintainer validates routing tests outside the agent.

## Tools

`schema/tools.json` is the contract. `evaluate_skill_routing` reads and returns JSON. The tools that would record validation, apply a diff, deploy, or send always raise, and the agent must not call them.

A sandbox file such as `draft-routing.json` is a copy of the JSON for that conversation. It is not an edit of a `SKILL.md` in the repository.

## Memory and files

The overview says this harness supports memory and file creation. An administrator control to turn memory off was not on the page opened on 27 October 2026. The skills say not to store the skill text or the utterances. The comparison page says customers should validate features and channels as the experience matures. That is a maturity caveat. The overview does not mark the harness as preview.

## Licensing sentences that are not merged

The standard-harness licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for the GitHub Copilot harness. The cost-management page says consumption is not included with a Microsoft 365 Copilot licence. Both sentences are stored from 27 October 2026. This note does not pick one. No quantity is copied.

## What this harness does not decide

It does not decide which skill a live Copilot Studio agent would select. The JSON is the local router. It does not select a platform when Experiment 14 is called. It does not approve a manifest when Experiment 03 is called.
