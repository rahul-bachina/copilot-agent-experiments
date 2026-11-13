# Experiment 55: OneDrive Document Finder

Catalogue ID **M007**. Autonomy **A0**. The requesting user selects the permitted locations. The assistant searches only there.

UK public bodies and regulated firms keep files in OneDrive and in SharePoint. A person asks, in ordinary language, for the housing repairs note, and needs a short list: which file, why it matched, where it sits, when it was last modified, and what sensitivity label it carries. They also need a plain sentence when nothing in the places they chose matches, and a flag when a copy looks stale, superseded, or duplicated.

This starter does that against one synthetic index. It does not call Microsoft Graph, the Microsoft Search API, Work IQ, or Microsoft Purview. It does not move, delete, share, or change permissions. A file outside the confirmed locations is counted and not listed. A file the user's principals cannot read is counted and not listed. A file labelled above the user's clearance in the fixture is counted and not listed. The sample does not widen access.

The organisation in the samples is Merrowfield Borough Council. It is invented. The clearance order used here, which treats OFFICIAL-SENSITIVE as above OFFICIAL for the purpose of withholding content, is a fixture rule. The Government Security Classifications Policy opened on 13 November 2026 names three tiers and describes the -SENSITIVE marking as an additional marking on OFFICIAL. It does not define this software order.

Stack in the catalogue: Microsoft 365 and Work IQ. The finder itself is Python in the standard library. It calls [Experiment 49](../49-records-classification/) so a legal hold and a personal-data indicator are not re-coded, [Experiment 50](../50-sharepoint-knowledge-curator/) for duplicate signals among files already admitted, and [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifier types. A user can run it without a tenant.

## The problem

A search that opens the finance library because a file says "search all locations", or that quotes a SECRET brief to a user cleared to OFFICIAL-SENSITIVE, is the failure this starter is built to refuse. The user still has to see the rank, the reason, the location, the date, and the label.

## Non-goals

- Searching a location the user has not confirmed on the selection object.
- Returning a title, an id, or an extract the user's principals cannot already read.
- Returning content from a file labelled above the user's clearance in the fixture.
- Stripping a sensitivity label, a retention label, or a legal hold.
- Moving, deleting, sharing, or changing permissions, including after acknowledgement.
- Calling Microsoft Graph, the Microsoft Search API, Work IQ, or Purview.
- Deciding that UK GDPR Article 5(1)(c) was met. `data_minimisation_met` stays false.
- Deciding the Freedom of Information Act 2000 section 1 duty to confirm or deny.
- Deciding that a Government Security Classifications marking is correct.
- Treating a safeguarding or distress cue as an ordinary hit.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 13 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(c) is data minimisation: adequate, relevant and limited to what is necessary. Article 5(2) is accountability. Article 6 and Article 9 were not opened. No lawful basis is asserted. |
| [Freedom of Information Act 2000, section 1](https://www.legislation.gov.uk/ukpga/2000/36/section/1) | Section 1(1) is the right to be told whether information of the description specified is held, and if so to have it communicated. Section 1(3) is further information needed to identify and locate it. The page said there are currently no known outstanding effects. This starter does not decide that duty. |
| [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html) | Updated 5 August 2024. Paragraph 1: not a statutory scheme. Paragraph 5: three tiers, OFFICIAL, SECRET and TOP SECRET. Paragraph 25: the -SENSITIVE marking is an additional marking on OFFICIAL. Principle Five is need-to-know balanced with need-to-share. |
| [What is Microsoft Copilot?](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-overview) | Experiences differ by grounding, integration, and licensing. Access is scoped by user permissions. Work-data grounding is described as Microsoft Graph and Work IQ where the experience includes work data. |
| [Knowledge sources summary](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio) | SharePoint uses GraphSearch with the agent user's Entra ID authentication. The note says the agent only surfaces content that user can access. OneDrive files and folders are named as unstructured data with different limits. The limits page was not opened. |
| [Search OneDrive and SharePoint](https://learn.microsoft.com/en-us/graph/search-concept-files) and [search query](https://learn.microsoft.com/en-us/graph/api/search-query?view=graph-rest-1.0) | `POST /search/query` with `driveItem` searches files. Example 4 on the files page says the query covers content the signed-in user can read. The query page lists delegated Mail.Read as least privileged, and application Files.Read.All as least privileged. Whether a driveItem-only call accepts a narrower delegated scope, and whether application permissions are trimmed to one user, was not stated. This starter calls neither API. |
| [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/) and [API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/api-overview) | Permission-aware. Delegated authentication. Application-only authentication is not supported. The API overview says Microsoft 365 permissions, sensitivity labels, and compliance policies are enforced automatically. Usage-based billing, independent of a Microsoft 365 Copilot licence, is on the overview. A general-availability date was not on the pages opened. That date is unverified. |
| [Sensitivity labels](https://learn.microsoft.com/en-us/purview/sensitivity-labels) | Labels are customisable. The page's examples include Personal, Public, General, Confidential, and Highly Confidential. A label is clear text in metadata and stays with the content. A document can carry one sensitivity label and a retention label. Copilot and agents are said to recognise sensitivity labels. Data Map labelling is described as currently in preview. The licensing table was not opened. A fixture's Government Security Classifications marking is not a Purview label. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses are named: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The standard harness follows the topics and rules the maker defines. The Microsoft Copilot harness is described for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The page states no price. The page does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

No FCA Handbook provision was opened. This starter does not apply a Handbook rule.

## What the result does

`src/find.py` reads one index, one request, and one selection object, and writes one JSON document. The same inputs and the same as-of date produce the same JSON. `human_approval` is null until `acknowledge_results`. `moved`, `deleted`, `shared`, and `permissions_changed` stay false. A full extract is not copied out.

**Confirmed locations.** `selection.confirmed` has to be the boolean true, and the actor role has to be Requesting user. Location ids, principals, and clearance come from that object. The same keys on the index are stripped. A sentence in a file that says the locations are confirmed is recorded and not followed.

**Admitted files.** A file is read only when its location is in the confirmed set, one of the user's principals is on `readers`, and the fixture label is at or below the fixture clearance. A missing readers list fails closed. An unrecognised label fails closed. Hidden files contribute a count. Their ids, titles, and extracts are not returned.

**Hits.** Every query term has to appear in the title, the location name, or the extract after negation is removed. The rank uses the title first, then the extract, then the location name. Each hit carries the reason, the location, the last modified date, and the sensitivity label as supplied. A retention label and a legal hold are kept. A likely duplicate, a superseded version, and a file last modified more than 365 days before the as-of date are flagged. The 365-day window is configuration, not a statutory period. A later version that the user cannot see is not named.

**Nothing matches.** The plain statement is: "Nothing in the permitted locations matches this request."

**Safeguarding.** A distress or safeguarding cue in the text that remains after negation is not a routine hit. The extract is not copied. Acknowledgement is refused until `queue_reviewed` is true on a separate review object.

**Not synthetic.** An index that is not marked synthetic is refused. The refusal does not echo the text. The CLI still exits 0.

`acknowledge_results` accepts `acknowledge` or `defer`. It refuses `delete_file`, `move_file`, `share_file`, and `change_permissions`. `executed` stays false.

`move_file`, `delete_file`, `share_file`, and `change_permissions` raise `FinderForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 08, 12, 19, 49, and 50 must be present beside this folder. Experiment 49 calls Experiments 08, 12, and 19. Experiment 50 calls Experiments 08, 12, and 49, and Experiment 44 only when a snapshot includes queries. This call does not pass queries.

```bash
cd experiments/55-onedrive-document-finder
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/find.py --index examples/sample_index.json --request examples/sample_request.json --selection examples/sample_selection.json --as-of 2026-11-13
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 18 passed, 0 failed, 0 errors, 18 cases.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is a word list. A paraphrase that shares no word with the title, the location name, or the extract is a non-match. That is not a statement that the file is irrelevant.
- The fixture clearance order is not a sentence of the Government Security Classifications Policy.
- Experiment 08 does not detect names, email addresses, telephone numbers, or dates of birth. This starter also masks honorific names, email addresses, UK phone numbers, dates of birth next to a birth cue, and street addresses on any snippet. A name with no honorific is not masked. The output is not anonymised.
- A file over 20,000 characters is not scanned. A title can still match.
- Experiment 49's file-plan category is not copied out. Legal hold and personal-data indicators are.
- Experiment 50 is asked only for duplicate signals among files already admitted. An archive proposal is not followed. SharePoint is not called.
- Article 6, Article 9, and the Copilot Studio OneDrive limits page were not opened. A Work IQ general-availability date was not on the pages opened. Whether application search permissions are trimmed to one user was not stated.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Merrowfield Borough Council is fictional.
- This is not legal advice, a file plan, a DPIA, or an ATRS submission.

## UK GDPR and records

The manifest does not assert the controller's lawful basis. Article 6 and Article 9 were not opened on 13 November 2026. A safeguarding note can be special-category data. The starter does not assert an Article 9 condition.

Article 5(1)(c) was read the same day. The result keeps a location, a date, a label, a reason, and a short snippet only when the extract matched. `data_minimisation_met` stays false.

Section 1 of the Freedom of Information Act 2000 was read the same day, including the words in section 1(3) about identifying and locating information. `foi_duty_decided` stays false. This starter does not answer a request and does not decide an exemption.

The agent does not make a disposal decision. A legal hold and a retention label stay on the hit. Article 22A was not opened.

## Two Copilot Studio harnesses

Both call `src/find.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness searches outside the selection or calls Graph. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The user confirms locations, the flow returns JSON, the topic stops. A later topic records acknowledgement only from a separate review object. Microsoft's harness overview, opened 13 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 13 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, billed in Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short note may be written from the JSON. The ranks, the reasons, the labels, and the empty approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Records classification: [../49-records-classification/](../49-records-classification/).
- SharePoint knowledge curator: [../50-sharepoint-knowledge-curator/](../50-sharepoint-knowledge-curator/).
- Identifier gateway: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/55-onedrive-document-finder/
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

## References opened on 13 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [Freedom of Information Act 2000, section 1](https://www.legislation.gov.uk/ukpga/2000/36/section/1)
- [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html)
- [What is Microsoft Copilot?](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-overview)
- [Knowledge sources summary](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)
- [Search OneDrive and SharePoint content](https://learn.microsoft.com/en-us/graph/search-concept-files)
- [searchEntity: query](https://learn.microsoft.com/en-us/graph/api/search-query?view=graph-rest-1.0)
- [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/)
- [Work IQ API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/api-overview)
- [Purview sensitivity labels](https://learn.microsoft.com/en-us/purview/sensitivity-labels)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
