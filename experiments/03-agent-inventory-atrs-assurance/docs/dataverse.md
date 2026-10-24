# Dataverse table design

This is a design and a set of synthetic CSV fixtures. It is not a Dataverse solution, and it does not create tables. A publisher prefix in a real environment would replace `g010`.

The agent identity, if one is ever registered, gets read access to these tables. It does not get write access to `g010_lifecyclestatus` or to any approved column. The governance owner’s role is the one that can change a status, and only after they have decided. This starter does not ship that security role.

## g010_agentinventory

One row per agent. Choice values match the core.

| Column | Type | Notes |
| --- | --- | --- |
| g010_inventoryid | Text, alternate key | Lower case. Matches `agent.id` if a manifest is drafted. |
| g010_catalogueid | Text | For example UK00, C006, G010, or SYN. |
| g010_name | Text | |
| g010_version | Text | Semantic version. |
| g010_sector | Choice | `public`, `fca_firm`, `other`. |
| g010_organisationname | Text | Synthetic in this repository. |
| g010_team | Text | |
| g010_srorole | Text | Role title, not a person's name. ATRS field 2.1.3. |
| g010_governanceownerrole | Text | The role that approves status changes. In the fixtures this is "Governance owner". |
| g010_contactemail | Email | Team mailbox. Placeholders use example.com or example.gov.uk. |
| g010_websiteurl | Text | Or the template's N/A. |
| g010_atrsphase | Choice | Pre-deployment, Private Beta, Public Beta, Production, Retired. From the v4.0 Validation sheet. |
| g010_region | Choice | The v4.0 region list, including UK. |
| g010_lifecyclestatus | Choice | proposed, in_design, pilot, assurance_drafted, awaiting_governance_owner, approved_for_limited_use, suspended, retired. |
| g010_autonomylevel | Choice | A0, A1, A2. A row that says A3 can be stored so the generator can refuse it. The manifest schema will not accept A3. |
| g010_sourcereviewedon | Date | G007 compares this with the as-of date. |
| g010_experimentpath | Text | Repository path, when the row describes a starter in this repo. |
| g010_processingregime | Choice | uk_gdpr, law_enforcement, intelligence_services, unknown. |
| g010_processespersonaldata | Choice | yes, no, unknown. |
| g010_specialcategory | Choice | yes, no, unknown. |
| g010_profiling | Choice | yes, no, unknown. |
| g010_meaningfulhumaninvolvement | Choice | yes, no, unknown. |
| g010_significanteffect | Choice | legal, similarly_significant, none, unknown. |
| g010_lawfulbasis | Text | Recorded basis, or "Not recorded". The core does not choose one. |
| g010_explicitconsent | Choice | yes, no, unknown. Not treated as meeting Article 22B(2) on its own. |
| g010_article92g | Choice | yes, no, unknown. |
| g010_contractorlaw | Choice | yes, no, unknown. |
| g010_safeguardinformation | Choice | yes, no, unknown. Article 22C(2)(a). |
| g010_safeguardrepresentations | Choice | yes, no, unknown. Article 22C(2)(b). |
| g010_safeguardhumanintervention | Choice | yes, no, unknown. Article 22C(2)(c). |
| g010_safeguardcontest | Choice | yes, no, unknown. Article 22C(2)(d). |
| g010_thirdpartyinvolvement | Choice | Yes, No. ATRS field 2.1.4. |
| g010_thirdpartyname | Text | |
| g010_companieshousenumber | Text | N/A when there is no real number. Do not invent one. |

There is no `g010_approved` column for the agent to set. A pack is a file or a note, and its approved flag is false.

## g010_agentnarrative

Long answers, one row per field, so a maker does not have to put every ATRS paragraph on the header.

| Column | Type |
| --- | --- |
| g010_inventoryid | Lookup to g010_agentinventory |
| g010_field | Text. Inventory key, for example `public_description` or `human_review`. |
| g010_value | Multiline text |

The loader copies these onto the inventory record before drafting. An empty value is a gap, not a guess.

## g010_dataaccess

| Column | Type |
| --- | --- |
| g010_inventoryid | Lookup |
| g010_direction | Choice: read, never |
| g010_resource | Text |
| g010_justification | Multiline text. For `never`, this is the reason. |
| g010_personaldata | Yes/No, reads only |

## g010_tool

| Column | Type |
| --- | --- |
| g010_inventoryid | Lookup |
| g010_tool | Text |
| g010_action | Text |
| g010_accesslevel | Text |

## g010_risk

| Column | Type |
| --- | --- |
| g010_inventoryid | Lookup |
| g010_riskid | Text |
| g010_risk | Multiline text |
| g010_likelihood | Choice: Low, Medium, High |
| g010_impact | Choice: Low, Medium, High |
| g010_residualrisk | Choice: Low, Medium, High |

A High residual risk makes the DPIA skeleton mention the ICO's prior-consultation point. It does not decide that consultation is required.

## g010_lifecycleevent

Append-only. The agent does not insert rows.

| Column | Type |
| --- | --- |
| g010_inventoryid | Lookup |
| g010_fromstatus | Choice |
| g010_tostatus | Choice |
| g010_requestedby | Text |
| g010_reason | Multiline text |
| g010_applied | Yes/No. Default No. |
| g010_approvedbythisagent | Yes/No. Default No. A business rule should keep this No. The core never sets it to Yes. |
| g010_externalapprovalid | Text. Blank until a person records an id from their own approval process. |
| g010_approverrole | Text |
| g010_externaldecision | Choice: approve, reject, or blank |

The fixture events for Experiments 01, 02, 04, and 05 are proposals. `applied` is false. No external approval id is stored.

## g010_assurancepack

Optional later table. Not populated by this starter.

| Column | Type |
| --- | --- |
| g010_inventoryid | Lookup |
| g010_asof | Date |
| g010_documentstatus | Text. The only value the agent may write, if a write is ever allowed, is `draft`. |
| g010_packjson | Multiline text or a file column. |
| g010_stale | Yes/No |

Do not add a column the agent can set to approved.

## Fixtures

| File | Contents |
| --- | --- |
| `fixtures/dataverse/agent_inventory.csv` | Header rows, including Experiments 01 and 02. |
| `fixtures/dataverse/agent_narrative.csv` | Long text. |
| `fixtures/dataverse/data_access.csv` | Reads and never-access. |
| `fixtures/dataverse/tools.csv` | Tools named on the worked examples. |
| `fixtures/dataverse/risks.csv` | Risk rows. |
| `fixtures/dataverse/lifecycle_events.csv` | Unapplied proposals. |

`fixtures/inventory/*.json` is the same data as one object per agent. `src/dataverse_csv.py` loads the CSV directory. Tests check the two shapes match.

Regenerate both from `fixtures/records.py`:

```bash
python fixtures/records.py
```

## Security role, when a tenant exists

| Role | Read inventory | Change lifecycle status | Insert an assurance pack | Send email |
| --- | --- | --- | --- | --- |
| Agent identity | Yes, rows it is asked to draft | No | No | No |
| Drafter | Yes | No | No | No |
| Governance owner | Yes | Yes, after their own decision | Yes, as a draft note if the organisation wants a copy | No, not by the agent |

Power Platform DLP should block mail connectors on this environment. That control is described in [security-and-permissions.md](security-and-permissions.md). It is not configured here.
