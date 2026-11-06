# Microsoft Foundry

Microsoft Foundry is named because the catalogue stack for this kind of agent includes a model host. A Microsoft Foundry agent page was not opened for this experiment. This starter does not call Microsoft Foundry. `foundry_called` stays false. UK region availability for a Foundry deployment was not verified.

## What was opened instead

The Azure Document Intelligence overview in Foundry Tools was opened on 6 November 2026:

https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0

The page title is "Azure Document Intelligence in Foundry Tools". It describes a cloud service. For v4.0, which the page marks GA (API version 2024-11-30), the Read model extracts printed and handwritten text and the Layout model extracts text, tables, and document structure. The page did not name an insurance wording comparison model. A product named as comparison tooling for policy wordings was not found on that overview. The diff in this starter is local Python.

The page points at a product-availability page for region access. That page was not opened. UK region availability is unverified. `document_intelligence_called` stays false. The caller pastes text that is already split into pages, paragraphs, and lines. A later deployment could use the Read or Layout model to produce that split. This folder does not implement that call, and it would still not rank the wordings.

The overview uses the words "Foundry Tools". In the portion read it did not use "Microsoft Foundry" as the product title. Those names are not treated as interchangeable here.

## What a later deployment would still not do

A model call would not be allowed to fill a not stated cell, to choose the meaning most favourable to the consumer, or to draft an endorsement. The deterministic checker would still have to pass, and the wording specialist would still validate every interpretation. Prompt shields are named in the security note. They were not configured here.
