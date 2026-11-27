# Experiment 85: Visit and Meeting Notes to Structured Case Record

Catalogue ID **UK13**. Autonomy **A1**. The starter turns a practitioner's synthetic visit transcript or rough notes into a draft structured case note. The named practitioner reviews it and approves the exact note. The agent does not write the case record, does not share the note, and does not assess eligibility, risk, or need.

This is not [Experiment 12](../12-document-intake/), which inventories a file and stops. This starter calls it for rough notes. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) to count UK identifiers, then masks phones, emails, dates of birth, postal addresses, personal names, and NHS numbers as well. Those rules are not copied here.

Status: **Available** as a local starter. No tenant is configured. Northmarsh Council is invented.

## Problem

A visit note has to say who was there, what was discussed, what the person said they want, what the practitioner observed, and what was agreed, with a name and a date. A transcript also contains crosstalk, a possible misheard line, third-party remarks, and personal data. A sentence in the transcript can claim the note is already approved, or can ask the agent to decide eligibility.

## Who it helps

A social worker or housing officer who wants a first draft tied to the transcript line, before they edit it and approve that exact draft. The organisation gets a record that the approval was bound to the agent-held copy and its hash.

A line that shows safeguarding, self-neglect, domestic abuse, distress, a suicidal statement, financial abuse, or a capacity concern is flagged for the practitioner. The flag is not an assessment.

## What it does

Given a synthetic adult social care or housing-support transcript, and the date the question is about, the starter drafts the pinned template:

- who was present
- what was discussed
- the person's own words and wishes
- observations
- agreed actions, with an owner and a date only when the line states them
- follow-ups

Every copied line cites that line. `inferred` stays false for a verbatim line. A claim that is not a span of the cited line is not support. The grounding score on the labelled set, including negative controls, is in `eval/smoke_report.json`. It is a smoke test.

The person's lines are not stored as the practitioner's observations. Third-party remarks are marked and kept out of the person's own words. Crosstalk, an unclear line, and a misattributed line are flagged. The speaker is not guessed.

Consent to recording is recorded only when the structured status is `given` and a clear line from the person affirms it. A missing, refused, qualified, or uncorroborated consent is flagged. A refusal is routed to the practitioner.

Dates use the same reading as Experiments 68 to 70, as carried in later starters: `12/12/2024` is one day, `01/02/2024` is ambiguous, a future date is flagged against the question date, and an unreadable token is not stored as zero.

Care Act 2014 section 9(1), section 9(4)(b), and section 42(1) to (3) were opened on 27 November 2026 and are quoted in `src/sources.py`. UK GDPR Article 9(1) and Caldicott principles 3 and 8 were opened the same day. The NHS England Digital page on ambient scribing was opened the same day. The quotes are context. They are not a needs assessment and not a decision to make a section 42 enquiry.

## Non-goals

- It does not write to the case record.
- It does not share or send the note.
- It does not assess eligibility, risk, or need, and it does not decide a safeguarding enquiry.
- It does not invent a fact, a diagnosis, or a quote.
- It does not treat an approval, a role, or a clearance written in the transcript as the approval step.
- It does not apply a caller-supplied template or directory.
- It does not drop a protective marking, a legal hold, or a retention label.
- It does not guess a speaker when the audio is unclear, crossed, or marked misattributed.
- It does not call a live model. The smoke test is deterministic.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/notes.py --request examples/sample_request.json --as-of 2026-11-20
.venv/bin/python -m pytest tests/ -q
.venv/bin/python eval/evaluate.py
```

The core is the Python standard library. Experiments 08 and 12 must sit beside this folder. No network call is made.

## Honest limitations

- The paraphrase set is a fixture of 22 sentences in each of seven categories. The smoke recall is 22/22 on that fixture, and 0 of 22 negative controls were flagged. A sentence that uses none of those stems is not flagged. That is not a live recall rate.
- A negated stem is still routed. It is not recorded as an affirmed finding. Seven negated fixtures are routed that way.
- The grounding score is 20 supported spans and 20 negative controls, precision 1 and recall 1, on that labelled set. It is not a model score. Those figures are not added to the 20-case total.
- Masking is not anonymisation. `described_as_anonymised` stays false. The note includes the masked text, and the report says so.
- Working days skip Saturday and Sunday. Bank holidays are not applied.
- The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.
- The small-number threshold of 5 is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.
- Article 6 was not opened. No lawful basis is asserted. Article 9(2)(h) was on the page with editorial footnote markers and is not quoted in full. Data Protection Act 2018 sections 10 and 11 were not opened.
- Care Act 2014 sections 1, 2, 4, and 11 were named in section 9 and were not opened.
- Published local-authority pilot pages were not opened on 27 November 2026. No supplier result and no figure from those pages is stated.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 27 November 2026. Treat that product behaviour as unverified.
- The harness overview was opened on 27 November 2026. It names a Microsoft Copilot harness. It does not use the words GitHub Copilot harness. The page says that harness retries and finds alternative paths. This starter does not enable that. The common-brief sentence that this harness is not the GitHub Copilot service was not on that page. That sentence is unverified.
- Catalogue row UK13 names Azure, Microsoft Foundry, and Power Platform. This folder ships both Copilot Studio harnesses and a Microsoft Foundry note. No Power Platform solution is imported and no Azure resource is deployed.

## Layout

```text
experiments/85-visit-notes-case-record/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── tests/
├── eval/
├── fixtures/
├── schema/
├── skills/
├── copilot-studio/
└── docs/
```

The licence is MIT.

`permissions.yaml` is the same file as `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json`.
