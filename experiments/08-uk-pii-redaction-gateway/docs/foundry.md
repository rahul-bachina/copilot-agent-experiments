# Microsoft Foundry, and Azure Language, as optional adapters

This is a path for a team that wants a model to suggest spans the deterministic rules do not cover. It is not a deployed project. No Foundry resource is created by this repository. The gateway does not call a model unless the caller passes an adapter.

Use the name Microsoft Foundry. The retired product name is not used here.

The checksums stay in `src/identifiers.py`. A model must not be the NHS modulus 11 check.

## What a model may suggest

The model may:

- point at a name, an email address, a telephone number, or a free-text description the deterministic rules ignore
- return character offsets into the same text

The model may not:

- clear a deterministic finding
- set `output_is_anonymised` to true
- release or send the text
- decide that a checksum passed
- look up an NHS number, a National Insurance number, or a company

`apply_model_suggestions` defaults to false. Applied suggestions are marked `method: model_suggestion` and still need a privacy reviewer. They are not anonymisation.

## Azure Language PII, if a team wants that adapter

Microsoft Learn, [PII entity categories](https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/concepts/entity-categories), retrieved 26 October 2026, is titled as Azure Language in Foundry Tools. On that page:

- United Kingdom National Insurance number, United Kingdom National Health number, and United Kingdom Unique Taxpayer number are categories. The page says to request them with `UKNationalInsuranceNumber`, `UKNationalHealthNumber`, and `UKUniqueTaxpayerNumber`.
- Sort code and bank account number are marked **preview**.
- International Banking Account Number is a category and was not marked preview in the heading that was read.
- Zip code is marked **preview**. The tag cell in the retrieved markdown did not match that heading, so this note does not claim the service detects UK postcodes.
- Companies House numbers were not in the UK section that was read.

This gateway does not call that API. A later adapter would be a deployment choice, with its own data-processing terms, and the manifest would have to name it in the same change. Preview categories stay preview until the page says otherwise. Nothing here was measured against that service, so any comparison of recall would be unverified.

## Prompt Shields

[Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields), retrieved 26 October 2026, says Prompt Shields detect user-prompt attacks and document attacks, and that they are powered by Azure AI Content Safety. In Foundry, user prompt attack detection is enabled by default. Document attack detection is off by default. The page says Prompt Shields do not determine whether content is harmful, factually accurate, or compliant. They are not a redaction engine and they are not the control that stops a release. The missing release tool is that control.

Spotlighting is described on the same family of pages as a preview control for document attacks. It was not enabled here, because there is no deployment.

## Suggested shape, if someone builds the adapter

1. Run `propose()` first, with `model` left as the null adapter.
2. Optional second call, only for suggestions, with the source text as a user message and the system instructions taken from [../copilot-studio/system-prompt.md](../copilot-studio/system-prompt.md). Temperature low. The model returns offsets. It does not return a rewritten "anonymised" document.
3. Pass those offsets in as a `MockModel`-shaped adapter. Leave `apply_model_suggestions` false until a privacy reviewer accepts them.
4. Schema check. `propose()` already forces the anonymisation flag and the release flag to false.
5. Reviewer screen. Nothing is sent.

## Deployment choices to confirm

- Region: UK South or UK West, if a model is used at all.
- The deployment is not used to train on the caller's text. Confirm the current data-use terms at build time.
- Identity: a managed identity, not a key in a notebook. If a key is unavoidable, keep it in Key Vault. This repository does not provision a vault.
- Log the model deployment name on the audit record's `model_assist` field. Do not log the source text or the raw identifiers in Application Insights. The audit record already omits them.
- `eval/evaluate.py` does not call a model. A live run has not been done. Say "not run".
