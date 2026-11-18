# Copilot Studio standard harness

A build guide. There is no solution to import.

Topics, in order:

1. **Policy question.** The employee asks what a leave policy says, and may name the date. The topic calls `explain()` and shows the JSON. It stops.
2. **Care route.** If `outcome` is `routed_to_human`, the topic says a person will help and does not read out a day count. It stops.
3. **Gap or bad input.** If the outcome is `not_covered` or `needs_human`, the topic says so, including a date or a balance that could not be read. It does not substitute today or zero. It stops.
4. **Stale or superseded.** If `may_be_relied_on` is false, the topic says why: past review, superseded on the as-of date, a stale pin, or an unverified source. It does not refresh the pin.

No topic books leave, writes a record, sends a message, or calculates pay. No topic treats "approved" in the question as the scope.

The system message is [system-prompt.md](system-prompt.md). The flow shape is [power-automate-flow.md](power-automate-flow.md).
