# Architecture

Experiment 77. Catalogue ID O002. Autonomy A1.

The runnable path is `src/extract.py`. Copilot Studio topics and the skills under `skills/` are guides to that same function. Neither harness decides a form, writes a production record, performs a call-back, or sends.

```text
pinned schema + pasted form + question date
        |
        v
extract_form()
  Experiment 12 intake()  -- does not confirm the file or a purpose
  Experiment 08 propose() -- counts identifiers, does not copy the redacted text
        |
        v
draft + review sheet + agent-held copy + content hash
        |
        +-- distress / safeguarding / whistleblowing --> record_route_seen()
        |
        v
record_reviewer_approval()
  named directory reviewer, exact agent-held hash
        |
        v
synthetic staging row
        x
decide / production write / call-back / send   (these raise)
```

The hash covers the fields, flags, marking, legal hold, retention labels, injection signals, suppression list, required acknowledgements, schema check, and whether the route was seen. A caller who changes any of those and hashes the package again does not match the copy the agent stored.

A SECRET cover is read from the page as well as from metadata. The higher marking is kept. A self-declared clearance in the form is ignored. If the directory clearance is below the marking, field values are withheld and the record cannot be staged.

Material fields on the review sheet are identity, bank details, amounts, dates, declarations, and the signature. The signature value is `present` or `absent`. It is never `verified`.
