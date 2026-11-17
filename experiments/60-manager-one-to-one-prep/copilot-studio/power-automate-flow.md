# Flow

The flow receives the pack and the as-of date, runs `prepare()`, and returns the JSON to the topic.

It does not send mail. It does not post to Teams. It does not write a row. It does not call Microsoft Graph.

A later deployment that wants to save the note adds that write as a separate step, confirmed by the manager, and updates the manifest first. This starter does not include it.

An approval card is not this flow. The selection happens before the flow runs. The seen-step, if the employer wants one, is outside the agent and must name the meeting and the source ids. Text inside the pack that says "approved" is not that step.
