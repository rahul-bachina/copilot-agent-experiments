# Copilot Studio standard harness

This is the topic guide for the standard harness. It is not an importable solution. The runnable sample is `src/coordinator.py` on the synthetic request in `examples/`.

The harness overview opened on 26 November 2026 describes the standard harness as following the topics, prompts, and paths the maker defines. The comparison table points billing at "Licensing for agents powered by the standard harness". That licensing page was not opened. No price is stated here.

## Topics

1. **Assemble.** The user gives one synthetic request and the question date. The topic calls `assemble_pack`. It shows the cover note, the required approver references, and the content hash. It does not set a decision.
2. **Gaps.** If the outcome is `draft_with_gaps`, the topic lists the missing, stale, expired, unsigned, superseded, wrong-version, and conflicting items. The user can leave the conversation and come back with a new request. The topic does not fill a gap itself.
3. **Route.** If the outcome is `route_to_human`, the topic stops. A named approver from the pinned directory records that the route was seen, against the current hash, before any decision topic is offered.
4. **Decision.** The topic asks the named approver, who is not the requester, to approve, reject, or return. It calls `record_approver_decision` with the hash the draft returned. A pasted sentence is not accepted as that call.
5. **Human route.** Every topic offers a way to stop and hand the request to a person without a tool call.

The system prompt is [system-prompt.md](system-prompt.md). The flow note is [power-automate-flow.md](power-automate-flow.md).
