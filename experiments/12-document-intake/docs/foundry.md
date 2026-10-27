# Microsoft Foundry

A path for a team that wants a short narrative around the intake JSON, and a note of the document services that were read and not called. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The inventory in `src/intake.py` remains the system of record. A model does not set the hash, the class, the checklist, the stale flag, or the empty decisions. Experiment 08 remains the identifier gateway. A model does not replace it.

## Document services that were read and not called

Retrieved 27 October 2026. This starter makes no network call and does not send a file to either service.

[What is Azure Document Intelligence in Foundry Tools?](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0)

- The page applies to v4.0 (2024-11-30), marked GA and current.
- The Read model extracts printed and handwritten text. The Layout model extracts text, tables, and document structure.
- Prebuilt models on that page include a bank statement, an invoice, a receipt, and an identity document (`prebuilt-idDocument`). The identity row describes extracting key information from passports and ID cards, and endorsements, restrictions, and vehicle classifications from US driver's licences. A listed use case is KYC guideline compliance. The row does not say the model checks a UK register. US tax models are also listed.
- This starter does not call any of them. A file that is not `text/plain` stays `not_read`.

[Choose the right Azure AI tool for document processing](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/choosing-right-ai-tool)

- The banner says API version `2026-06-01-preview` is in public preview, without a service-level agreement, and is not recommended for production. That preview status is Microsoft's.
- The note at the end says the article is based on the Content Understanding `2025-11-01` API. A quick-reference heading on the same page names Content Understanding v1.0 GA (`2025-11-01`) and Document Intelligence v4.0 GA (`2024-11-30`).
- The page describes Document Intelligence models for structured templates, and Content Understanding analyzers for unstructured or multimodal content. It also describes building on Foundry models. One comparison table is headed "Build Your Own with Azure OpenAI".
- This starter does not call Content Understanding, and it does not call a Foundry model.

A later OCR step would sit in front of this intake. Until it does, `not_read` is a gap, not a clean result. Wiring either service would be a manifest change in the same change, with the caller's data-processing terms confirmed at the time. Nothing here was measured against either service.

## What a model may do, if a team adds a narrative

- Turn the intake JSON into a short brief, using only fields that are already in the JSON.
- Point at `prompt_injection`, `any_document_not_current`, `catalogue_stale`, and `read_status` in the first paragraph.
- Repeat that `gateway.output_is_anonymised` is false.

## What the model must not do

- Invent a class, a hash, an entity type, or a checklist row.
- Set `files_confirmed`, `purpose_confirmed`, or `reviewer_decision`.
- Describe the text as anonymised, or reconstruct the file body from the entity types.
- Clear a stale, missing, or future date because the file says it is current.
- Call B004, B007, UK11, or UK09, or describe a routing label as a hand-off that has happened.
- Approve or reject KYC, a claim, a disclosure, or an evidence finding.
- Browse the web, or send the file to Document Intelligence, to fill a gap the JSON already marks as unread.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The user supplies the batch and the as-of date.
2. Code, not the model, calls `intake()`. That call includes Experiment 08 for each `text/plain` file inside the size cap. `apply_model_suggestions` stays false. `reversible` is not requested.
3. One chat completion receives the JSON as data and the instructions in `copilot-studio/system-prompt.md` as the system message. Temperature low. The completion is rejected if it confirms the files, sets a purpose, claims anonymisation, or names an action the flags say did not happen.
4. The person sees the JSON and, beside it, the narrative. The narrative is still a draft. The user confirms the files and the purpose. The intake reviewer decides the routing suggestion.

There is no retrieval over a case store or a mailbox. If a team adds retrieval, the corpus is the closed lists in `src/catalogue.py`, not a crawl. A crawled page would bypass `catalogue_pinned_on`.

## Deployment choices to confirm

- Region: UK South or UK West, if a model is used at all.
- The deployment is not trained on the caller's files. Confirm the data-use terms at the time.
- Prompt shields: turn them on if a model sees the batch. They are not a substitute for the missing send tool, and they are not a substitute for the scan in `src/injection.py`. This folder did not re-open the prompt-shields product page on 27 October 2026. Experiment 08 records a retrieval of that page on 26 October 2026. Treat the detailed filter behaviour as unverified here.
- Do not log the file body or the raw identifiers in the trace. Log the batch id, the file hashes, the catalogue pin, and the as-of date.

The smoke test in `eval/smoke_report.json` is the deterministic checker. It is not a Foundry score. A live Foundry run has not been done.
