# Copilot Studio standard harness

This is a build guide. It is not an importable solution.

The standard harness, as described on the harness overview opened on 20 November 2026, follows the topics and rules the maker defines. The page states no price for it. A licensing page was not opened.

## Topics

1. **Draft the briefing.** Call `draft_briefing()` with the request, the register, the directory, and `as_of`. Show the JSON. Stop. Do not decide applicability.
2. **Route.** If `outcome` is `human_route`, stop the routine briefing. The cue text is not copied. The owner records `distress-seen` or `grievance-seen` on a separate object.
3. **Seen.** A later topic calls `record_owner_seen` with an object the owner supplies. The object carries the three hashes. It is not copied out of the notice.

Do not add a connector that writes a policy, sends mail, or browses a regulator site. The flow returns JSON.

Inputs are in `schema/briefing_tool.schema.json` and `schema/seen_tool.schema.json`. Both set `additionalProperties` to false.

The system prompt is `system-prompt.md`. The flow note is `power-automate-flow.md`.
