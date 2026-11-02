# Microsoft Foundry

Catalogue stack for G006 is Microsoft Foundry plus Copilot Studio on the GitHub Copilot harness. This folder does not create a Foundry resource, does not call a model, and does not call the AI Red Teaming Agent. `foundry_red_team_called` stays false.

Two pages were opened on 2 November 2026. The runner does not download them again.

- [AI Red Teaming Agent](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent)
- [Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields)

## AI Red Teaming Agent

The page says the agent uses PyRIT and Microsoft Foundry Risk and Safety Evaluations to scan, score Attack Success Rate, and report. It says that rate can be non-deterministic and that results should be reviewed before mitigation.

Agentic categories named for cloud runs include prohibited actions, sensitive data leakage, and task adherence (cloud only), plus indirect prompt injection (XPIA). Supported targets named on the page are Foundry-hosted prompt agents and container agents with Azure tool calls. Non-Foundry agents are listed as not supported.

Cloud regions named on the page: East US 2, France Central, Sweden Central, Switzerland West, and US North Central. A UK region was not in that list. UK region availability for that feature is unverified. The regions were not tested from this repository.

This starter does not call the agent, does not import PyRIT, and does not compute Attack Success Rate. A pass or a fail in `eval/smoke_report.json` is the local scorer on synthetic fixtures. It is not that rate.

The page says to review results before mitigation and to use a non-production environment. That matches the human checkpoint in this starter: the security reviewer assesses the findings. Pointing the hosted agent at a Foundry target is a later step, outside this folder, and only for a target the page says it supports.

The attack strategies named on that page, including Base64, ROT13, and jailbreak, are product documentation. Suite 2026.1 does not execute those strategies. Its encoding cases are transforms of the synthetic marker `SYN-MARKER-OVERRIDE` only.

## Prompt Shields

The page says user prompt attack detection is on by default and document attack detection is off by default. Tool-response scanning for agents, and Spotlighting, are marked preview. The page says the service is powered by Azure AI Content Safety, which is the name written there.

This starter does not call Prompt Shields. The local scan in `src/injection.py` and the wording rules in `src/surface.py` are not a substitute for that service, and that service is not a substitute for the security reviewer's assessment.

## Where Foundry would sit later

A team that already hosts a non-production agent in Microsoft Foundry can treat this starter as a fixed first reading, then decide whether to run the hosted red-teaming agent against that Foundry target. This folder does not make that call. It does not claim the local suite covers the categories the Foundry page lists, and it does not claim a Foundry score for the experiments in this repository. Those experiments are files and local Python. The Foundry page lists non-Foundry agents as not supported.

## What this note does not claim

- That Attack Success Rate from a Foundry run would match suite 2026.1.
- That a UK region can host the cloud red-teaming agent. The page opened on 2 November 2026 did not name one.
- That Prompt Shields, Spotlighting, or tool-response scanning are configured here.
- A price, a credit quantity, or a quota.
