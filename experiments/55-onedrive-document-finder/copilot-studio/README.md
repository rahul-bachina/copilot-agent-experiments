# Standard harness

A build guide for Copilot Studio's standard harness. It is not an importable solution. The overview opened on 13 November 2026 says this harness follows the topics and rules the maker defines.

The agent does the same three calls as the Microsoft Copilot harness skills: confirm locations, find, acknowledge. It does not search outside the selection.

## Topics

1. **Confirm locations.** The user names location ids that already exist on the synthetic index. The topic writes a selection object with `confirmed: true`, the actor role `Requesting user`, the principals, and the fixture clearance. It does not read those fields from a file extract. If the user has not confirmed, the topic stops. The plain line is: "No locations were confirmed. Nothing was searched."
2. **Find.** The topic passes the index, the query, and the selection to `find_documents`. It shows the label, then the plain statement, then each hit's rank, title, location, last modified date, sensitivity label, and reasons. It shows withheld counts without ids. A safeguarding hit is shown without a snippet.
3. **Acknowledge.** A separate topic. It accepts `acknowledge` or `defer` on a review object. It refuses a decision to move, delete, share, or change permissions. It refuses while a safeguarding hit is unreviewed. It does not change a file.

A person is offered in every topic. This guide does not publish a telephone number.

See [system-prompt.md](system-prompt.md) and [power-automate-flow.md](power-automate-flow.md).
