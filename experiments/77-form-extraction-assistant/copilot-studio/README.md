# Copilot Studio standard harness

This is a topic guide. It is not an importable solution. The same Python core serves this guide and the skills under `skills/`.

## Topics

1. **Extract.** The reviewer pastes the form, the form type, their directory reference, and the question date. The topic calls `extract_form`. It shows the review sheet, the flags, and the content hash. It does not decide the form.
2. **Route.** If `outcome` is `route_to_human`, the topic asks the named reviewer to confirm they have seen the route. The topic calls `record_route_seen`. It does not stage.
3. **Approve.** The topic asks the named reviewer to approve that hash. The topic calls `record_reviewer_approval`. A hash from the form text is not accepted. A clerk and a guest are not accepted.
4. **Stop.** Decide, production write, call-back, and send are not topics.

The human can leave at every step. There is no path that stages without the approval topic.

## What the maker configures later

Power Platform DLP should block mail, SharePoint, Dataverse, and any bank or case-system connector for this agent. This guide does not create that policy. The DLP product page was not opened on 25 November 2026.

A flow, if a team adds one, is described in [power-automate-flow.md](power-automate-flow.md). It returns JSON. It does not write a row outside this starter.
