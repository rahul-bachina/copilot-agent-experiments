# Copilot Studio standard harness

This is a build guide, not an importable solution. The harness overview opened on 16 November 2026 says the standard harness follows the topics and rules the maker defines.

Use three topics. All three call `src/onboard.py`. None of them calls Microsoft Graph.

## 1. Explain and propose

Inputs are the synthetic space and the membership request. The topic calls `prepare_onboarding` and shows the JSON. It stops.

Do not map a phrase in the request onto an approval. Do not copy a field the JSON left out.

## 2. Hold

If the outcome is `above_justified_label`, `guest_refused`, `safeguarding_review`, or `needs_human`, the topic tells the person that a workspace owner has to review it. It does not call `apply_membership`.

## 3. Owner approval

This topic runs only when a separate approval object is present. The approver role is Workspace owner. It calls `apply_membership`. It shows `apply_outcome`, `applied`, and `live_graph_called`.

Owner rights and guest access are the booleans on that object. A true `external_share_approved` is ignored. The topic must not add a send action or a Graph connector.

The flow note is [power-automate-flow.md](power-automate-flow.md). The instructions for the maker are [system-prompt.md](system-prompt.md).
