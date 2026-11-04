# Microsoft Foundry

Catalogue stack for UK09 is Microsoft Foundry, Azure, and Copilot Studio. This folder does not create a Foundry resource, does not call a model, and does not call a search index. `foundry_called` stays false.

The Microsoft Foundry product page was not opened for this experiment. Document Intelligence, Azure AI Search, and the groundedness evaluator are unverified deployment options. They are not called. No UK region was confirmed. UK region availability is unverified. Billing pages were not opened. No price is copied.

## What a later deployment might use

A team that already hosts a non-production project in Microsoft Foundry could, outside this starter, consider three separate pieces. This note does not describe their current behaviour, because those pages were not opened on 4 November 2026.

- **Document Intelligence.** A service that reads a file into text. This starter does not read a PDF, an image, or a scan. The caller pastes text that is already split into pages, paragraphs, and lines. Whether Document Intelligence can preserve a page, a paragraph, and a line in the way this checker requires is unverified.
- **Azure AI Search.** An index over documents. This starter looks up a document id inside the JSON bundle. It does not query a search service. Whether a search hit can stand in for a pinpoint citation is unverified, and this checker would still reject a sentence that is not a contiguous copy of the cited lines.
- **The groundedness evaluator.** Experiment 29 describes that evaluator from a page it opened. This experiment does not repeat that description as its own reading, and it does not call the evaluator. A 1 to 5 score is not this checker's verdict. `supported` here means the sentence is a contiguous part of the cited lines.

## Where Foundry would sit later

A team could treat this starter as a fixed first reading of a synthetic bundle, then decide whether to send a file to a Foundry deployment. That decision is the decision-maker's, outside this folder. Sending a real case file would also need the lawful basis the data protection officer confirms. This starter does not make that call and does not store a case.

## What this note does not claim

- That Document Intelligence, Azure AI Search, or the groundedness evaluator is configured here.
- That a UK region can host them. That was not verified on 4 November 2026.
- That a Foundry score would match `checker_passed`.
- A price, a credit quantity, or a quota.
- That this starter is the Home Office asylum summariser, the PoliceAI disclosure pilot, or the DBS barring summary tool. It is none of those.
