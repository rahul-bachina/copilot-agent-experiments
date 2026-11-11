# Security and permissions

Manifest `exp-47-work-order-completion`, version 0.1.0. Autonomy **A1**. The only write is an in-memory stub after each field has been approved. Sends are disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. So are close, charge, parts order, customer contact, and clearing a hazard.

`permissions.yaml` is the same file as `agent-manifest.yaml`. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03.

If this note and the manifest disagree, the manifest is the control. This note is not a completed DPIA and it is not an ATRS submission.

## What the starter reads

One completion pack the technician supplies. An optional pre-visit pack, passed to Experiment 46, or a supplied Experiment 46 brief, read for structured ids only. Experiment 15 categories. Experiment 05 for a housing illustration, with officer approval forced off. The static citations in `src/sources.py`.

The notes, the photo text, and any door code are not copied out. Experiment 15's phrases are not copied out. Experiment 05's quoted reasons are not copied out.

## What it does not touch

A production work order, a charge, a parts order, a mailbox, or a customer message. The stub sets `production_system_written` false. `job_closed`, `charges_raised`, `parts_ordered`, and `customer_contacted` stay false.

## UK GDPR

No Article 6 basis is asserted. Article 6 was read on 11 November 2026. Points (ea) and (f) do not apply to processing by public authorities in the performance of their tasks. Article 5(1)(c) and Article 5(1)(d) were read the same day. The record keeps ids and catalogue values. Clashes stay listed. The agent does not erase or rectify a field on its own. Article 9 was not opened. A note may reveal health. The controller confirms a condition and completes a DPIA before live use.

Article 22A was not opened. This starter does not take a solely automated decision about the job. The technician approves each field, and the agent still does not close it.

## Controls named, not configured

These product pages were not opened on 11 November 2026. Treat the behaviour as unverified.

| Control | In this starter |
|---|---|
| Microsoft Entra Agent ID | Not registered. |
| Conditional Access | Not configured. |
| Power Platform DLP | No connector. A later policy should block work-order writes, charges, parts orders, and messaging. |
| Microsoft Foundry prompt shields | Not enabled. The core does not call a model. The product page was not opened. |
| Key Vault | No secret is stored. |
| Microsoft Purview | No label is applied. |
| Application Insights | No trace is written. Do not log the notes or a door code. |

## Logging

This starter writes no log. Before live use, log who ran it, the work-order id if it matched the synthetic pattern, the outcome, the field ids approved, and the field ids stub-written. Do not log the notes.

## Kill switch

Turn the Copilot Studio agent off. Revoke any later Foundry credential. Block a later connector in a data loss prevention policy the organisation configures. Contacts in the manifest use `calderwell.example.gov.uk`. They are placeholders. Calderwell Borough Council is invented.
