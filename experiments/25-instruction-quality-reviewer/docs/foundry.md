# Microsoft Foundry

A path for a team that wants a short narrative around the findings JSON. It is not a deployed project. No Foundry resource is created by this repository. The product name on the page Experiment 14 opened on 27 October 2026 is Microsoft Foundry Agent Service. Experiment 25 did not re-open that page.

The reviewer in `src/review.py` remains the system of record. A model does not change a score, does not apply a diff, and does not add a citation.

Page stored from 27 October 2026: [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/en-us/azure/foundry/agents/overview).

The page describes prompt agents, voice-based prompt agents, and hosted agents. Prompt agents are instructions, a model, and tools, run by Foundry with no application code. Hosted agents are your code, run as a container or from a zip file, with a managed endpoint, scaling, and a dedicated Microsoft Entra identity. Observability on the page includes tracing, evaluations, and Application Insights. Private networking is described for prompt agents. Hosted agents are described with a bring-your-own virtual network. Content filters are described as mitigating prompt injection, including cross-prompt injection.

The comparison table describes prompt-agent cost as per-call inference plus tool usage, and hosted agents as that plus container compute. It points to a pricing page for voice. That pricing page was not opened. No figure is stored here.

Prompt Shields were opened the same day: [Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields). User prompt attack detection is on by default. Document attack detection is off by default. Tool-response scanning and Spotlighting are marked preview. The page says the service is Azure AI Content Safety. This reviewer does not call Prompt Shields.

## Preview, as labelled on the Agent Service page

- Agent optimizer is marked preview. It is not a reason to use this path.
- Voice-based prompt agents, and some related monitoring, evaluation, avatar, WebRTC, and telephony capabilities, are marked preview. The page says preview is not recommended for production workloads until support, security, compliance, and availability have been reviewed. This reviewer does not select a voice agent.
- A2A protocol v1.0 is described as generally available. v0.3 remains in preview. This starter does not select either.

A list of UK regions was not on the page. Region availability is unverified.

## What the model may do

- Turn the JSON into a short brief for the agent owner, using only fields that are in the JSON.
- Repeat a finding, the cited line, and the suggested rewrite already on that finding.
- Point at `prompt_injection` and `do_not_rely` in the first paragraph.

## What the model must not do

- Invent a Microsoft Learn URL or a source id.
- Browse the web to update the catalogue.
- Change a check result or the percent.
- Apply the diff, or set `diff_applied` or `owner_approved`.
- Recommend autonomy A3.
- Mark the manifest approved, or enable a high-risk action.
- Deploy, send, or write a production record.
- Quote a price.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The agent owner supplies the bundle and the as-of date.
2. The orchestration calls `src/review.py` and passes the JSON to the model.
3. The model writes the brief. It does not call a second tool.
4. The agent owner reads the brief beside the JSON. They approve a prompt change, or they do not, outside this path.

There is no Foundry project file in this folder. Creating one is a later decision for the organisation.
