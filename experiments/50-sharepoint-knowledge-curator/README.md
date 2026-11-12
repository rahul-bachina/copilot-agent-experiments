# Experiment 50: SharePoint Knowledge Curator

Catalogue ID **M001**. Autonomy **A1**. The site owner approves every metadata change and every publishing action.

UK public bodies and regulated firms keep intranet knowledge in SharePoint. Pages drift: a content type is missing, a review date has passed, two pages say the same thing, a link points nowhere, or a page still carries a marking the knowledge curator should not touch. This starter reads one synthetic site snapshot and proposes those curation actions. Each proposal has the evidence that produced it and a confidence level. The site owner approves every proposal that would change metadata or publishing. The sample records a stub only after that approval.

The stub does not call SharePoint or Microsoft Graph. The agent does not delete, unpublish, move, or change permissions. A page the requesting user cannot already see is counted and not read.

The organisation in the samples is Merrowfield Borough Council. It is invented. Content type, owner, review date, and audience are starter fields. The Microsoft Graph `sitePage` property list opened on 12 November 2026 does not include audience, review date, or owner.

Stack in the catalogue: Microsoft 365, Copilot Studio, and Power Platform. The proposal itself is Python in the standard library. It calls [Experiment 12](../12-document-intake/) to inventory visible text, [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers, [Experiment 49](../49-records-classification/) for a records classification on text with negated tails removed, and [Experiment 44](../44-knowledge-gap-detector/) when the snapshot includes synthetic queries. A site owner can run it without a tenant.

## The problem

A model that unpublishes a page because the page says "delete this page", or that describes a library the requester cannot open, is the failure this starter is built to refuse. The site owner still has to see the proposal, the evidence, and the confidence.

## Non-goals

- Approving a metadata change or a publishing action. The site owner does that, per proposal.
- Deleting, unpublishing, moving, or changing permissions, including after approval.
- Calling SharePoint, Microsoft Graph, or a Copilot Studio knowledge-source API.
- Deciding that UK GDPR Article 5(1)(d) or Article 5(1)(e) was met. Article 84B was not opened.
- Deciding that the section 46 code was followed, or issuing a practice recommendation. Section 48 was not opened.
- Treating the 2021 code as the Lord Chancellor's code. The PDF that was opened is presented by the Secretary of State. The words Lord Chancellor do not appear in that extract.
- Applying the section 46 code to a body subject to the Freedom of Information (Scotland) Act 2002. The code says it does not apply there.
- Publishing, merging, or archiving a page that looks like personal data, or that carries a marking other than ordinary OFFICIAL.
- Showing content the requesting user cannot already see.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 12 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(d) is accuracy. Article 5(1)(e) is storage limitation. The longer-storage limb now refers to Article 84B, substituted on 5 February 2026. Article 84B was not opened. Article 6 and Article 9 were not opened. No lawful basis is asserted. |
| [Freedom of Information Act 2000, section 46](https://www.legislation.gov.uk/ukpga/2000/36/section/46) | Section 46(1) is the duty of the Secretary of State to issue a code on the keeping, management and destruction of records. The Secretary of State wording was substituted on 9 December 2015. Section 46(7) defines a relevant authority. The page said there are currently no known outstanding effects. Section 48 was not opened. |
| [Code of Practice, 15 July 2021](https://www.gov.uk/government/publications/code-of-practice-on-the-management-of-records-issued-under-section-46-the-freedom-of-information-act-2000) | The GOV.UK page links the PDF presented to Parliament by the Secretary of State for Digital, Culture, Media and Sport pursuant to section 46(6). Paragraphs 1.4.3, 2.3.1, 2.5, and 2.6.2 were read. The code does not apply to bodies subject to the Freedom of Information (Scotland) Act 2002. Paragraph 2.6.2 says disposition decisions must be recorded and taken by people who are properly authorised. This starter does not take one. |
| [Writing to GOV.UK standards](https://www.gov.uk/guidance/content-design) and [Retire outdated content](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content/retire-content/) | The content-design URL returned a page titled Writing to GOV.UK standards. The retire page describes withdraw and unpublish for GOV.UK. Guidance should usually be updated rather than withdrawn. News over a year old is an example of content that can be withdrawn. This is GOV.UK publishing guidance. An intranet is not GOV.UK. This starter does not withdraw or unpublish. |
| [sitePage resource](https://learn.microsoft.com/en-us/graph/api/resources/sitepage?view=graph-rest-1.0) and [list sitePage](https://learn.microsoft.com/en-us/graph/api/sitepage-list?view=graph-rest-1.0) | v1.0, opened 12 November 2026. `contentType` is `contentTypeInfo`. The property list does not include audience, review date, or owner. List pages: least privileged permission shown is `Sites.Read.All`; higher is `Sites.ReadWrite.All`. [Sites.Selected](https://learn.microsoft.com/en-us/graph/permissions-selected-overview) is a different page. The list-pages page does not say `Sites.Selected` is accepted. This starter calls neither API. |
| [Add SharePoint as a knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint) | The page says it describes the standard harness. The agent surfaces only content the user can access. Without permission it responds with no response. Read is the minimum stated. Hyperlinks inside a registered page are not crawled. SharePoint lists are described as ingested into Dataverse. The GitHub Copilot harness knowledge-sources page was not opened. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness follows the topics and rules the maker defines. The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. Agents on it use Copilot Credits. The page states no price. |

No FCA Handbook provision was opened. This starter does not apply a Handbook rule.

## What the draft does

`src/curate.py` reads one JSON snapshot and writes one JSON document. The same snapshot and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty until a stub receipt is recorded, and even then nothing is written to a tenant. `deleted`, `unpublished`, `moved`, and `permissions_changed` are false. Page bodies are not copied out. An identifier value is not copied out.

**Visible items.** An item is read only when one of the requesting user's principals is on its `readers` list. A missing list fails closed. Hidden items contribute a count. Their ids, titles, and text are not returned and are not passed to Experiments 08, 12, 44, or 49.

**Proposals.** Missing metadata (content type, owner, review date, audience). Inconsistent metadata, using negation-aware phrases. Duplicates and near-duplicates, with a token overlap and no copied text. Review dates before the as-of date. Published pages with no inbound link in the visible export (the export has no navigation, so this is not a finding that the page is unreachable). Links on a visible page that do not match a visible URL. Archive, only as a proposal, when a review date is more than the configured 365 days before the as-of date and the page is orphaned in the export or is news. Merge, only as a proposal, for a near-duplicate pair. A knowledge-gap topic, only when queries were supplied and Experiment 44 returned a content gap.

**Human queue, not curation.** An Experiment 08 identifier. An Experiment 49 sensitive reason (personal data, OFFICIAL-SENSITIVE, a higher marking, a legal hold). A sensitivity value other than empty, OFFICIAL, none, or unmarked. Any other value is queued. That is the open route. A short banner line that is not OFFICIAL is queued. A personal-data flag other than false or absent is queued. Text over 20,000 characters is not scanned and is queued. Queued items do not receive metadata, merge, or archive proposals.

**Negation.** A phrase after "not true that", "never mind, ignore", or another negation cue in the same sentence is not a positive match. Experiment 49 is called on that reduced text. Experiment 08 is called on the original visible text, so an identifier still queues the page.

**Prompt injection.** Instructions to delete, unpublish, move, change permissions, skip the queue, or treat the page as already approved are recorded. `followed` is false. An HTML comment is not used as evidence.

**Not synthetic.** A snapshot that is not marked synthetic is refused. The refusal does not echo the text. The CLI still exits 0.

`record_approval` accepts `approve_actions`, `reject_actions`, or `defer` from a separate approval object. The actor role has to be Site owner. Each approved id is named. A human-queue id cannot be approved as a change. If any item is queued, `queue_reviewed` has to be true before other proposals can be approved. That review does not curate the queued page.

`apply_approved_action` records a stub only after that approval. `sharepoint_called` and `graph_called` stay false. `metadata_applied_in_tenant` stays false.

`delete_page`, `unpublish_page`, `move_page`, and `change_permissions` raise `CuratorForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, 44, and 49 must be present beside this folder. Experiment 49 also calls Experiments 08, 12, and 19. Experiment 44 calls Experiments 08, 21, and 40 when the sector is public service.

```bash
cd experiments/50-sharepoint-knowledge-curator
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/curate.py --input examples/sample_site.json --as-of 2026-11-12
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once.

The exit code is 0 when a draft or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The content-type matcher is a small phrase list. Wording that is not on the list is not typed. A tie is not an inconsistency. This list is for metadata hygiene. It is not the safety hold.
- The safety hold is open on the sensitivity value: anything other than empty, OFFICIAL, none, or unmarked goes to a person. A closed list of sensitive labels is not the hold.
- Experiment 08 does not detect names, email addresses, or telephone numbers. No identifier is not a finding that the page has no personal data. The output is not anonymised.
- Experiment 12 reads `text/plain` only. A file over 20,000 characters is not scanned and is queued.
- Experiment 49's low-confidence file-plan result is not, by itself, a reason to queue the page. Sensitive reasons are.
- Experiment 44 runs only when the snapshot includes queries in its shape. It does not publish an outline. Its other finding kinds are counted and not turned into curation actions.
- The 365-day window is configuration. The GOV.UK retire page gives news over a year old as an example for GOV.UK. It is not a rule that an intranet page must be withdrawn.
- Orphan means no inbound link in this export. Navigation, search, and hub links are not in the snapshot.
- A link that does not resolve in the visible set is unresolved for this user. The draft does not say whether a hidden page exists at that URL.
- Article 84B, Article 6, Article 9, and section 48 were not opened.
- The GitHub Copilot harness knowledge-sources page was not opened. Whether `Sites.Selected` works for list sitePage was not stated on the list-pages page.
- The smoke test is not a model score.
- Building the GitHub Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Merrowfield Borough Council is fictional.
- This is not legal advice, a file plan, a DPIA, or an ATRS submission.

## UK GDPR

The manifest does not assert the controller's lawful basis. Article 6 and Article 9 were not opened on 12 November 2026. A safeguarding or sickness note can be special-category data. The starter does not assert an Article 9 condition.

Article 5(1)(d) and Article 5(1)(e) were read the same day. `accuracy_met` and `storage_limitation_met` stay false. The longer-storage limb cites Article 84B. That article was not opened. The code's paragraph 2.5 paraphrases Article 5(1)(e) in words from 2021. Those words are not quoted here as the current article text.

The agent does not make a disposal decision. Article 22A was not opened.

## Two Copilot Studio harnesses

Both call `src/curate.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness deletes a page or calls Graph. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The site owner pastes a snapshot, the flow returns JSON, the topic stops. A second topic records approval. A third runs the stub only when approval is already on the JSON. Microsoft's harness overview, opened 12 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a follow-up on the same JSON: which evidence matched, why an item is queued, why a stub did not run. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short narrative may be written from the JSON. The proposal ids, the confidence, and the empty approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- The document inventory: [../12-document-intake/](../12-document-intake/).
- The identifier gateway: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The records classification: [../49-records-classification/](../49-records-classification/).
- The knowledge-gap detector: [../44-knowledge-gap-detector/](../44-knowledge-gap-detector/).

## Project structure

```
experiments/50-sharepoint-knowledge-curator/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 12 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [Freedom of Information Act 2000, section 46](https://www.legislation.gov.uk/ukpga/2000/36/section/46)
- [Section 46 code of practice](https://www.gov.uk/government/publications/code-of-practice-on-the-management-of-records-issued-under-section-46-the-freedom-of-information-act-2000)
- [Writing to GOV.UK standards](https://www.gov.uk/guidance/content-design)
- [Retire outdated content](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/plan-manage-content/retire-content/)
- [Microsoft Graph sitePage](https://learn.microsoft.com/en-us/graph/api/resources/sitepage?view=graph-rest-1.0)
- [List sitePage](https://learn.microsoft.com/en-us/graph/api/sitepage-list?view=graph-rest-1.0)
- [Selected permissions overview](https://learn.microsoft.com/en-us/graph/permissions-selected-overview)
- [Add SharePoint as a knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
