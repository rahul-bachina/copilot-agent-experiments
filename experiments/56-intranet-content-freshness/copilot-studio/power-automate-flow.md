# Power Automate, as a sample design

The approvals page opened on 16 November 2026 describes "Start and wait for an approval". The type "Approve/Reject - First to respond" completes when any approver responds. Approvers are notified. Flows are saved in Dataverse. The approvals connector is a standard connector.

A deployment that followed this design would:

1. Send that approval only to the named content owner.
2. Wait for approve, reject, or defer on the named task ids.
3. Pass the response to `record_approval`, not to a page-edit action.
4. Refuse any branch that edits, publishes, unpublishes, deletes, reassigns, or messages other staff.

This starter does not create that flow. `power_automate_called` stays false. `approval_request_sent` stays false. The JSON field `power_automate_approval_not_sent` records the action name and `called: false`.

Planner is the same. `POST /planner/tasks` was read. It needs an existing plan id. The stub sets `planId` to null and `called` to false. A JSON stub is not a Planner task.
