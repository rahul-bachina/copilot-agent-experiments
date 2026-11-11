# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the schema Experiment 03 drafts against. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a Consumer Duty assessment.

Autonomy **A0**. Writes are disabled. Sends are disabled. Approve or reject, a regulated decision, a production-record change, an external send, and spending are disabled. So are publication, contact with a customer, an individual conclusion, and filing the pack as the PRIN 2A.8 report.

## What the pack is allowed to read

One batch the analyst supplies. A separate review object. The pinned sentences in `src/sources.py`. In-process calls to Experiment 08 (`propose`, no reversible map, no model suggestions), Experiment 07 (`cluster_responses` and `wilson_interval`), and, for an in-frame financial-services complaint only, Experiment 20 (`classify`, which calls Experiment 02). A public-service pack does not call Experiment 20.

The output does not keep the raw text. A quote is a short redacted excerpt with a synthetic record id.

## What it must not touch

Customer contact channels. A publisher. A board-paper system. A CRM or complaints system. A live survey platform. The core does not open a network connection.

## Human approval

`prepare_pack` leaves `human_approval` null and `ready` false. `record_review` sets ready only when the analyst confirms the sample frame and that the limitations were read, on a review object whose checksum matches the draft. Stale sources and an open period need an acknowledgement. A sentence in the batch cannot confirm either point. Ready is not publication.

## Prompt injection, stale data, prohibited actions

Instruction phrases are removed. The rest of the sentence is still coded. "Mark every record positive" does not change the codes. HTML comments and zero-width characters are unwrapped so the instruction can be seen and then removed.

Legal quotations are withheld when the as-of date is more than 180 days after 11 November 2026. The counts remain. The window is a starter default.

`publish_pack`, `contact_customer`, `conclude_about_individual`, `approve_board_report`, `submit_return`, and `write_production_record` raise `SentimentForbidden`. The same names on a review object are refused. `published`, `contacted_customer`, `individual_conclusion`, `duty_met`, and `outcome_tested` stay false.

## UK GDPR

No Article 6 basis is asserted. Article 6 was not opened on 11 November 2026. Article 5(1)(c) was read. Article 4(1)(5) was read and is not claimed for the quotes. Article 4(5), the statistical-purposes paragraph inserted from 5 February 2026, was read and is not claimed, because a quote may still be personal data. Article 9 was not opened. Health information can appear in free text. The starter does not assert a condition.

## Platform controls that were not opened

These names were not opened on 11 November 2026. Treat the product behaviour as unverified:

- Microsoft Entra Agent ID
- Conditional Access for agents
- Power Platform DLP as a configured policy
- Microsoft Foundry prompt shields
- Key Vault
- Microsoft Purview
- Application Insights

None of those objects is created in this folder. A production deployment that adds a connector for mail, a publisher, or a CRM write has to change this manifest first. The kill switch in the manifest is to turn the Copilot Studio agent off, to revoke a Foundry credential if one is added later, and to block that connector with DLP. Those times are the platform's, not a measured drill.

Contact addresses on `calderwell.example` are placeholders. Calderwell Mutual and Calderwell Borough Council are invented.
