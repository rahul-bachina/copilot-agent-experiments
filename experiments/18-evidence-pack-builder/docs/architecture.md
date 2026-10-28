# Architecture

Experiment 18, catalogue ID L004. Autonomy A1. The runnable core is `src/pack.py`. It does not approve an export and it does not send.

```
Person (scopes, search period, as-of date, pasted items)
        |
        v
Either Copilot Studio harness
  standard topic, or GitHub Copilot harness skills
        |
        v
build_pack()                         record_export_approval()
  scope check                        role: Evidence pack approver
  injection scan                     exact item ids
  Experiment 12 intake()             redaction decisions
       |
       v
  Experiment 08 propose()            produce_export()
  identifiers only                   index, no bodies
        |
        v
Draft JSON                           then stop
  export_approved = false
        |
        X  send_external, disclose_to_requester,
           write_production_record, apply_exemption,
           release_redacted
           all raise PackForbidden
```

The diagram in [architecture_diagram.png](architecture_diagram.png) is the same shape, drawn for the briefing site. Regenerate it with `docs/generate_diagram.py` if the boxes change. Matplotlib is used only by that script. It is not a runtime dependency.

## What is deterministic

Hashes, scope membership, the search-period comparison, duplicate detection, closed-list privilege and third-party phrases, page order, and the empty approval are Python. A language model must not set them. Experiment 12 supplies the hash, the keyword class, the intake date status, and the Experiment 08 entity types for in-scope items. This experiment does not copy those detectors.

Out-of-scope text is not passed to Experiment 12. It is scanned for instructions so a hidden phrase is recorded, and it is not hashed into the candidate manifest.

## Human approval

1. The evidence pack approver sets the authorised scopes and the search period. Item text cannot.
2. The same role approves the exact list of item ids and a redaction decision for every flagged item that is included.
3. Stale sources, or an intake date older than 90 days, have to be acknowledged. The flag stays on the draft.
4. Release and send stay outside the agent after the index exists.

`record_export_approval` and `produce_export` exist so a test can show the gate. The skills say the agent must not call them. `schema/tools.json` marks both `callable_by_agent: false`.

## What is not in the box

No Microsoft 365 search, no Dataverse write, no SharePoint write, no mail connector, and no call to an ombudsman or regulator portal. Pack types for the Financial Ombudsman Service and the Housing Ombudsman are labels. Their evidence rules were not opened on 28 October 2026.

UK GDPR Article 15 and Data Protection Act 2018 Schedule 2 paragraphs 16 and 19 are cited from pages opened on 28 October 2026. They are not applied. Article 15(1A) is not implemented as a test of whether the search was reasonable and proportionate.
