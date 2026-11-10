# Security and permissions

Manifest `exp-46-field-visit-preparation`, version 0.1.0. Autonomy **A0**. Writes disabled. Sends disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. So are schedule, dispatch, close, authorise entry, and clear a hold.

`permissions.yaml` is the same file as `agent-manifest.yaml`. It validates against `schemas/agent-manifest.schema.json`.

The technician confirms the asset and the safety context on a separate review object. The work-order text cannot set that confirmation. A prohibited key such as `scheduled` or `officer_approved_category` is stripped and recorded.

## What a run may read

One pack the technician supplies. Pinned quotations in `src/sources.py`. Experiment 15 for indicator categories, which calls Experiment 08. Experiment 12 when text files are attached. Experiment 05 for a housing illustration, with officer approval forced off. The Python starter does not persist the narrative.

A call that is not marked synthetic is refused. The refusal does not echo the text.

## What a run must not do

Schedule, dispatch, close, update a work order, send a message, authorise entry, clear a hold, copy a door code, or label a person as vulnerable. Those flags stay false, including after confirmation.

## Least privilege

The prepare tool and the review tool are read-only in the manifest. The review tool is the only one that requires a human approval, and the approval it records is not an execution. Direct functions raise `VisitForbidden`.

## UK GDPR

No Article 6 basis is asserted. Points (ea) and (f) of Article 6(1), read on 10 November 2026, do not apply to processing carried out by public authorities in the performance of their tasks. Article 9 was not opened. A vulnerability category can be special-category data. No condition is asserted. A DPIA is for the controller. This file is not one.

Article 5(1)(c) was read the same day. The brief does not copy the narrative.

## Controls named, and not opened

These product pages were not opened on 10 November 2026. Treat the names as unverified here. None of these objects is created in this folder.

- Microsoft Entra Agent ID
- Conditional Access for agents
- Power Platform DLP as a configured policy
- Microsoft Foundry prompt shields
- Key Vault
- Microsoft Purview
- Application Insights

Experiment 01 records Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access as announced, with availability unverified. This folder did not re-check that announcement.

**Power Platform DLP.** If a connector to a scheduling system, a mailbox, or a work-order system is added later, a DLP policy is the place to block it. No such connector is in this folder. A policy was not configured here.

**Key Vault.** Not provisioned. If a later Foundry call cannot use a managed identity, the key belongs in Key Vault. No secret is stored in this folder.

**Prompt shields.** Not opened. The core does not call a model. The injection tests in this folder are the control on the stand-in. A filter is not a substitute for having no dispatch tool.

## Logging

This starter writes no log. Before live use, log the synthetic work-order id, the as-of date, the outcome, and whether an instruction or a stale pin was flagged. Do not log the narrative or a door code.

## Kill switch

Turn the Copilot Studio agent off, remove any Foundry credential, and block a later scheduling connector with DLP. Times are the platform's, not a measured drill. Contacts in the manifest use `calderwell.example.gov.uk`. Calderwell Borough Council is invented.

## Residual risk

Residual risk is not all Low. A paraphrase that uses none of the pinned phrases can miss a hold. A keyword can flag ordinary wording, including the word "loft". The technician is the control. There is still no tool that dispatches.
