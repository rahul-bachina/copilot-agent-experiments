# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for a records manager, a DPO, and a security lead deciding whether to try the starter. It is not a completed DPIA and it is not an ATRS submission.

`permissions.yaml` is the same file as `agent-manifest.yaml`.

## Autonomy

**A1.** The records manager confirms or changes every field. The label stub is a second, explicit step and still does not change a record. There is no A3 path. Writes are disabled. Sends are disabled.

## What is read

**Read, in this starter.** The document the records manager pastes. The as-of date. The fictional scheme. The pinned sources. Experiments 12, 08, and 19, in process, for this document only.

The Python starter does not persist the document. A document that is not marked synthetic is refused, and the refusal does not echo the body. Identifier values are not copied. `output_is_anonymised` stays false.

## What is not done

The agent does not delete, dispose of, move, or downgrade a record. It does not call Microsoft Purview. It does not decide that section 3 of the Public Records Act 1958 was met, that the section 46 code was followed, or that Article 5(1)(e) was met.

## Controls that were opened

Microsoft Purview records management and sensitivity labels were opened on 11 November 2026.

- The records-management get-started page describes a file plan, retention labels, and disposition reviews so that somebody reviews and approves before content is deleted. It recommends the Records Management admin role group. The licensing table on the service description was not opened.
- The sensitivity-labels page says a label can classify and protect, including encryption and content markings, and that a document or email can have both a sensitivity label and a retention label. Extending labels to Microsoft Purview Data Map is described there as currently in preview.
- The file-plan manager article and the disposition click-path were not opened. Column names and the reviewer's email workflow are unverified here.

This starter does not create those objects.

## Controls that were not opened

These pages were not opened on 11 November 2026. Treat the product behaviour as unverified. None of these objects is created in this folder.

| Control | In this starter |
|---|---|
| Microsoft Entra Agent ID | Not registered |
| Conditional Access for agents | Not configured |
| Power Platform DLP as a configured policy | Not configured. The flow note says what a later connector must not do |
| Microsoft Foundry prompt shields | Not enabled. The core does not call a model |
| Key Vault | Not used |
| Application Insights | Not connected |
| Purview audit of a Copilot Studio transcript | Not connected. Whether a transcript is audited was not verified |

## Logging

This starter writes no log. Before live use, log who ran it, when, the document id if it matched the synthetic pattern, the outcome, and the later review. Do not log the body or an identifier value.

## Kill switch

Turn the Copilot Studio agent off, remove any Foundry credential, and block a connector that can label or delete. Contacts in the manifest use `merrowfield.example.gov.uk`. They are placeholders. Merrowfield Borough Council is invented.

## UK GDPR

Article 5(1)(e) was read on 11 November 2026. The longer-storage limb cites Article 84B. That article was not opened. Article 6 and Article 9 were not opened. No basis and no Article 9 condition are asserted. Experiment 19's screen does not decide that a DPIA is required.
