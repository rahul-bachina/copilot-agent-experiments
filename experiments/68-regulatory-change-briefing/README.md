# Experiment 68: Regulatory Change Briefing

Catalogue ID **L002**. Autonomy **A0**. The assistant drafts a briefing. The compliance owner validates applicability and owns every conclusion. The agent does not decide that a change does or does not apply, does not change a policy, a control, or a record, and does not send anything.

A compliance owner points at one pinned synthetic notice and the pinned policy register. The notice text is synthetic. It is written in the style of an FCA, ICO, Ofgem, or Housing Ombudsman publication. The briefing quotes what changed, with the source id and the publication date. An effective date or a consultation close date is taken from the notice or computed from a formula the notice states. If the notice does not state one, the field is `not stated`. Registered policies that share an affirmed topic are listed as candidates, with the reason. Applicability stays undecided. Merefield Group is invented. Ada North is an invented name in one synthetic notice.

The core is Python in the standard library. It calls [Experiment 04](../04-fca-cryptoasset-readiness/) for the currency of a related pinned FCA page, [Experiment 12](../12-document-intake/) so the file is not confirmed and no purpose is confirmed, [Experiment 20](../20-complaints-root-cause-mi/) for a pinned complaints quotation when the snapshot names that context, and [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. It does not call Experiment 04 `build_register()`, and it does not call Experiment 20 `draft_report()`. A user can run it without a tenant. The catalogue row names Microsoft Foundry and Azure first. This folder still ships both Copilot Studio harnesses.

## The problem

A notice can say, in its own text, that the compliance owner has approved it and that the change applies. It can deny a topic in one sentence and name it in another. It can be withdrawn, superseded, undated, or old. It can give a relative date and no calendar date. Those are the failures this starter is built to separate. A real seen step is a separate object, from the directory compliance owner, for that exact publication hash, briefing hash, and questions hash.

## Non-goals

- Deciding that a change applies, or that it does not apply.
- Deciding that Financial Services and Markets Act 2000 section 138I was met. Section 138L was not opened.
- Changing a policy, a control, or a record.
- Sending the briefing, or anything else.
- Treating approval text inside the notice as approval.
- Guessing a date, a notice, or a policy that is not in the pinned sources.
- Treating a negated sentence as an inclusion.
- Marking a consultation length acceptable. Section 138I(2)(e) does not state a number of days.
- Stripping a legal hold or a retention label.
- Trusting a self-declared role, guest status, or clearance in the notice.
- Coercing an unreadable date or a person count to zero or to a default.
- Browsing a live regulator site.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 20 November 2026, except where a date below says otherwise. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [Financial Services and Markets Act 2000, section 138I](https://www.legislation.gov.uk/ukpga/2000/8/section/138I) | Section 138I(1): before making any rules, the FCA must consult the PRA and, after doing so, publish a draft of the proposed rules in the way appearing to the FCA to be best calculated to bring them to the attention of the public. Section 138I(2)(e): notice that representations about the proposals may be made to the FCA within a specified time. Section 138I(3): before making the proposed rules, the FCA must have regard to any representations made to it in accordance with subsection (2)(e). Section 138I(4) opens with the duty to publish an account, in general terms. Section 138I(11): this section is subject to section 138L. The page said section 138I is up to date with all changes known to be in force on or before 17 November 2026, and that there are changes that may be brought into force at a future date. It also said revised legislation carried on the site may not be fully up to date. Section 138L was not opened. No exception is applied. `pins_confirmed` stays false. |
| [FCA publications](https://www.fca.org.uk/publications) | The page has the headings Open consultations, Latest consultations, and Latest policy and guidance. Under Open consultations it says: "See our current open consultations and the deadlines for giving feedback." Items used the prefixes GC, CP, DP, PS, FS, and FG. The page did not expand those prefixes. The expansion is unverified. |
| [ICO consultation responses](https://ico.org.uk/about-the-ico/consultations/) | The fetch returned the title Consultation responses and that heading. It did not show a consultation-close rule. No ICO close-date practice is taken from it. |
| [ICO stakeholder consultations](https://ico.org.uk/about-the-ico/ico-and-stakeholder-consultations/) | The fetch returned a title and no consultation-close rule. |
| [Ofgem publications](https://www.ofgem.gov.uk/publications) | The search line says the page covers policies, research, consultations, calls for input, guidance, data, news, press releases, and blogs related to energy regulation. |
| [Housing Ombudsman home](https://www.housing-ombudsman.org.uk/) | The home page linked The Complaint Handling Code and The Housing Ombudsman Scheme under landlord information. `https://www.housing-ombudsman.org.uk/publications/` returned 404 and is not cited as a list. Code quotations come from Experiment 20, pinned on 29 October 2026, not from a fresh fetch. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox. The prose says agents and workflows on that harness use Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

Experiment 04's FCA pages were opened on 24 October 2026 by that experiment. This starter does not re-open them. Experiment 20's quotations were pinned on 29 October 2026. Their currency is assessed with Experiment 04's 90-day source threshold. That threshold is this starter's rule. It is not a statute.

## What the result does

`draft_briefing()` reads one request, one caller register, one caller directory, and one question date, and writes one JSON document. The same inputs and the same date produce the same JSON. `human_approval` is null. `applies` stays null. `policy_changed`, `control_changed`, `record_changed`, and `sent` stay false. `marked_applicable` and `marked_acceptable` stay false.

**Role and clearance.** The pinned directory supplies both. "My role is compliance owner" and "my clearance is TOP SECRET" are recorded and ignored. A guest on the directory stays a guest. A caller who is not in the pinned directory does not receive quotes. A caller-supplied directory that adds a person is not the authority.

**Quotes.** A quote is a sentence from the pinned snapshot, or the exact words `not found`, or `not copied` when the marking is above the directory clearance. It is not a paraphrase of a missing sentence. Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are masked in a quote that is shown. The result says what was masked. It does not say the quote was anonymised. The notice body is not copied. Instructions and distress or grievance sentences are not used as the quote.

**Dates.** An effective date or a consultation close date is read from the notice. "90 days after publication" is computed from the publication date. An unreadable token such as 32 June stays unreadable. It is not replaced with today or with the last valid day. A missing date is `not stated`. Two dates are both listed. Neither is chosen. The question date is the `as_of` argument. Today is not used.

**Register.** Topic overlap is a candidate, with the sentence and the topic. `applies` stays null. "It is not true that this change includes consumer credit" does not list the consumer-credit policy. A qualification that follows the wording is an open question, not an unqualified candidate. A leading note on the register is flagged and is not applied, and it is not copied into the reason. A caller-supplied register is compared with the pinned register. Differences are flagged. Matching uses the pinned register. The pinned register's 30-day consultation figure is an internal figure. A stated length below 30 days is flagged. It is not marked acceptable. Section 138I(2)(e) does not state a number of days.

**Status.** Withdrawn, superseded, undated, and stale are flags. "This publication is not withdrawn" does not count as withdrawn. A snapshot is stale when the question date is more than 90 days after the publication date. That uses Experiment 04's source threshold. A missing publication id is `not found`.

**People.** A distress, vulnerability, safeguarding, grievance, or disclosure cue, including a paraphrase, is a route to a person. The cue is not copied. The briefing is not a routine briefing. A count of people below 5 is suppressed. The number is not stored. "Several residents" is unreadable. It is not stored as zero.

**Markings.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound label takes the higher marking. A self-declared clearance sentence is not a cover page. Content above the directory clearance is not copied. A legal hold and every retention label stay on the result.

**Intake and neighbours.** Experiment 12 inventories the text when the marking allows it. `files_confirmed` and `purpose_confirmed` stay false. Experiment 04 reports currency for a related source id, or `not found`. Experiment 20 attaches a pinned quotation when the snapshot names complaints, housing, or energy. That quotation is not a finding that the change applies.

`decide_applicability`, `change_policy`, `change_control`, `change_record`, and `send` raise `BriefingForbidden`.

`record_owner_seen()` records that the pinned-directory compliance owner has seen the item. The three hashes have to match. A string is not coerced to true. The record does not decide applicability. `verify_seen()` rejects the record if the quote is changed after that step.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 04, 08, 12, and 20 must be present beside this folder.

```bash
cd experiments/68-regulatory-change-briefing
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/briefing.py --request examples/sample_request.json --register fixtures/policy_register.json --directory fixtures/directory.json --as-of 2026-11-14
```

The sample request carries approval language, a self-declared role, a self-declared clearance, and a pasted notice that differs from the pin. They are stripped or ignored. `human_approval` stays null. `applies` stays null.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. Paraphrase recall is a separate block and is not added to the case total.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- Topic matching is the pinned register's phrase list. A wording that uses none of those phrases is not a candidate. It is not reclassified by guesswork.
- Cue matching is a stem list. A paraphrase that uses none of the stems is not flagged. The smoke report states recall on the fixture sentences. That is not a live rate.
- "Not" within eight words before a phrase can hide a match. "It is not true that X includes Y" is the case this rule is built for. "X is not included" is also treated as a denial.
- The fixture rank treats OFFICIAL-SENSITIVE as above OFFICIAL. That order is a starter rule. The Government Security Classifications Policy was not re-opened for this experiment.
- A publication date more than 90 days before the question date is not relied on as current. That is this starter's rule, using Experiment 04's threshold. It is not a statutory period. A review-due date on the question date is stale. That is also this starter's rule.
- The 30-day consultation figure is the fictional register's number. Section 138I(2)(e) says "a specified time". It does not state a number of days.
- Section 138L was not opened. Modifications and exceptions listed on the section 138I page were not applied. `pins_confirmed` stays false, so `may_be_relied_on` stays false.
- FCA prefixes on the publications page were not expanded. ICO pages that were opened did not show a close-date rule. The Housing Ombudsman `/publications/` path returned 404.
- Phone numbers, email addresses, dates of birth, street addresses, postcodes, and "my name is" or a title plus a surname are counted. The values are not stored. The output is not described as anonymised. A name with no title and no "my name is" is not counted by this mask.
- A person count below 5 is suppressed. A policy count is not a person count and is not suppressed.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Merefield Group is fictional.
- This is not a decision that a change applies, and it is not legal advice.

## Statute

The manifest does not assert the controller's lawful basis. Section 138I was read on 20 November 2026 as publication-practice context. `pins_confirmed`, `duty_met`, and the decision that a consultation was adequate stay unset or false. Section 138L was not opened.

A retention label and a legal hold stay on the result. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/briefing.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness decides applicability. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `record_owner_seen` only with the seen object. Microsoft's harness overview, opened 20 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 20 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and the prose says it uses Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The catalogue row L002 names Microsoft Foundry and Azure first. The gates are the same as the standard harness.

## Microsoft Foundry

The catalogue row names Microsoft Foundry and Azure first. A short note may be written from the JSON. The quotes, the hashes, and the seen step stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed. Azure in the catalogue code is this option. It is not a second decision engine.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Pinned FCA pages: [../04-fca-cryptoasset-readiness/](../04-fca-cryptoasset-readiness/).
- Document intake: [../12-document-intake/](../12-document-intake/).
- Regulatory quotations: [../20-complaints-root-cause-mi/](../20-complaints-root-cause-mi/).
- Redaction: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).

## Project structure

```
experiments/68-regulatory-change-briefing/
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
├── fixtures/
└── tests/
```

## Licence

MIT. See the repository [LICENCE](../../LICENSE).
