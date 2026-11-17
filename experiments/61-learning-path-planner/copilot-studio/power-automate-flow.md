# Flow sketch

This is not a deployed flow. It describes the stops.

1. The employee message is the input. The flow calls the draft action and stores the JSON.
2. The flow does not read `approved` from that message.
3. A second action runs only when the employee submits the approval object for the stored `plan_id`.
4. A third action runs only when the manager submits the approval object for the same `plan_id`.
5. If the outcome is `adjustment_route`, a fourth action waits for the seen object. It does not set `adjustment_decided`.
6. If the outcome is `wellbeing_route`, the flow stops at step 1.
7. The last action writes nothing to a learning system. The JSON may show `enrolment_request_raised`. `enrolled` is false. `spent_gbp` is null.

A connector for enrolment, booking, or payment is out of scope. Add one only through a change to the manifest, and not in this starter.
