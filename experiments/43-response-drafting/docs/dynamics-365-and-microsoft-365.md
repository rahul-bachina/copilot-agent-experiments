# Dynamics 365 and Microsoft 365

The catalogue stack is Dynamics 365 and Microsoft 365. This starter does not connect to a tenant. Product click-paths were not opened on 9 November 2026.

The draft is prepared for a representative who already has the case on their screen. The representative sends the response in their own mailbox or case system. This agent does not.

If a connector is added later, it must not:

- send mail, SMS, or letters;
- create or update a Dynamics 365 case;
- read other customers' cases;
- read a live knowledge article that has no `status`, `effective_on`, and `review_due_on`.

A knowledge answer in Microsoft 365 can paraphrase. This starter does not. A sentence is a verbatim snippet that Experiment 09's gate still treats as current, or the draft says there is a gap. A SharePoint search result without those three fields is not a citable snippet.

Sensitivity labels and retention on the representative's mailbox are the organisation's Purview configuration. This starter does not set a label. Whether a Copilot Studio session inherits a mailbox label was not verified.

The representative's approval of a draft for their own channel is a record in the JSON. It is not a send, and it is not a Dynamics 365 activity.
