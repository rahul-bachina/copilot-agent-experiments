# Form Extraction Assistant

Catalogue ID **O002**. Autonomy **A1**. A reviewer pastes a synthetic completed form. The starter extracts each pinned field with a page, line, or box id and a confidence, and it returns a review sheet of the material fields. The named reviewer approves that exact draft before a row is written to a synthetic staging store.

The catalogue checkpoint is "Reviewer validates material fields". The catalogue stack is Azure AI Document Intelligence and Power Platform. What you can run today is Python in the standard library. It calls [Experiment 12](../12-document-intake/) (O001, document intake), which calls [Experiment 08](../08-uk-pii-redaction-gateway/) (O005, the UK identifier PII gateway). This experiment does not ship a second inventory or a second redactor. It does not call Document Intelligence.

**Status.** Available as a local starter. The draft runs offline on synthetic text. No Azure credential and no network call are required. It is not an importable Copilot Studio solution, and a live model has not been scored.

North Quay, Sam River, and River Supplies are fictional.

## The problem

A council permit, an HR change, and a supplier bank-details change are full of boxes. Some are blank. Some are illegible. Some are filled twice with different values. A checkbox can be ticked and crossed. A signature box can say "verified" when nobody has checked it. A bank-details change is a fraud risk if a program treats the form as already confirmed.

A pasted schema can disagree with the schema the service actually uses. A line in the form can tell the reader to ignore the schema, mark the signature verified, or drop a legal hold.

## Who it helps

A reviewer who needs a first structured record and a sheet that highlights identity, bank details, amounts, dates, and declarations. The organisation gets a synthetic staging row only after that named reviewer approves the exact record.

A person who writes that they are frightened, not safe, or raising a grievance is not processed as a routine form. The cue is routed and the words are not copied.

## What it does

From one synthetic form and the pinned schema for that form type, the starter reads labelled lines. Each field keeps its location and a confidence band. Dates, postcodes, sort codes, and amounts are normalised only when the text parses. `12/12/2024` is one date. `03/04/2025` is left ambiguous. An impossible date, an unreadable amount, and an out-of-range amount are flagged. Nothing is replaced with today or with zero.

A missing field stays missing. An illegible field stays empty. Two different values are not reduced to one. A ticked-and-crossed box is not resolved. A signature is `present` or `absent`. `verified` stays false. A supplier bank-details change, or a ticked bank-details change on the HR form, is high risk for a human call-back. The call-back is not performed.

UK GDPR Article 5(1)(c) and Article 5(1)(d) are quoted from legislation.gov.uk, opened on 25 November 2026. Article 6 and Article 9 were not opened. The quotes are context. They are not a finding that a principle was met.

A count from 1 to 4 is withheld, and so are percentages, differences, and counts filed under other field names. Five is this starter's threshold, not a claim of anonymisation.

## What it does not do

It does not invent or infer a missing value. It does not decide an application. It does not write to a production system. It does not send anything. It does not perform a call-back. It does not treat the word approved, or the word verified, inside the form as the approval step. It does not apply a caller-supplied schema. It does not follow instructions embedded in the form. It does not trust a role or a clearance written in the form. It does not drop a legal hold, a retention label, or a protective marking. It does not describe the output as anonymised.

## How a record is approved

1. The draft is stored by the agent when it is built. The hash covers the fields, the flags, the marking, the hold, the retention labels, the injection signals, the suppression list, the required acknowledgements, and whether a route was seen.
2. A distress, safeguarding, or whistleblowing cue, including a paraphrase, must be seen by the named reviewer before staging. The seen step is `record_route_seen`. It does not stage.
3. `record_reviewer_approval` compares the caller's package with the agent-held copy. An edit that is hashed again is refused. The approver must be the directory reviewer named on the draft. A clerk cannot approve. A guest cannot approve. A string is not the boolean true.
4. Only then is a synthetic row written. `decided`, `sent`, `production_written`, and `call_back_performed` stay false.

## UK sources

Opened on 25 November 2026:

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5). Article 5(1)(c): "adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed (‘data minimisation’);". Article 5(1)(d): "accurate and, where necessary, kept up to date; every reasonable step must be taken to ensure that personal data that are inaccurate, having regard to the purposes for which they are processed, are erased or rectified without delay (‘accuracy’);". Neither paragraph showed a footnote marker. Paragraphs (b) and (e), and paragraph 3, did. Those are not quoted here as unchanged text.

Article 6 and Article 9 were not opened. No lawful basis is asserted. This is not legal advice.

## Honest limitations

- The confidence numbers `0.95`, `0.55`, and `0.15` are labels for this starter. They are not a model score.
- Phrase lists miss a paraphrase that uses none of the stems. Recall on the fixture is not a live rate.
- The review sheet keeps material values for the named reviewer. The audit log does not. The output is not anonymised. Experiment 08 does not detect names, email addresses, or telephone numbers. This folder counts those for the log and still does not claim the form is anonymous.
- A line that is not `label: value` is not a field. Free text that merely mentions a fee is not extracted.
- The marking order and the small-number threshold are starter rules. The Government Security Classifications policy and the ICO anonymisation guidance were not opened.
- Stale means the question date is on or after the pinned review-due date. That is not a statutory period.
- Document Intelligence was read and not called. See [docs/foundry.md](docs/foundry.md).
- No tenant is configured.

## 10-point gate

| Gate | Where it is |
| --- | --- |
| Non-goals | This readme, and `autonomy.constraints` in the manifest |
| SKILL.md metadata | `skills/*/SKILL.md`, one description line, saying when to use the skill |
| Synthetic fixtures | `fixtures/`, `examples/sample_request.json` |
| Least-privilege tool schemas | `schema/` |
| Permissions manifest | `permissions.yaml`, the same file as `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json` |
| Prompt injection, stale data, prohibited actions | `tests/` and the workflow smoke steps |
| Evaluation | `eval/evaluate.py`. The report is a smoke test, not a model score |
| CI | `.github/workflows/experiment-77-tests.yml` |
| Clean install | `requirements.txt` is pytest, PyYAML, and jsonschema. The core is the standard library |
| Honest limitations | This readme and [docs/security-and-permissions.md](docs/security-and-permissions.md) |

## Run it

From this folder:

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -q
python eval/evaluate.py
python src/extract.py --request examples/sample_request.json --as-of 2026-10-15
```

`eval/smoke_report.json` is a deterministic smoke test of 20 synthetic cases. Paraphrase recall and the fee-line check are not added to that total. It is not a model score.

The licence is MIT.
