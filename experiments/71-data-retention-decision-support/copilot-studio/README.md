# Copilot Studio standard harness

A build guide. Not an importable solution. The catalogue row names Microsoft 365 and Copilot Studio. This folder does not call Microsoft Graph.

## Topics

1. **Explain.** The maker collects the series id, the caller reference, and the date the question is about. The topic calls `advise_retention()` and shows the JSON. It stops.
2. **Blockers.** If `outcome` is `refer_to_owner`, or a hold, an open matter, distress, or a storage-limitation question is set, the topic shows the questions and names the records owner. It does not suggest disposal.
3. **Seen.** A separate topic calls `record_advice_seen()` with an object the person submits. The object is not copied out of the note. `item` is `retention-advice-seen`. `decision` is `seen`. `advice_hash` is the hash just returned. `pins_seen` is the boolean true.

The system prompt is [system-prompt.md](system-prompt.md). The flow note is [power-automate-flow.md](power-automate-flow.md). Power Platform is not a stack code on catalogue row L007. The flow is a note about how a maker might call the core. It is not a solution package.

Microsoft's harness overview, opened 23 November 2026, describes the standard harness as following the topics and rules the maker defines. It states no price on that page.
