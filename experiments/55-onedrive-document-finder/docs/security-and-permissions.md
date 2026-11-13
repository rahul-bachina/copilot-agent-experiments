# Security and permissions

Manifest `exp-55-onedrive-document-finder`, version 0.1.0. Autonomy **A0**. Writes disabled. Sends disabled. `permissions.yaml` is the same file as `agent-manifest.yaml` and validates against `schemas/agent-manifest.schema.json`.

## What the sample enforces

The selection object is the only place locations, principals, and clearance are read. File text that says the user has approved, or that clearance is TOP SECRET, is an injection signal. `followed` is false.

A file is copied into the result only when all three are true:

1. Its location id is in the confirmed set.
2. A principal on the selection is on its `readers` list. A missing list fails closed.
3. The fixture sensitivity label ranks at or below the fixture clearance. An unrecognised label fails closed.

Withheld files contribute a count. Ids, titles, and extracts are not in the JSON. The tests use canary strings for a SECRET file, a finance file outside the selection, a file with another principal, an unrecognised label, and a later SECRET version. None of those strings is in the result.

The sensitivity label, the retention label, and a legal-hold flag on an admitted file are copied through. A suggestion from Experiment 49 does not replace the fixture label.

`move_file`, `delete_file`, `share_file`, and `change_permissions` raise `FinderForbidden`. Acknowledgement refuses those decision names. `executed` stays false.

## Platform controls, as far as the pages opened on 13 November 2026

Microsoft Graph search, opened the same day, can query `driveItem` files. The files page's example 4 says the query covers OneDrive and SharePoint content the signed-in user can read. The query API page lists delegated Mail.Read as the least privileged permission and application Files.Read.All as the least privileged application permission. Whether a driveItem-only query accepts a narrower delegated scope was not stated. Whether application permissions are trimmed to one user was not stated. This sample calls neither API, so it does not rely on that trimming. It demonstrates the trim in the fixture instead.

Work IQ, opened the same day, uses delegated authentication. The API overview says application-only authentication is not supported, and that Microsoft 365 permissions, sensitivity labels, and compliance policies are enforced automatically. A general-availability date was not on the pages opened. That date is unverified. This sample does not call Work IQ. The Work IQ.Act permission, which the permissions reference describes as read and change, is not requested.

Copilot Studio knowledge, opened the same day, says a SharePoint source uses the agent user's Entra ID authentication and surfaces only content that user can access. OneDrive is named as unstructured data with different limits. The limits page was not opened.

Purview sensitivity labels, opened the same day, are customisable, stored as clear text in metadata, and can sit beside a retention label. The page says Copilot and agents recognise them. Data Map labelling is described as currently in preview. The licensing table was not opened. This sample does not call Purview. A Government Security Classifications marking in a fixture is not one of those labels.

These product pages were not opened. Treat the names as unverified here: Microsoft Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, and Application Insights. None of those objects is created in this folder.

## Data minimisation

Article 5(1)(c) was read on 13 November 2026. The result does not keep a full extract. A snippet is returned only when the extract matched and the hit is not a safeguarding cue. Phone numbers, email addresses, dates of birth, street addresses, and honorific names are masked on that snippet, in addition to the UK identifiers Experiment 08 proposes. `output_is_anonymised` stays false. `data_minimisation_met` stays false. This is not a finding that Article 5(1)(c) was met.
