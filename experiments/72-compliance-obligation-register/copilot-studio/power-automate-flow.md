# Power Automate flow

This is a description of a flow. It is not an importable solution and it is not connected to a tenant.

1. The trigger is a manual run by the compliance owner, with the synthetic request and the question date.
2. A desktop or cloud flow step runs `python3 src/register.py` with that request and date. The step has no connector that can send mail or write a production table.
3. If `outcome` is `route_to_human`, the flow shows the route hash and stops. A later manual step may call `record_route_seen` with a seen object the owner supplies. The flow does not copy the cue into an email.
4. Otherwise the flow shows the diff. It does not stage.
5. A second manual step accepts an approval object the owner types: `decision` is `approve`, the change id, both hashes, and the boolean acknowledgements. The step calls `stage_approved_change`.
6. The step writes only the in-memory staging row the function returns. `production_written` remains false. There is no send action on the flow.

A word in the request JSON is not an input to step 5. The approval object is a separate parameter.
