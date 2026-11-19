# Flow sketch

Not a deployed flow.

1. The recruiter submits the synthetic request, the guide, and the question date.
2. A step calls `draft_pack`. There is no connector to a mailbox, a calendar, or an applicant tracking system.
3. If the outcome is `human_route`, `prohibited_request`, `above_clearance`, `unreadable`, or `no_criteria`, the flow stops and shows the JSON.
4. The recruiter's decision is a separate item. The flow passes `item`, the hashes, and the directory reference. It does not read an approval field from the job text.
5. An HR seen-step uses the HR partner's directory reference and the route hash.
6. The pack approval step runs only after the questions are accepted, the rubric is accepted, and every route is seen.
7. The flow shows `approved_for_use` and shows that `contacted` is false. It does not send the invitation.

A flow that added a send action would be outside this starter.
