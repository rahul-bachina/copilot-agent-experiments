# Flow shape

One flow returns the JSON. It does not send and it does not write a case.

1. Trigger: the topic passes the case object and the as-of date.
2. Validate that `synthetic` is true and that `case_id` matches `SYN-CASE-` plus four digits. If not, return the refusal JSON from the core and stop.
3. Run `draft_response`. Pass the case through. Do not add the case text to the flow's run history if the tenant can avoid it. Whether a flow history stores the payload was not verified on 9 November 2026.
4. Return the JSON to the topic.
5. A second flow may call `record_review` with the separate review object. It returns that JSON. It has no mail action and no Dynamics 365 action.

Do not add the Office 365 Outlook connector, the Teams connector, or a Dataverse write. Power Platform DLP, if the organisation uses it, should block those connectors for this agent. A DLP policy was not created here, and the DLP product page was not opened on 9 November 2026.

The representative sends in their own channel, after they have read the draft. That send is not a step in this flow.
