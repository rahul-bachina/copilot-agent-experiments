# Which harness to use

Both harnesses are Microsoft Copilot Studio. Both call `draft_memo()` and stop. Neither approves or declines credit, sets a limit, contacts the customer or a bureau, posts a core banking or CRM system, or files a SAR. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. The harness overview opened on 6 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

## Standard harness

Use this when the credit officer wants one topic: paste a synthetic pack, receive the JSON, stop. The maker defines the topic. See [../copilot-studio/README.md](../copilot-studio/README.md).

The harness overview uses "standard harness" for a rule-based agent. The generative-orchestration guidance opened on 6 November 2026 uses the words "Standard harness (planner)" for an LLM planning layer. Those two uses were not identified as the same component on either page. Treating them as the same component is unverified.

## GitHub Copilot harness

Use this when the credit officer wants the draft explained in steps: one skill drafts, one skill checks a proposed sentence, one skill lists sections that are not stated. See [github-copilot-harness.md](github-copilot-harness.md) and [../skills/](../skills/).

The overview says this harness can take a goal, break it into steps, and use skills and memory, and that it can work with Word, Excel, PowerPoint, and PDF inside a sandbox. This starter does not read those file types. It reads JSON the credit officer already split into lines. It does not store the pack in memory.

The overview says agents and workflows on that harness use Copilot Credits. The billing page was not opened. No prices are stated here. The overview did not mark the harness itself as preview.

The generative-orchestration guidance says the planner can invoke a topic when its described purpose matches the need, and also by trigger phrases, and that names carry more weight than descriptions. It does not describe numeric routing weights. These skills do not list trigger phrases and do not assign routing weights. Whether that planner is the GitHub Copilot harness selector was not stated on the harness overview. That link is unverified.

## Customer Conversation harness

The overview also describes a Customer Conversation harness for voice and chat. It is not built here. A credit pack does not belong on a public chat.

## What neither harness does

Neither harness decides the credit. Autonomy stays A1. A3 is never a recommendation. Microsoft Foundry is not called. Microsoft Fabric is not written. Product pages for both were not opened.
