# Flow sketch

This is a sketch, not a published flow.

1. Trigger: the topic passes a synthetic pack, an as-of date, and a stale-after-days window.
2. Action: run `python src/draft.py` with `--pack` and `--as-of` only. Do not pass `--approve`, `--decline`, `--set-limit`, `--contact-customer`, `--contact-bureau`, `--post-core`, `--post-crm`, or `--file-sar`.
3. Return the JSON to the topic.
4. Do not write Dataverse, SharePoint, a core banking system, a CRM, or a Fabric item.
5. Do not send an email.

The flow has no side effect beyond returning the draft. The credit officer approves any later use outside this flow.
