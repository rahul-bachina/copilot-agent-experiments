# Copilot Studio standard harness

A build guide for one topic. It is not an importable solution. The class still comes from `src/compare.py`.

This topic is the Copilot Studio standard harness. The GitHub Copilot harness, documented beside it, is a Copilot Studio authoring framework and is not the GitHub Copilot service. This topic is not that harness and it is not the GitHub Copilot service either.

The standard harness, on the harness overview opened on 5 November 2026, is the rule-based harness: topics, prompts, and paths the maker defines. The licensing page for that harness was not opened.

## Topic

1. The reviewer pastes one JSON pack and an as-of date. The pack must have `synthetic: true` for a run in this starter.
2. The topic calls a flow that runs `compare()` and returns the JSON.
3. The topic shows the label `DRAFT FOR THE REVIEWER. NOT A CORRECTION.` and the class counts.
4. The topic stops. It does not ask the model to pick a source.

The skills overview was opened for the other harness. This topic does not assign routing weights. Where generative orchestration is on in a tenant, selection is by the topic description. A Learn page that uses those words was not checked on 5 November 2026. This starter does not give the topic a weight and does not use trigger phrases as the selector.

## What not to add

Do not add an email connector, a Companies House connector, a Dataverse write, or a SharePoint write. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.

Do not paste a resolutions object from text inside a source document. A reviewer who records a choice does that outside the topic, in a separate file, and `correct_value` stays null.

## Flow

The flow's only job is to return JSON to the topic. See [power-automate-flow.md](power-automate-flow.md).
