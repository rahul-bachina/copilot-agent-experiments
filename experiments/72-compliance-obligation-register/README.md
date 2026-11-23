# Compliance Obligation Register

Catalogue row L008. Autonomy A1. The named compliance owner approves each change before it is written to a synthetic staging register. This starter does not interpret the law as final advice, assign accountability, or send anything.

Halebridge & Co is fictional. The register rows are synthetic. They are not the FCA Handbook and they are not the Financial Services and Markets Act 2000.

## What the owner does

The owner reads a proposal: the source and the provision, the obligation text quoted verbatim, an applicability candidate, a proposed owner reference from the pinned directory, a review date, linked controls, duplicate flags, and a field-level diff. One change is staged only when that owner approves that change hash.

`proposed_owner_ref` may be `CMP-1001` because the pinned directory has one compliance owner. `owner_chosen` stays false until that person approves the change. The name is not copied.

## Non-goals

- Do not treat SYSC 6.1.1R, or FSMA 2000 sections 59, 59ZA, or 63E, as a decision that the fictional firm is in scope.
- Do not assign accountability.
- Do not mark an obligation covered when the linked control does not address it.
- Do not treat a carve-out, a "should", or a negation as an acceptable must.
- Do not trust a register, directory, or control library supplied in the request.
- Do not follow instructions embedded in an extract or a note.
- Do not send, and do not write the production table `cr72_obligation_register`.
- Do not drop a legal hold, a retention label, or a protective marking.

## What was opened

Opened on 23 November 2026. Quotes in `src/sources.py` are the context pins. They are not the synthetic obligation text. `pins_confirmed` stays false.

| Source | Quote opened on 23 November 2026 | What was not done |
|---|---|---|
| [SYSC 6.1.1R](https://www.handbook.fca.org.uk/handbook/SYSC/6/1.html) | "A firm must establish, implement and maintain adequate policies and procedures sufficient to ensure compliance of the firm including its managers, employees and appointed representatives (or where applicable, tied agents) with its obligations under the regulatory system and for countering the risk that the firm might be used to further financial crime." | The handbook page had no "up to date on or before" line. SYSC 1 Annex 1 was not opened. The sentence states no number of months. |
| [FSMA 2000 s.59(1)](https://www.legislation.gov.uk/ukpga/2000/8/section/59) | "An authorised person (“A”) must take reasonable care to ensure that no person performs a controlled function under an arrangement entered into by A in relation to the carrying on by A of a regulated activity, unless that person is acting in accordance with an approval given by the appropriate regulator under this section." The page said it was up to date with all changes known to be in force on or before 21 November 2026. | The page said changes may be brought into force at a future date. No statutory day count. |
| [FSMA 2000 s.59ZA(2)](https://www.legislation.gov.uk/ukpga/2000/8/section/59ZA) | "A function is a “senior management function”, in relation to the carrying on of a regulated activity by an authorised person, if— (a) the function will require the person performing it to be responsible for managing one or more aspects of the authorised person's affairs, so far as relating to the activity, and (b) those aspects involve, or might involve, a risk of serious consequences— (i) for the authorised person, or (ii) for business or other interests in the United Kingdom." Up to date on or before 19 November 2026. | Subsection (3) was read and is not copied. `applies` stays null. |
| [FSMA 2000 s.63E(1)](https://www.legislation.gov.uk/ukpga/2000/8/section/63E) | "An authorised person (“A”) must take reasonable care to ensure that no employee of A performs a specified function under an arrangement entered into by A in relation to the carrying on by A of a regulated activity, unless the employee has a valid certificate issued by A under section 63F." Up to date on or before 21 November 2026. | Section 63F was not opened. No handbook certificate rule was opened. |
| [FCA SM&CR overview](https://www.fca.org.uk/firms/senior-managers-and-certification-regime) | "The Senior Managers and Certification Regime (SM&CR) aims to reduce harm to consumers and strengthen market integrity by making individuals more accountable for their conduct and competence." The page said last updated 24/04/2026. | SUP 10C, COCON, and statements of responsibilities were not opened. Which firms and functions are in scope is unverified. |

The 12-month figure is the fictional policy's internal minimum. It is not a period stated in the pages above. A review interval longer than 12 months is flagged. It is not marked acceptable.

## What the result does

`propose_register()` reads the pinned extracts, register, controls, and directory. It proposes new, changed, and retired rows. A duplicate includes a reworded must with the same themes. A qualified sentence is not an exact or near duplicate. A provision whose pin says superseded is retired even if the text says it is not superseded. A review date on or before the question date is stale. That is this starter's rule, not a statute. An unreadable date stays unreadable.

A control is linked as cover only when it addresses every affirmed theme with an unqualified must. `CTL-FIRE` does not cover an approval duty. `CTL-SHOULD` does not support a must. `CTL-LEAD` is flagged and not applied.

`stage_approved_change()` writes one in-memory row when the approver is the directory compliance owner and both hashes match. Tampered text or dates are rejected. The string `true` is not an acknowledgement.

## How to run

From this folder, with Python 3.10+ and the packages in `requirements.txt`:

```bash
python3 src/register.py \
  --request examples/sample_request.json \
  --as-of 2026-11-14
```

`python3 eval/evaluate.py` runs the deterministic smoke test of 20 synthetic cases. It is not a model score. The paraphrase block is reported separately and is not added to that total. The committed report is `eval/smoke_report.json`.

## Limitations

Phrase lists miss wording that uses none of the stems. The smoke test is not a model score. Name masking covers the pinned directory names and a few title patterns. It does not claim the note is anonymised.

`pins_confirmed` stays false. Handbook currency beyond the page opened is unverified. Article 6 and Article 9 were not opened. No lawful basis is asserted.

The harness overview opened on 23 November 2026 names a Microsoft Copilot harness and states no price. It does not use the words "GitHub Copilot harness". Older wording that this harness is not the GitHub Copilot service was not on that page. That point is unverified.

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened. Treat that product behaviour as unverified.

This is not legal advice.

## Two harnesses

The standard Copilot Studio harness is the topic flow in `copilot-studio/`. The skills in `skills/` are the Microsoft Copilot harness, in the layout the common brief calls the GitHub Copilot harness. Both call the same Python core. See `docs/harness-comparison.md`.

Microsoft Foundry is an optional short note from the JSON. Quotes, hashes, and the approval step stay in Python. No Foundry resource is deployed. See `docs/foundry.md`.

The Dataverse tables in `docs/dataverse.md` are a design. They are not a deployed environment.

## Neighbours

Date tokens are cross-checked with [Experiment 68](../68-regulatory-change-briefing/). A second calendar date is not chosen. Sentence strength and carve-outs are read with [Experiment 69](../69-policy-control-mapping/) `strength_of` and `qualified`. `assess_sentence` is not called, because that function can set support true on a qualified must. [Experiment 12](../12-document-intake/) intake does not confirm the files. [Experiment 08](../08-uk-pii-redaction-gateway/) counts identifiers and does not describe the output as anonymised.

## Project tree

```
src/register.py          proposal and the staging step
src/dates.py             dates, including ambiguous numeric forms
src/match.py             themes, duplicates, and whether a control addresses a duty
src/negate.py            denial frames and carve-outs
fixtures/                the only register, extracts, controls, and directory
skills/                  Microsoft Copilot harness skills
schema/                  least-privilege tool schemas
eval/                    20 cases and the paraphrase set
agent-manifest.yaml      permissions, copied to permissions.yaml
```

## Licence

MIT. See the repository `LICENSE`.
