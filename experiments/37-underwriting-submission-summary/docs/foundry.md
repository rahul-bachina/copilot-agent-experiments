# Microsoft Foundry

The catalogue row for B006 names the Copilot Studio GitHub Copilot harness and Microsoft Foundry. Foundry is named here because that is the catalogue stack, and because a later host might show this JSON beside other evaluations. This folder does not call Foundry and does not recommend a move to Foundry.

A Foundry product page was not opened for this experiment. The following are unverified. Do not treat an unverified row as a capability of this starter.

| Idea | Status |
|---|---|
| A model that writes a fluent submission brief | Not built. A fluent brief can add words that are not in the submission. This starter copies lines. |
| Document Intelligence for a PDF or a scan | Not called. Unverified. This starter reads text the caller already split into lines. |
| A groundedness evaluator hosted in Foundry | Not called. Unverified. The number and date check is Experiment 29, in process, and support is a contiguous span. |
| UK region for a Foundry resource | Unverified. This starter does not choose a region and does not call a model. |

`foundry_called` stays false. `release_evaluation` always raises, including for a score that a later host might produce. A pass is not a coverage decision.

Prompt shields, if a later host adds a model, were not verified. See `docs/security-and-permissions.md`.
