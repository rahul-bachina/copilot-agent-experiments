# Experiment 19: Privacy Impact Assessment Assistant

Catalogue ID **L006**. An assistant for a project team drafting a data protection impact assessment. Stack in the catalogue: Copilot Studio and Power Platform. Autonomy **A1**.

It screens one synthetic project brief against UK GDPR Article 35(1) and (3) and the ICO's list of processing likely to result in high risk. It screens solely automated significant decisions against UK GDPR Articles 22A to 22D, inserted by the Data (Use and Access) Act 2025. It drafts the description of the processing, the necessity and proportionality section, and the risk and mitigation sections. It flags when prior consultation under Article 36(1) may need to be considered. It can take an [Experiment 03](../03-agent-inventory-atrs-assurance/) inventory record, or a permissions manifest, and copy empty fields. Free text goes through [Experiment 08](../08-uk-pii-redaction-gateway/) before it is copied into the draft.

**Status.** Available as a local starter. The draft runs in Python with no Azure credentials and no network. It is not an importable Copilot Studio solution, and a live model has not been scored.

The privacy officer approves the assessment. The project owner accepts residual risk. The agent does not. `dpia_required` stays null. `article_36_consultation_required` stays null. `lawful` stays null.

Samples are synthetic. Northwharf Borough Council is fictional. The National Insurance value in the sample is the non-allocatable fixture documented in Experiment 08.

## The problem

A project team has to decide whether a DPIA is needed, and then write one, before processing starts. Article 35(1) is the test. Article 35(3) names three types that shall in particular be required. Article 35(4), as revised, says the Commission shall publish a list. The ICO's pages still publish a list of ten types and say the guidance is under review because of the Data (Use and Access) Act. A language model that fills the form from memory will invent a lawful basis, a sign-off, and a decision that the ICO need not be consulted.

This starter is the screening and the first draft. The decision stays with the privacy officer.

## Who it helps

**A project team.** They answer a closed questionnaire and get the Article 35(7) sections back, with gaps left as gaps.

**A privacy officer, or a data protection officer where one is designated.** They see which recorded answers match Article 35(3) or the ICO list, what Articles 22A to 22D would ask, and whether a residual risk is recorded as High. Article 35(2) says the controller shall seek the DPO's advice where a DPO is designated. The advice line in this draft is blank.

**A project owner.** They are the person named to accept residual risk. This agent does not accept it for them.

**Someone who already has an Experiment 03 inventory.** Empty description, necessity, Article 22, and risk fields can be copied from that record. Screening answers are not inferred from it.

It does not help a team that wants the tool to sign the DPIA, reject the project, or email a consultation.

## Non-goals

- Approving, rejecting, or signing off a DPIA.
- Deciding that Article 35 requires a DPIA, or that it does not.
- Deciding that Article 36(1) requires prior consultation, or sending that consultation.
- Deciding that processing is lawful, or that an Article 22B condition is met.
- Applying the ICO's stated exception for genetic data processed by an individual GP or health professional for direct care.
- Applying Article 35(10), or the ICO's description of when a DPIA may already have been done.
- Accepting residual risk.
- Writing a production record, including a DPIA register, Dataverse, or SharePoint.
- Inferring a screening answer from an inventory or a manifest.
- Treating a manifest that disables a regulated decision as meaningful human involvement under Article 22A(1)(a).
- Re-implementing Experiment 08.
- Reading WP248, Article 6, Article 9, Article 14, or any regulations made under Article 22D.
- Autonomy A3.

## What the draft does

`src/assess.py` reads one JSON brief and an as-of date and writes one JSON document. The same inputs produce the same JSON. `approved`, `signed_off`, and `residual_risk_accepted` are false. `actions_taken` is empty.

**Article 35.** A recorded yes on Article 35(3)(a), (b), or (c) is reported as `article_35_3_recorded`. A recorded no on the team's view of Article 35(1) does not clear that. Every screening answer is yes, no, or unknown. Missing is unknown, not no.

**ICO list.** The ten types are the types on the ICO when-page and the examples page, both opened on 28 October 2026. Five of them are recorded as list triggers only when another criterion from the nine European criteria on the when-page is also yes. Innovative technology does not count its own twin, "innovative use", as that other criterion. The pages say the guidance is under review. This tool does not decide that the page is the list Article 35(4) now requires the Commission to establish.

**Article 22A to 22D.** The screen uses the revised text on legislation.gov.uk. Section 80 came into force for specified purposes at Royal Assent. The Article 22A page dates that specified-purposes commencement 19 June 2025. It came into force on 5 February 2026 in so far as not already in force, by S.I. 2026/82 regulation 2(j), with regulation 5. A decision the brief dates before 5 February 2026 is not run through the new test. Regulation 5 is not interpreted. Law-enforcement processing (sections 50A to 50D) and intelligence-services processing (section 96(4)) are named and are not screened as Article 22A. No Article 22D regulations were read.

**Sections.** Description, necessity and proportionality, risks, and measures follow Article 35(7)(a) to (d) and the ICO's seven steps. A gap stays a gap. A mitigation string is not recorded as in place. The ICO likelihood and severity matrix is not scored.

**Article 36.** A residual recorded as High sets `prior_consultation.code` to `high_residual_recorded`. The statutory addressee in the revised Article 36(1) is the Commission. The word was substituted on 30 September 2026. The ICO consultation page still says to consult the ICO and still gives an email address. The draft quotes both and does not reconcile them. Nothing is sent.

**Pre-fill.** An Experiment 03 inventory can fill empty narrative, Article 22 facts, and risk rows. A permissions manifest can fill the project name, a description, and a basis string other than "Not asserted". Neither source answers the screening questionnaire.

**Redaction.** Each free-text field is passed to Experiment 08 `propose()`. Model suggestions are off. The reversible vault is not requested. `output_is_anonymised` stays false.

**Prompt injection.** Instructions in the body, in an HTML comment, after a form feed, after blank lines, or between zero-width characters are recorded. `followed` is false. The phrase is removed from the copied section. A payload key such as `approved` is stripped.

**Human steps, outside `assess()`.** `approve_assessment`, `reject_assessment`, `sign_off_assessment`, `accept_residual_risk`, `send_prior_consultation`, and `write_production_record` raise `AssessmentForbidden`. `record_external_attestation` accepts only `caller` `human_outside_agent`, only the roles named in the manifest, and only a matching checksum. The skills say the agent must not call it. The effect is none. The draft stays a draft.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiment 08 must sit beside this folder, which it does in this repository. PyYAML is required only for `--manifest`.

```bash
cd experiments/19-privacy-impact-assessment
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/assess.py --input examples/sample_project.json --as-of 2026-10-28
```

An Experiment 03 inventory can be passed with `--inventory`. A manifest can be passed with `--manifest`.

`eval/evaluate.py` prints a **deterministic smoke test** of 24 synthetic briefs. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done.

The exit code is 0 when a draft is produced, including when a screening result is serious or an injection phrase is present. Those are findings, not an approval. A brief that is not marked synthetic is refused, and the refusal does not echo the body.

## Limitations

- **The screen is not a DPIA and not a decision.** `dpia_required` is null on every result, including `recorded_answers_do_not_indicate`.
- **The ICO pages are under review.** Each DPIA page opened on 28 October 2026 says the Data (Use and Access) Act means the guidance may change. The when-page still says the ICO is required by Article 35(4) to publish the list. The revised Article 35(4) says the Commission. This tool does not decide which text a controller must follow.
- **Combination items are not completed triggers on their own.** The when-page says that for innovative technology, biometric data, genetic data, invisible processing, and tracking. A single factor can still be a reason to do a DPIA. This tool records that and does not choose.
- **The genetic-data exception is not applied.** Nor is Article 35(10). The ICO says it has not issued a list of processing that does not require a DPIA.
- **WP248 was not opened.** The nine criteria are the nine bullets on the ICO when-page.
- **Article 6, Article 9, and Article 14 were not opened.** Article 22B(4) refers to Article 6(1)(ea). A basis string is matched as text. It is not confirmed.
- **Article 22D regulations were not read.** Safeguards recorded as present are not a clearance. S.I. 2026/82 regulation 5 was not interpreted.
- **Law-enforcement and intelligence-services tests are not run.**
- **The 90-day window is not a statutory review period.** Article 35(11) is the controller's duty. This flag only says the pin of 28 October 2026 is older than 90 days before the as-of date.
- **Experiment 08's misses are inherited.** Names, email addresses, and telephone numbers are not redacted. The draft must not be described as anonymised.
- **The injection list is a word list.** A novel instruction would pass it. The privacy officer still reads the draft.
- **Pre-fill can copy a stale or wrong inventory sentence.** Copied fields are marked. They are not the project team's answers until a person treats them as such.
- **The smoke test is not a model score.**

This is not legal advice, a DPIA, or a statement that a project complies with UK GDPR. The manifest does not assert an Article 6 basis. The adopting organisation confirms its own.

## Two Copilot Studio harnesses

Both call `assess()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness approves the assessment, accepts residual risk, or sends a consultation. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic for a project team and a privacy officer. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution. It is not a public chat. The Customer Conversation harness is the wrong harness, because this draft is an internal assessment.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a reviewer who wants the draft explained. It is not the GitHub Copilot service. Skills are in [skills/](skills/). The harness overview, opened 28 October 2026, says agents and workflows on that harness use Copilot Credits. The comparison table on that page points the GitHub Copilot harness billing cell at a separate overview, which was not opened. No price is copied. A last-updated line was not in the text retrieved. The overview did not mark the harness itself as preview.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).
- The gateway this experiment calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The inventory shape it can read: [../03-agent-inventory-atrs-assurance/](../03-agent-inventory-atrs-assurance/).

## Project structure

```
experiments/19-privacy-impact-assessment/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── assess.py
│   ├── automated.py
│   ├── injection.py
│   ├── prefill.py
│   ├── screening.py
│   └── sources.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 28 October 2026

Legislation and ICO pages are quoted from the addresses below. The operative words used in the draft are in `src/sources.py`.

- [UK GDPR Article 35](https://www.legislation.gov.uk/eur/2016/679/article/35). No known outstanding effects are listed. Article 35(4) and (5) show "the Commission", substituted on 30 September 2026 by S.I. 2026/386, Schedule 3, paragraph 41, in force by [S.I. 2026/1015 regulation 2(c)](https://www.legislation.gov.uk/uksi/2026/1015/regulation/2/made).
- [UK GDPR Article 36](https://www.legislation.gov.uk/eur/2016/679/article/36). The same substitution. Article 36(1) says the controller shall consult the Commission where a DPIA indicates the processing would result in a high risk in the absence of measures taken by the controller to mitigate the risk.
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A). Annotated as substituted for Article 22 on 19 June 2025 for specified purposes, and on 5 February 2026 in so far as not already in force, by Data (Use and Access) Act 2025 sections 80(1) and 142(1) and (2)(h), and by S.I. 2026/82 regulation 2(j), with regulation 5.
- [Data (Use and Access) Act 2025 section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80). The same commencement footnotes. Articles 22A to 22D, and the law-enforcement and intelligence-services amendments, are in this section.
- [S.I. 2026/82 regulation 5](https://www.legislation.gov.uk/uksi/2026/82/regulation/5/made), original version as made. The amendments made by section 80 and Schedule 6 do not apply to a decision taken before 5 February 2026 to which Article 22(3) of the UK GDPR, or section 14(1) or 50(2) of the Data Protection Act 2018, applied. This tool has not interpreted that saving.
- [Data (Use and Access) Act 2025 section 119](https://www.legislation.gov.uk/ukpga/2025/18/section/119). In force on 30 September 2026 by S.I. 2026/1015 regulation 2(c). Functions of the Information Commissioner transfer to the Information Commission.
- [ICO, When do we need to do a DPIA?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/when-do-we-need-to-do-a-dpia/) The page carries the Data (Use and Access) Act review banner. It lists Article 35(3), ten ICO types, and nine WP29 criteria. It says the ICO has not issued a list of processing that does not require a DPIA.
- [ICO, Examples of processing likely to result in high risk](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/examples-of-processing-likely-to-result-in-high-risk/). The same banner. This is the longer description of the ten types.
- [ICO, How do we do a DPIA?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/how-do-we-do-a-dpia/). Seven steps. Step 7 says that if a high risk remains you need to consult the ICO before going ahead.
- [ICO, Do we need to consult the ICO?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/do-we-need-to-consult-the-ico/). The page says the focus is residual risk after mitigation, and it gives `dpiaconsultation@ico.org.uk`. That address is not a tool of this agent.
- [ICO news, 15 September 2026, updated 17 September 2026](https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2026/09/ico-governance-changes-confirmed-for-30-september-2026). The organisation continues to be known as the ICO.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview). A last-updated date was not in the text retrieved.

Not opened, and not applied:

- WP248 rev.01. The nine criteria are taken from the ICO when-page, which cites it.
- UK GDPR Articles 6, 9, and 14.
- Any regulations made under Article 22D.
- The billing overview and the standard-harness licensing article linked from the harness comparison table.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
