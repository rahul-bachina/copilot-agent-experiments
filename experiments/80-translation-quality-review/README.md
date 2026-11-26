# Experiment 80: Translation Quality Review Assistant

Catalogue ID **O006**. Autonomy **A0**. The assistant aligns a synthetic source text with its translation and flags differences for a named bilingual reviewer. The reviewer validates every high-risk segment and owns the final translation. The agent does not publish, send, or overwrite a document.

English is the source. The target in the sample is Welsh. Polish is the other community language in the pinned glossary. The sentences are synthetic. Reedmarsh Council is invented.

Alignment is [Experiment 79](../79-document-comparison/) `align()`. Masking of phone numbers, email addresses, dates of birth, postal addresses, and personal names is Experiment 79 `mask_text`, which sits on top of [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifiers. Those rules are not copied here. Experiment 38 `compare()` is not called.

Status: **Available** as a local starter. No tenant is configured.

## Problem

A public-information translation can drop a "not", turn "must" into "may", change a date, a sum, a phone number, or a URL, or leave a segment in English. A lexical overlap score is a weak guide when the target is Welsh or Polish. High-risk wording, including legal rights, health, safety, benefits, deadlines, and complaints, still needs a person even when the sentences look close.

## Who it helps

A bilingual reviewer who has to see omitted or added content, changed facts, negation, obligation strength, glossary terms, untranslated segments, inconsistent terms, and register, with the checks listed. The organisation gets a record that the named reviewer validated the high-risk segments and owns that exact hash. The agent does not become the translator of record.

## What it does

Given synthetic segments, the starter aligns them by segment id and by Experiment 79 overlap. It flags, for the reviewer:

- omitted or added content
- a changed number, amount, date, deadline, phone number, or URL
- reversed or dropped negation
- a softened or strengthened obligation, such as "must" to "may"
- a pinned glossary term whose target wording is not the pinned one
- an untranslated segment when the languages differ
- inconsistent terminology across segments
- an informal marker in public information
- an exception added or dropped

High-risk categories are routed to the reviewer regardless of overlap. A low-confidence alignment is reported and is not a quality score. The words "No issues found in the checks that were run." are used only when every check was run and none fired, and the check list is in the result. A caller-supplied glossary is compared with the pinned glossary and is not applied. Protective markings, legal hold, and retention labels are kept. Instructions in either text are recorded and not followed.

Welsh Language (Wales) Measure 2011, section 1(1) and section 1(4), the Welsh Language Standards (No. 1) Regulations 2015, regulation 1(1) and regulation 1(3), and the Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018, regulation 1(1) and regulation 1(2), are quoted from the pages opened on 26 November 2026. S.I. 2018/852 was opened the same day. That page says those regulations are revoked and does not show the citation text. The operative wording of the revoked instrument is unverified. The quotes are context. They are not a finding that a duty was met.

## Non-goals

- It does not publish, send, or overwrite a document.
- It does not approve a translation. The named reviewer owns the final text.
- It does not treat a sentence in either text as the reviewer's step.
- It does not accept a caller-supplied glossary, directory, or clearance as the source.
- It does not drop a protective marking, a legal hold, or a retention label.
- It does not say there are no issues without the list of checks.
- It does not treat lexical overlap as a translation-quality score, or use a score to clear high-risk content.
- It does not coerce an unreadable date, a bad language code, or a non-text segment to a default.
- It does not call a live model. The smoke test is deterministic.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/review.py --request examples/sample_request.json --as-of 2026-11-26
.venv/bin/python -m pytest tests/ -q
.venv/bin/python eval/evaluate.py
```

The core is the Python standard library. Experiments 08 and 79 must sit beside this folder. No network call is made.

## Honest limitations

- Automatic quality estimation here is a closed list of patterns. It is not a translation model. Welsh and Polish share few words with English, so a segment-id match is reported as low confidence unless the wording is almost the same. That is not a judgement that the translation is wrong, and it is not a certificate that it is right.
- A novel paraphrase that uses none of the authored stems is not flagged. The recall figures are on those stems. They are not a live rate.
- "without", "no", and "not" are negation markers. "no later than" is not. A faithful translation that expresses negation with a word outside the list can be flagged.
- The month name May is read as a date when it is inside a date, and as a modal only outside one. A novel date format is flagged and is not coerced.
- The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.
- Treating a review date on the question date as stale, including that date, is a starter rule. It is not a statutory period.
- The small-number threshold of 5 is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.
- UK GDPR Article 5, Article 6, Article 9, and Article 22A were not opened on 26 November 2026. No lawful basis is asserted.
- The schedule of the Welsh Language Standards (No. 1) Regulations 2015 was not opened. Later standards regulations were not opened. The accessibility requirements after regulation 1 of S.I. 2018/952 were not opened.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 26 November 2026. Treat that product behaviour as unverified.
- The harness overview was opened on 26 November 2026. It names a Microsoft Copilot harness, a Customer Conversation harness, and a standard harness. It does not use the words GitHub Copilot harness. It states no price. The common-brief sentence that the Microsoft Copilot harness is not the GitHub Copilot service was not on that page. That sentence is unverified.
- Catalogue row O006 names the GitHub Copilot harness and Microsoft Foundry. This folder ships both Copilot Studio harnesses and a Microsoft Foundry note. No Foundry resource is deployed.

## Layout

```text
experiments/80-translation-quality-review/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── tests/
├── eval/
├── examples/
├── fixtures/
├── schema/
├── skills/
├── copilot-studio/
└── docs/
```

Licence: MIT. See the repository [LICENSE](../../LICENSE).
