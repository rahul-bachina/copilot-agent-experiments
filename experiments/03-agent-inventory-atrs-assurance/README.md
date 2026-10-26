# Experiment 03: Agent inventory, lifecycle, and ATRS assurance pack

Catalogue ID **G010**. Stack: Power Platform and Dataverse. Autonomy **A1**.

A governance owner keeps a list of agents. This starter drafts the pack they would read before a lifecycle status changes: an [Algorithmic Transparency Recording Standard](https://www.gov.uk/government/publications/algorithmic-transparency-template) record, a mapping to the ten principles in the [AI Playbook for the UK Government](https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government/artificial-intelligence-playbook-for-the-uk-government-html), an [ICO DPIA](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/how-do-we-do-a-dpia/) skeleton, a screen against [Data (Use and Access) Act 2025 section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80) (UK GDPR Articles 22A to 22D), and an FCA-style inventory row drawn from the FCA's [AI good-practice examples](https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services) published on 19 October 2026. It also drafts an `agent-manifest.yaml` and checks it against `schemas/agent-manifest.schema.json`.

The governance owner approves every lifecycle status change. The core never marks a pack, a manifest, or a status approved.

Catalogue items **G006** (prompt-injection findings) and **G007** (groundedness and a staleness check) are the evaluations inside the pack. A security reviewer assesses G006 findings. An evaluation owner approves G007 thresholds. Neither approval is recorded here.

Experiments 01, 02, 04, and 05 are the worked inventory examples. They are synthetic descriptions of those starters, not live deployments. Harbour & Wold Borough Council, Northbridge Mutual, and Harbourline Markets Ltd are fictional. Experiment 05 does not name a landlord.

This revision does not call a model and does not connect to a tenant. MIT licence: see the repository [LICENSE](../../LICENSE).

## The problem

An organisation can have many agents and no single place that says what each one reads, who owns it, and whether a transparency or data-protection record has even been drafted. Public bodies in scope of the ATRS are expected to publish records for in-scope tools. Firms are being pointed at inventories of AI use cases, models, owners, and controls. A language model that fills those forms from memory will invent fields, statutory tests, and approvals.

The draft has to be traceable to an inventory row, and a status has to stay put until the governance owner has decided.

## Who it helps

**Governance owners.** They get one draft pack per agent, with gaps left blank, and a lifecycle proposal they can refuse.

**Data protection officers.** They get a DPIA skeleton with the ICO's seven steps and a DUAA screen that cites section 80. They do not get a signed DPIA or a lawful-basis decision.

**Security reviewers and evaluation owners.** G006 lists injection findings. G007 lists unsupported claims and a stale review date. The 180-day threshold is explicitly not approved.

**Architects.** The same Python core, the same manifest schema, and the same tests sit behind a Copilot Studio standard-harness guide and a Copilot Studio GitHub Copilot harness guide. See [docs/harness-comparison.md](docs/harness-comparison.md).

## Non-goals

- Approving, rejecting, or publishing an agent, a manifest, a DPIA, or an ATRS record.
- Deciding that a tool is inside the ATRS mandatory scope. The [scope and exemptions policy](https://www.gov.uk/government/publications/algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy) is for the organisation's single point of contact.
- Emailing `algorithmic-transparency@dsit.gov.uk` or anyone else.
- Writing Dataverse, a case system, or any other production record.
- Choosing a lawful basis, an Article 9 condition, or the outcome of Articles 22A to 22D.
- Deciding that a firm has met an FCA expectation. The FCA has not published a prescribed inventory form.
- Reproducing ATRS prompts, the AI Playbook, or the Act. Field names and short verified pointers only.
- Calling a model, scoring a model, or clearing G006 or G007.
- Autonomy A3. A row that asks for it does not get a manifest.

## What the core does

`src/pack.py` builds a pack from one inventory JSON file and an as-of date. The same inputs always produce the same JSON. Nothing is fetched.

| Draft | What is copied | What stays empty |
| --- | --- | --- |
| ATRS v4.0 | 56 field identifiers read from the [template workbook](https://assets.publishing.service.gov.uk/media/681b8f20e26cd2f713d8705d/ATRS_V4.0__FINAL.xlsx) on 24 October 2026. An answer is copied only from the matching inventory key. | Anything missing is the gap sentence. A phase or region that is not on the template's Validation sheet is not presented as a completed field. |
| AI Playbook | The ten principles in the list on the HTML playbook, published 10 February 2025. Where the section heading differs (principles 4, 5, and 9), both wordings are stored. | `met` is null. This is not a compliance score. |
| DPIA | The seven steps on the ICO's "How do we do a DPIA?" page. | Every sign-off name is null. |
| DUAA screen | Recorded facts tested against the structure of Articles 22A to 22D, as substituted by section 80. | `lawful` is null. Article 22D regulations are not read. |
| FCA-style row | Use case, model, owner, access, controls, and whether the row looks experimental or in production, following the good-practice examples. | Senior Manager Function mapping is a gap. `agent_recorded_as_live` is not an approval. |
| Manifest | A schema-valid draft, or no draft if the row asks for A3. | `draft_control.approved` is false. `--approve` exits without writing. |

Lifecycle statuses are `proposed`, `in_design`, `pilot`, `assurance_drafted`, `awaiting_governance_owner`, `approved_for_limited_use`, `suspended`, and `retired`. `propose_status_change` does not modify the record. `apply_status_change` modifies a copy only when the caller supplies an external decision whose role is `Governance owner`, whose source is `external`, and whose id does not start with `g010-generated-`. The event still says this tool did not approve the change. The assurance pack stays a draft afterwards.

The Dataverse table design and the synthetic CSV fixtures are in [docs/dataverse.md](docs/dataverse.md). There is no solution to import.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/03-agent-inventory-atrs-assurance
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
```

`eval/evaluate.py` prints a **smoke test** of 28 synthetic cases. `eval/smoke_report.json` is that run: 28 of 28 passed. It is not a model score.

Draft a pack and a manifest:

```bash
python src/pack.py \
  --inventory fixtures/inventory/exp-01-foi-triage.json \
  --as-of 2026-10-24

python src/generate_manifest.py \
  --inventory fixtures/inventory/exp-02-consumer-duty-complaint-intake.json \
  --as-of 2026-10-24 \
  --output /tmp/exp-02-draft-manifest.yaml
```

`--approve` is refused and writes nothing.

## Sample

Experiment 01, as-of 24 October 2026:

- ATRS 1.1 Name is "FOI Complaint Triage Agent", copied from the inventory.
- Applicability is `public_sector_spoc_must_decide`. The tool does not decide mandatory scope and does not allow an email to DSIT.
- The DUAA screen result is `significant_decision_not_recorded`. The wider FOI decision is flagged as not screened.
- The pack is not stale. `approved` is false.

Experiment 02 is the same shape for a fictional firm, Northbridge Mutual. Applicability is `not_a_public_sector_body`. A firm does not complete an ATRS record by holding the draft.

Experiment 04 is the same shape for Harbourline Markets Ltd, also fictional, at autonomy A0. The generated manifest stays A0. Applicability is `not_a_public_sector_body`. The pack does not say the firm is ready for authorisation.

Experiment 05 is a public-sector row for the Awaab's Law starter. No landlord is named. Applicability is `public_sector_spoc_must_decide`. The pack does not copy that experiment's dates and does not decide that a defence is made out.

The fictional Harbour & Wold benefits scorer records no meaningful human involvement, a legal effect, special-category data, and Article 6(1)(ea). The screen result is `restriction_may_apply`, pointing at Article 22B(1) and Article 22B(4). That is not a finding that an offence has been committed and not a decision about the processing.

## Limitations

- ATRS field names and the phase and region lists were read from template v4.0 on 24 October 2026. The workbook's "All data" sheet still mentions an older field layout and was not used. The model-name cell is labelled `2.4.2.1.` with a trailing stop; the reference here is `2.4.2.1`. One model block is drafted. The template says to duplicate the sheet for further models.
- The principles list and three section headings on the playbook page do not use the same words. Both are stored. The page was read on 24 October 2026.
- Section 80 was in force at Royal Assent for specified purposes (section 142(1)(2)(h)) and on 5 February 2026 in so far as not already in force (S.I. 2026/82, regulation 2(j), with regulation 5). Regulation 5 has not been interpreted. Article 22D regulations have not been read.
- The screen does not decide that Article 22B(2) or 22B(3) is met. Explicit consent is not treated as enough, because the article also requires the decision to be based entirely on that processing.
- Law-enforcement processing (Data Protection Act 2018 sections 50A to 50D) and intelligence-services processing (sections 96 and 97) are pointed at and not run. The law-enforcement test uses "adverse". Article 22A does not.
- The FCA publication of 19 October 2026, updated 20 October 2026, describes good practice. It is not a form. No Senior Manager Function is assigned.
- The 180-day staleness threshold is a draft. G007 says the evaluation owner approves thresholds. That approval is not in this repository.
- G006 is a pattern list, not a red-team exercise and not a model evaluation.
- This is not legal advice, a DPIA, an ATRS submission, or a statement of compliance.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Dataverse tables and CSV fixtures: [docs/dataverse.md](docs/dataverse.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- GitHub Copilot harness skills: [skills/](skills/).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md). This experiment does not call it.
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/03-agent-inventory-atrs-assurance/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── tests/
├── eval/
├── fixtures/
│   ├── inventory/
│   └── dataverse/
├── copilot-studio/
├── skills/
└── docs/
```
