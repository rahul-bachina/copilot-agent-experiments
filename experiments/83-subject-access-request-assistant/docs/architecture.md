# Architecture

The runnable path is `src/sar.py`. It does not call a model. Either Copilot Studio harness is a guide to that same function. Microsoft Foundry, if used, only turns the JSON into a short note. It does not choose a redaction, an exemption, or a deadline.

```text
synthetic request and records export
        |
        v
scope()  ---- calls Experiment 08 propose() and Experiment 12 intake()
        |
        v
draft JSON + agent-held copy and hash
        |
        +-- route_to_human --> record_route_seen()  (named officer, same hash)
        |
        v
record_disclosure_approval()  (named officer, same hash, every redaction and exemption)
        |
        v
disclosure_approval_recorded true
response_sent, records_deleted, records_edited, exemption_decided_by_agent stay false
```

Experiment 01 is not imported. FOI Act section 40(1) is a route in `src/foi.py`. `foi_disclosure` and `foi_answered` stay false.

The hash covers the case, the requester reference, the deadline illustration, the search scope, the FOI route, the document ids, the masked copies, the redactions, the exemptions, the identity and authority flags, the sensitive categories, the marking, the legal hold, the retention labels, the injection signals, the suppression block, the required acknowledgements, the conflicts, the records-export flags, and the forced-false action flags. A later edit of any of those is a different hash. The held copy is not replaced unless the approval step succeeds with no blocked reason.

`send_response`, `delete_record`, `edit_record`, and `decide_exemption` raise `SarForbidden`.
