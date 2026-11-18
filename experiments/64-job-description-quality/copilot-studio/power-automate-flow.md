# Flow sketch

Not a deployed flow.

1. The recruiter submits one draft, the guide, and the question date.
2. A flow calls `review_draft()` and returns the JSON to the topic.
3. The topic stops. It does not post to a jobs board.
4. A later flow may call `record_suggestion_decision()`, `record_hr_seen()`, or `record_final_wording()` when the person submits the decision object.
5. The flow does not send email and does not write an applicant-tracking system.

A sentence in the draft is not a step in this flow.
