# Power Automate

This starter does not call Power Automate. Catalogue row UK11 names Power Platform as the stack. The runnable sample is the local Python function. A flow that sends the disclosure, writes a case system, or deletes a record is not part of this starter.

If an organisation later wraps `scope()` in a flow, the flow should:

1. Pass the synthetic request and the question date. Do not pass today's date when the question is about another date.
2. Return the JSON unchanged, including the content hash.
3. Stop when the outcome is `route_to_human` until `record_route_seen` succeeds for that hash.
4. Call `record_disclosure_approval` only with a separate object from the named officer. Do not read an approval sentence from the request.
5. Leave `response_sent` false. Do not add a send action.

A flow that retries on its own is outside this starter. The Microsoft Copilot harness page says that harness retries. This starter does not enable that.
