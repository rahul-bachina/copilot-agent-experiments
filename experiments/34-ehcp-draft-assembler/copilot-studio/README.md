# Copilot Studio standard harness

One topic. The caseworker points at a synthetic advice bundle and an as-of date. The topic calls `assemble_ehcp_draft` and shows the JSON. Then it stops.

The standard harness, on the overview opened on 4 November 2026, follows the topics and rules the maker defines. This topic is that shape. There is no skill on this path. The GitHub Copilot harness for the same draft is `docs/github-copilot-harness.md`. That harness is not the GitHub Copilot service.

The billing overview says the standard harness starts billing after publish. The licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for the GitHub Copilot harness, and, in a separate sentence, that with that licence some answer types in Copilot Chat, Teams, or SharePoint do not count against the message pack or meter. Those two sentences are not merged. No quantity is copied. The cost-management page was not opened for this experiment, so this note does not repeat a sentence from it. This starter does not look up a licence.

A Learn page on generative orchestration was not opened on 4 November 2026. How a tenant selects a topic is unverified. This topic does not carry a weight. Where generative orchestration is enabled, Microsoft describes selection by the topic description. That description was not re-checked for this experiment.

## Build it

1. Create an agent on the standard harness. Paste `copilot-studio/system-prompt.md` as the instructions.
2. Add one tool, `assemble_ehcp_draft`, that runs `src/assemble.py` with the bundle and the as-of date. The contract is `schema/tools.json`.
3. Do not add a connector to email, a parent portal, a school system, Dataverse, or a local authority case system. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Ask for the bundle and the as-of date. In this repository the sample is `examples/sample_bundle.json`. It has `synthetic` true. If a file is not marked synthetic, the tool returns a refusal and no quote.
5. Show the label `DRAFT FOR CASEWORKER — NOT A PLAN`. Say that the caseworker authors the final text.
6. Stop. Do not offer to send the draft or to fill section I.

## Inputs

| Input | Required | What it is |
|---|---|---|
| `bundle` | Yes | One JSON object. `synthetic` must be true. `child_ref` is `Child` and one letter. |
| `as_of` | Yes | The date the caseworker types, `YYYY-MM-DD`. |

The sign-off file is not an input to this topic. Export is a separate command the caseworker runs. The agent does not collect `final_text`.

## What this topic does not do

It does not decide needs, provision, placement, or outcomes. It does not edit the final plan. It does not send anything. It does not check the local template. It does not attach section K appendices.
