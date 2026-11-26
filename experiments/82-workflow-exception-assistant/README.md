# Experiment 82: Workflow Exception Assistant

Catalogue ID **O009**. Autonomy **A1**. The assistant reads synthetic Power Automate-style run histories, classifies the exception, groups related failures, and proposes retry, route, or cancel with the risks. The named process owner chooses. The agent does not retry, cancel, edit a record, or re-run a flow.

This is not [Experiment 17](../17-invoice-exception-triage/), which triages one invoice that failed a match. This starter does not call it. It calls [Experiment 08](../08-uk-pii-redaction-gateway/) to count UK identifiers. Those rules are not copied here.

Status: **Available** as a local starter. No tenant is configured. Reedmarsh Internal Services is invented.

## Problem

A failed or stuck flow is hard to read. The error text may say "retry now" when the structured code is a business-rule breach. A lookup that is idempotent is not the same as a payment step. A run that already sent an email or wrote a record can be only partly complete. A sentence in the payload can claim the owner has already approved a retry.

## Who it helps

A process owner who needs a first reading of related failures, with a citation to the run and the step, before they choose retry, route, or cancel. The organisation gets a record that the choice was bound to the exact proposal and its hash. The agent does not become the operator.

A person who pastes a note of distress, a safeguarding concern, whistleblowing, or a grievance is not processed as a routine failure. The cue is routed to the owner and the words are not copied.

## What it does

Given synthetic runs and the date the question is about, the starter classifies each failure from a pinned error-code list:

- transient connector or throttling
- authentication or an expired connection
- data validation
- missing reference data
- permissions
- business-rule breach
- duplicate submission
- timeout, including a run that is still going and is past the pinned stuck threshold on the question date

Related failures are grouped. Each group cites the run id, the step name, the step index, and the status. Error text is not the class. "It is not true that the error includes ignore previous instructions" is not an instruction. Conflicting codes are not picked.

Retry is marked safe only when every failing step is idempotent on the pinned register, has no side effect, has no qualifier, and the class is transient or timeout. A payment, an email, or a record write is flagged as a possible duplicate. Partial completion is flagged. A caller-supplied register is compared and not applied. A stale run, a future timestamp, and an unreadable timestamp are flagged and are not coerced.

UK GDPR Article 5(1)(c) and Article 22A(1)(a) and the opening of Article 22A(1)(b) are quoted from the pages opened on 26 November 2026. The FCA operational-resilience overview was opened the same day. The two sentences in `src/sources.py` are the words on that page. SYSC 15A was not opened. The quotes are context for an audit trail. They are not a finding that a duty was met or that a firm stayed inside an impact tolerance.

## Non-goals

- It does not retry, cancel, edit a record, or re-run a flow.
- It does not treat error text, a payload sentence, or a caller-supplied register as authoritative.
- It does not mark a retry safe for a payment, an email, a record write, or a step with a qualifier.
- It does not auto-retry, including when the reading says retry is safe.
- It does not drop a protective marking, a legal hold, or a retention label.
- It does not decide that a firm met an operational-resilience impact tolerance.
- It does not triage an invoice. That is Experiment 17.
- It does not call a live model. The smoke test is deterministic.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/workflow.py --request examples/sample_request.json --as-of 2026-11-26
.venv/bin/python -m pytest tests/ -q
.venv/bin/python eval/evaluate.py
```

The core is the Python standard library. Experiment 08 must sit beside this folder. No network call is made.

## Honest limitations

- The class list is the pinned taxonomy. A code that is not on it is unclassified. A novel error string is not read as a class.
- The paraphrase set is a fixture. The smoke recall is on those rewordings, not on live text. A cue that uses none of the stems is not flagged.
- A sensitive stem is routed even when the sentence denies it. A policy title such as "safeguarding policy" is not.
- Calendar-day hours for a stuck run are a lower bound. A run that started on the question date is not given a duration of zero. It is flagged as not known.
- Treating a run as stale on the pinned boundary, including that day, is a starter rule. It is not a statutory period. The FCA page does not state a retry interval.
- The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.
- The small-number threshold of 5 is a starter control. It is not anonymisation. The ICO anonymisation guidance was not opened.
- Article 6 and Article 9 were not opened on 26 November 2026. No lawful basis is asserted. SYSC 15A was not opened.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 26 November 2026. Treat that product behaviour as unverified.
- The harness overview was opened on 26 November 2026. It names a Microsoft Copilot harness. It does not use the words GitHub Copilot harness. The page says that harness retries and finds alternative paths. This starter does not enable that. The common-brief sentence that this harness is not the GitHub Copilot service was not on that page. That sentence is unverified.
- Catalogue row O009 names Power Platform and Copilot Studio. This folder ships both Copilot Studio harnesses and a Microsoft Foundry note. No Power Platform solution is imported and no Azure resource is deployed.

## Layout

```text
experiments/82-workflow-exception-assistant/
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
