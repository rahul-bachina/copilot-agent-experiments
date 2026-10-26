# Microsoft Foundry

This experiment does not deploy a model. The counts CI checks come from the codebook in `src/pipeline.py`.

ThemeFinder, if a body installs it, needs a language-model client. Its README, read on 24 October 2026, shows `langchain_openai.AzureChatOpenAI` and these environment variables for an Azure OpenAI endpoint:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `OPENAI_API_VERSION`

Those are ThemeFinder's names. This note does not rename them. Whether that endpoint is a deployment inside Microsoft Foundry, in UK South or UK West, is a choice for the body. **Unverified here:** that ThemeFinder 0.8.x accepts a Foundry project endpoint without the variables its README lists. This repository has not made the call.

If that client is added later:

- Put the key in Key Vault, or use a managed identity if the client supports one. Do not commit a key. This folder has none.
- Send the redacted text the adapter already passes. Do not point the client at the raw export.
- Keep the fixed system prompt. Do not append a response to it.
- Treat the result as a mapping onto the approved framework. It does not approve the framework and it does not finish the sample.
- The README's incubation warning still applies. Do not describe the output as an expert coding.
- Do not call the consultation-setup path. It uploads to an i.AI bucket.

Microsoft documents prompt shields as a control on generative deployments. Confirm the current control name in the Foundry resource you use. Nothing in this starter enables one, because nothing here calls a model. **Unverified here:** the portal label on 24 October 2026. That product page was not opened for this revision. The injection tests in `tests/test_safeguards.py` and `tests/test_pipeline.py` are the control on the codebook.

A Foundry deployment would be metered on its own. Copilot Credits for the GitHub Copilot harness are a separate bill. See [harness-comparison.md](harness-comparison.md). No price is stated here.
