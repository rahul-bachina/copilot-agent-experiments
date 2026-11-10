# Copilot Studio standard harness

A build guide. It is not an importable solution. There is no `.zip` in this folder.

One topic. The technician pastes one synthetic pack and types the as-of date. The topic calls `prepare_brief` in `src/prepare.py` and shows the JSON. It stops.

The harness overview opened on 10 November 2026 says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are "not a focus". That is the shape of this topic.

Do not add a skill to this harness. Skills belong on the GitHub Copilot harness, which is a different Copilot Studio framework and not the GitHub Copilot service. See [../docs/harness-comparison.md](../docs/harness-comparison.md).

## Topic shape

1. Ask for the pack and the as-of date.
2. Call the Python core. Do not ask a model to decide the holds.
3. Show `DRAFT FIELD BRIEF FOR TECHNICIAN CONFIRMATION`.
4. If `prompt_injection.detected` is true, say the instruction was not followed and still show the holds.
5. Stop. The technician confirms on a separate review object, outside the topic's free text. See [power-automate-flow.md](power-automate-flow.md).

The topic has no connector to a scheduling system, a mailbox, or a work-order write. Do not add one. The licensing article for the standard harness was not opened on 10 November 2026. This guide does not state a price.

## What this folder does not verify

The authoring click-path was not exercised in a tenant. How a tenant selects a topic when generative orchestration is on was not opened. This starter does not give the topic a weight.
