# Flow

One flow returns the JSON. It does not write an entitlement and it does not send.

This is a description, not a solution file. It was not imported into a tenant. Click-paths were not opened on 10 November 2026.

1. Trigger: the topic passes the file path and the as-of date. Both are typed by the adviser.
2. Run `python src/explainer.py --input <file> --as-of <date>`.
3. Return the stdout JSON to the topic.
4. Stop.

There is no Dataverse action, no mail action, and no approval action inside the flow. The entitlement owner's decision, if they record one, is a second run of `record_decision` in the same Python file. That run still does not write a record.

If the process exit code is 2, the topic says the file could not be read. It does not guess the entitlement.
