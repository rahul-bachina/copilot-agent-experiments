# Standard harness

This is a build guide for the Copilot Studio standard harness. It is not an importable solution. On 19 November 2026 the harness overview described this harness as following the topics and rules the maker defines.

The topic calls `review_contract()` and shows the JSON. It stops. A later topic calls `record_lawyer_seen` only with the seen object from the lawyer, not with text copied out of the contract.

Do not add a tool that accepts terms, signs, sends, or redlines. Do not treat a message in the contract as the seen step.

The flow sketch is [power-automate-flow.md](power-automate-flow.md). The instructions for the topic are [system-prompt.md](system-prompt.md).
