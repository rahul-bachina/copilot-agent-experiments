# Harness comparison

Both harnesses call the same Python functions. Neither one sends a disclosure.

| | Standard harness | Microsoft Copilot harness |
|---|---|---|
| Where it lives | `copilot-studio/` | `skills/*/SKILL.md` |
| What it is here | A topic guide. Not an importable solution | Three skills with a one-line description |
| Who approves | The named information governance officer, on a separate object | The same officer and the same object |
| Retry | Not used | The product page says the harness retries. This starter does not enable that |
| Model | None on the runnable path | None on the runnable path |

Microsoft Foundry is optional and is not a third harness. See `docs/foundry.md`.

The comparison above follows the page opened on 27 November 2026 (`https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview`). That page says "Microsoft Copilot harness". It does not say "GitHub Copilot harness". It does not say this harness is not the GitHub Copilot service. That common-brief sentence is unverified. The page says the harness retries and finds alternative paths. This starter does not enable that behaviour. No price was stated on the page, and the standard-harness price page was not opened.
