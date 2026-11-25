# Microsoft Foundry

A path for a team that wants a short note around the extraction JSON, and a note of Document Intelligence, which was read and not called. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The record in `src/extract.py` remains the system of record. A model does not set the hash, a field value, a confidence, the stale flag, or the approval. Experiment 12 remains the intake. Experiment 08 remains the identifier gateway. A model does not replace either.

## Document Intelligence, read and not called

Opened on 25 November 2026. This starter makes no network call and does not send a form to the service.

[What is Azure Document Intelligence in Foundry Tools?](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0)

The page, for the v4.0 (GA) range, describes Azure Document Intelligence in Foundry Tools as a cloud service for document processing. The Read model extracts printed and handwritten text. The Layout model extracts text, tables, and document structure. Prebuilt models on that view include a bank statement, an invoice, a receipt, and an identity document. The page also says v4.0 (2024-11-30) is GA and current, with no announced end-of-support date. v3.0 is described as retiring on 30 March 2029.

This starter does not call any of those models. The runnable sample reads synthetic text, including OCR-style text, with the deterministic parser. A scanned file that is not already text is out of scope. Wiring Document Intelligence would be a manifest change in the same change, with the caller's data-processing terms confirmed at the time. Nothing here was measured against the service.

The product page uses the name Azure Document Intelligence and the name Foundry Tools. It does not, on the sections read, use the retired product name this repository forbids.

## What a model may do, if a team adds a narrative

- Turn the extraction JSON into a short note, using only fields that are already in the JSON.
- Point at blank, illegible, contradictory, and high-risk bank flags in the first paragraph.
- Repeat that `described_as_anonymised` is false and that `call_back_performed` is false.

## What the model must not do

- Invent a field value, a date, an amount, or a confidence.
- Set `human_approval`, `verified`, `decided`, or `call_back_performed`.
- Describe the text as anonymised, or copy the form body back from the audit counts.
- Choose one of two contradictory values.
- Treat a signature as verified because the form says so.
- Clear a legal hold or a retention label.
- Send the form to Document Intelligence to fill a blank the JSON already marks as missing.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The reviewer supplies the form and the question date.
2. Code, not the model, calls `extract_form()`. That call includes Experiment 12 and Experiment 08. `reversible` is not requested.
3. One chat completion receives the JSON as data. The completion is rejected if it decides the form, verifies a signature, or claims a call-back was done.
4. The reviewer sees the JSON and, beside it, the note. The note is still a draft. The reviewer approves the content hash. Only then is the synthetic row written.

## Deployment choices to confirm

- Region: UK South or UK West, if a model is used at all.
- The deployment is not trained on the caller's forms. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the form. They are not a substitute for the missing send tool. This folder did not open the prompt-shields product page on 25 November 2026. Treat the detailed filter behaviour as unverified.
- Do not log the form body, a bank value, or a raw identifier. Log the extraction id, the form type, the question date, and whether a flag was raised.

The smoke test in `eval/smoke_report.json` is the deterministic checker. It is not a Foundry score. A live Foundry run has not been done.
