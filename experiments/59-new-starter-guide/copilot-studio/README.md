# Copilot Studio standard harness

This is a build guide. It is not an importable solution.

Three topics call `draft_guide` and show the JSON. A fourth topic explains that sharing is not a topic the agent completes.

## Topics

1. **First week.** The user names a synthetic person id. The topic passes the pack, the directory, the HR scope, and the as-of date. It shows the checklist, the proposals, and the pins. It says the list is not shared.
2. **How do I.** The same call. If the JSON names a route, the topic stops at that route. It does not ask for a passport, a share code, or a health detail.
3. **Share this list.** The topic shows the checklist id, the item digest, and the directory line manager. It does not set `human_approval`. It does not send.

The system prompt is [system-prompt.md](system-prompt.md). The flow stops before any connector. See [power-automate-flow.md](power-automate-flow.md).

Knowledge sources are not configured in this starter. A tenant that later adds one should treat the pages as untrusted: an instruction inside a file is not followed, and a file above the ceiling is not quoted. Limits for SharePoint knowledge were not re-opened on 17 November 2026.
