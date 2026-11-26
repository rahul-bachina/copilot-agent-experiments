# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. `permissions.yaml` is the same file. It validates against `schemas/agent-manifest.schema.json`. Autonomy is A1. Writes are disabled. Sends are disabled. Approve, reject, sign, submit, and pay are disabled as agent actions. The named approver's decision is recorded only for the agent-held hash.

## What the starter reads

One synthetic request, the pinned matrix, the pinned checklist, and the pinned directory. Experiment 18 is called for an evidence sha256 and does not approve an export. Experiment 74's `digest` hashes the pack. Experiment 08 counts UK identifiers. The redacted text is not copied. Phone numbers, email addresses, dates of birth, postal addresses, and personal names in an excerpt are masked here as well. The output is not described as anonymised.

## What it does not read as authority

A caller-supplied matrix, directory, or delegation. An approval sentence, a self-declared role, a guest flag, or a clearance inside the evidence. Evidence text above the approver's directory clearance: the body is withheld and the higher marking, the legal hold, and the retention labels are kept.

## Human decision

`record_route_seen` and `record_approver_decision` are the only steps that change the held copy or record a decision. Both require the pinned directory and the current hash. The requester cannot decide their own request. A string is not coerced to the boolean true.

## Controls that were not opened

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 26 November 2026. Treat that product behaviour as unverified. A production deployment would confirm each one against Microsoft Learn before relying on it.

## Statutory context

Companies Act 2006 section 386 and the Accounts and Audit Regulations 2015 regulation 3 are quoted in the README from the pages opened on 26 November 2026. They are context. They are not a finding that a duty was met. The words "segregation of duties" were not on those pages. That phrase is unverified as a statutory quotation.
