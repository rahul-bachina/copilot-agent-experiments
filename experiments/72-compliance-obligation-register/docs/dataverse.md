# Dataverse table design

This is a design for a synthetic environment. No Dataverse environment is deployed from this folder. The only write the Python core performs is an in-memory row that mirrors `cr72_obligation_staging`.

## Staging table: `cr72_obligation_staging`

| Column | Notes |
|---|---|
| `cr72_changeid` | Key. Example `CHG-OBL-1001`. |
| `cr72_action` | `new`, `changed`, or `retired`. |
| `cr72_obligationid` | The register id. |
| `cr72_sourceid` | The pinned extract id, when there is one. |
| `cr72_provision` | The clause or rule reference from the pin. |
| `cr72_obligationtext` | The verbatim quote, or `not copied` when the marking is above the directory clearance. |
| `cr72_applicability` | A candidate. Not a scope decision. |
| `cr72_proposedowner` | A lookup to the directory person. Not an assignment by the agent. |
| `cr72_reviewdate` | The review date, `unparseable`, or `not stated`. |
| `cr72_changehash` | Hash of the action, the id, the before record, the after record, and the dates. |
| `cr72_proposalhash` | Hash of the proposal the owner approved. |
| `cr72_approverref` | The directory compliance owner who approved this hash. |
| `cr72_legalhold` | Copied. The agent cannot clear it. |
| `cr72_retention` | Copied. The agent cannot drop it. |
| `cr72_marking` | The higher of the metadata and the page. |
| `cr72_productionwrite` | Default false. The agent cannot set it true. |
| `cr72_sent` | Default false. |
| `cr72_finaladvice` | Default false. |
| `cr72_accountabilityassignedbyagent` | Default false. |

## Read-only mirrors

| Table | Use |
|---|---|
| `cr72_obligation_register` | The production register. This starter never writes it. |
| `cr72_control` | The pinned control library. |
| `cr72_directory_person` | Role, guest flag, and clearance. A sentence in the note is not a row. |
| `cr72_source_extract` | The pinned extracts, including effective dates and status. |

A second write of the same change hash is already staged. A different hash for the same change id is a conflict and is not overwritten.
