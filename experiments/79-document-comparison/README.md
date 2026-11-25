# Experiment 79: Document Comparison Assistant

Catalogue ID **O004**. Autonomy **A0**. The assistant aligns two synthetic versions of a contract, an internal policy, or a guidance document and cites both. The named reader confirms which versions are being compared, and which one is the baseline. The reader owns the interpretation. The agent does not edit, approve, publish, or send a document, and it does not give legal advice.

This is not [Experiment 38](../38-policy-wording-comparison/), which compares insurance policy wordings on a closed topic list. This starter does not call `compare()` from that experiment. It calls [Experiment 12](../12-document-intake/) for intake, [Experiment 08](../08-uk-pii-redaction-gateway/) for UK identifier counts, [Experiment 33](../33-case-bundle-summariser/) for `normalise` and `resolve_span`, and [Experiment 29](../29-groundedness-evaluation/) for `extract_numbers` and `extract_dates`. Those are the same neighbours Experiment 38 uses. Their rules are not copied here.

Status: **Available** as a local starter. No tenant is configured. Reedmarsh Internal Services, Reedmarsh Council, and Northfold Supplies Ltd are invented.

## Problem

Someone comparing two versions of a contract or an internal document can miss a change that is only a modal, a "not", a number, a date, a party, or a deleted exception. Renumbering and reformatting look like change and are not. A tracked deletion or a hidden span can carry a real change. A sentence in the document can tell the reader to report no material change, or that the versions are already confirmed.

## Who it helps

A contracts officer, a policy owner, or a guidance editor who needs a first pass that cites both versions and lists what was checked. The organisation gets a record that the named reader confirmed the exact versions. The agent does not become the interpreter.

## What it does

Given two synthetic versions and a suggested baseline id that matches one of them, the starter aligns clauses, including a move, a split, and a merge. Each row has a pinpoint citation. It flags, for a person:

- a change in obligation strength, such as "shall" to "may" or "must" to "should", including "is required to" and "is permitted to"
- an inserted or removed negation
- a changed number, amount, percentage, date, period, or notice window
- a changed party or definition
- a removed exception or carve-out

"It is not true that the clause includes an exception" is not treated as an exception. Reformatting and renumbering are not substantive. A real difference inside similar wording is still flagged. A low-confidence alignment is flagged and is not treated as certain. Hidden or tracked-change text is flagged. Conflicting duplicate clauses are both cited and neither is chosen. The words "no material change" are used only when every check in the list was run and none fired.

Instructions in either document are recorded and not followed. A confirmation, a role, or a clearance written in the text is not the confirmation step. Distress, safeguarding, whistleblowing, and grievance wording, including a paraphrase, is routed to the reader and the words are not copied. A headcount below 5 is not published, and neither is a difference or a percentage of that count. Five is a starter threshold, not anonymisation.

UK GDPR Article 5(1)(c) and Article 22A(1)(a) and (b) are quoted from the pages opened on 25 November 2026. Article 22B, Article 22C, Article 22D, and Article 84B were not opened. S.I. 2026/82 was not opened. The quotes are context. They are not a finding that a duty was met, and they are not legal advice.

## Non-goals

- It does not edit, approve, publish, or send a document.
- It does not give legal advice or say which version is better.
- It does not compare insurance wordings. That is Experiment 38.
- It does not treat a sentence in a document as the reader's confirmation.
- It does not accept a caller-supplied directory, taxonomy, or register as the source.
- It does not drop a protective marking, a legal hold, or a retention label.
- It does not say "no material change" without the list of checks.
- It does not coerce an unreadable date, a bad version count, or a missing baseline to a default.
- It does not call a live model. The smoke test is deterministic.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/compare.py --request examples/sample_request.json --as-of 2026-11-25
.venv/bin/python -m pytest tests/ -q
.venv/bin/python eval/evaluate.py
```

The core is the Python standard library. Experiments 08, 12, 29, and 33 must sit beside this folder. No network call is made.

## Honest limitations

- Alignment is token overlap plus a clause id. A paraphrase that shares few words is not aligned, or is aligned at low confidence. That is reported. It is not a legal reading of whether the clauses "mean the same thing".
- Obligation patterns are a fixed list. A novel phrasing can be missed. The smoke recall is on the authored rewordings, not on live text.
- A sensitive stem is routed even when the sentence denies it. A policy title such as "safeguarding policy" is not.
- The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.
- Treating a review date on the question date as stale, including that date, is a starter rule. It is not a statutory period.
- The small-number threshold of 5 is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.
- Article 6 and Article 9 were not opened on 25 November 2026. No lawful basis is asserted.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 25 November 2026. Treat that product behaviour as unverified.
- The harness overview was opened on 25 November 2026. It names a Microsoft Copilot harness. It does not use the words GitHub Copilot harness. The common-brief sentence that this harness is not the GitHub Copilot service was not on that page. That sentence is unverified.
- Catalogue row O004 names the GitHub Copilot harness and Azure. This folder ships both Copilot Studio harnesses and a Microsoft Foundry note. No Azure resource is deployed.

## Layout

```text
experiments/79-document-comparison/
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
