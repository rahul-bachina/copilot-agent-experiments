# Microsoft Foundry

A path for a team that wants a short narrative around the options JSON. It is not a deployed project. No Foundry resource is created by this repository. The product name on the page opened on 27 October 2026 is Microsoft Foundry Agent Service.

The advisor in `src/advise.py` remains the system of record. A model does not choose a platform, does not set autonomy, and does not add a citation.

Page opened on 27 October 2026: [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/en-us/azure/foundry/agents/overview).

The page describes prompt agents, voice-based prompt agents, and hosted agents. Prompt agents are instructions, a model, and tools, run by Foundry with no application code. Hosted agents are your code, run as a container or from a zip file, with a managed endpoint, scaling, and a dedicated Microsoft Entra identity. Observability on the page includes tracing, evaluations, and Application Insights. Private networking is described for prompt agents. Hosted agents are described with a bring-your-own virtual network. Content filters are described as mitigating prompt injection, including cross-prompt injection.

The comparison table describes prompt-agent cost as per-call inference plus tool usage, and hosted agents as that plus container compute. It points to a pricing page for voice. That pricing page was not opened. No figure is stored here.

## Preview, as labelled on that page

- Agent optimizer is marked preview. It is not a reason to use this path.
- Voice-based prompt agents, and some related monitoring, evaluation, avatar, WebRTC, and telephony capabilities, are marked preview. The page says preview is not recommended for production workloads until support, security, compliance, and availability have been reviewed. This advisor does not select a voice agent.
- A2A protocol v1.0 is described as generally available. v0.3 remains in preview. This starter does not select either.

A list of UK regions was not on the page. Region availability is unverified.

## What the model may do

- Turn the JSON into a short brief for the architect, using only fields that are in the JSON.
- Repeat a reason and the source URL already on that reason.
- Point at `prompt_injection` and `do_not_rely` in the first paragraph.

## What the model must not do

- Invent a Microsoft Learn URL or a source id.
- Browse the web to update the catalogue.
- Select a platform, or change `selected` or `platform_selected`.
- Recommend autonomy A3, or change the recommended level.
- Mark the manifest approved, or enable a high-risk action.
- Deploy, send, or write a production record.
- Quote a price.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The architect supplies the use case and the as-of date.
2. Code, not the model, calls `advise`.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion schema rejects a response that contains a platform selection, autonomy A3, or a URL that is not in `sources`.
4. The architect sees the JSON and, beside it, the narrative. The narrative is still a draft.

There is no retrieval over the live Learn site. If a team adds retrieval, the corpus is the text already pinned in `src/sources.py`, not a crawl. A crawled page would bypass the last-verified date.

## Prompt Shields

[Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields), opened 27 October 2026. The page says they detect user prompt attacks and document attacks, and that the service behind them is Azure AI Content Safety. User prompt attack detection is on by default. Document attack detection is off by default. For Agent Service agents, document-attack scanning at the tool-response point is marked preview. Spotlighting is marked preview and is off by default. A cost note in that section is not copied. The page says Prompt Shields do not decide that content is harmful, accurate, grounded, or compliant.

Turn them on if a model sees the use case. They are not a substitute for the missing deploy tool, and they are not a substitute for the injection scan in `src/injection.py`. The local advisor does not call Prompt Shields.

## Deployment choices to confirm

- Region: not listed on the overview opened today. Unverified. Do not assume UK South or UK West from this note.
- Do not log the narrative in the trace. Log the case id, the catalogue `last_verified` values, and the as-of date.

The smoke test in `eval/smoke_report.json` is the deterministic checker. It is not a Foundry score. A live Foundry run has not been done.
