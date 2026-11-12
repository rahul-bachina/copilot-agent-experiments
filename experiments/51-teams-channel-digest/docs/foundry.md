# Microsoft Foundry

The digest does not need a model. Decisions, questions, owners, and citations come from `src/digest.py`. Experiment 29's `score_claim` runs in process. It does not call Microsoft Foundry. `foundry_called` stays false.

A tenant may later ask a model to write a short note from the JSON. That note may use only fields already in the JSON. It may not add a decision, an owner, or a message that the core did not return. It may not describe the output as anonymised. Experiment 08 sets `output_is_anonymised` to false, and this starter keeps that.

No Foundry resource is deployed. The Assistants API sunset and the Foundry IQ preview status were not re-opened for this experiment. Experiment 14 and the catalogue note those points. Treat a deployment choice that depends on them as unverified here.

Work IQ is named on catalogue row M002. The Work IQ Learn page was not opened on 12 November 2026. This starter does not call Work IQ. Treat its behaviour as unverified here.

If a model is added later:

- Run it in UK South or UK West. This repository cannot enforce that.
- Do not send the raw export. Send the JSON the core already returned.
- Do not give the model a tool that can post, reply, react, mention, or forward.
- Keep `human_approval` null. A model sentence is not confirmation of the scope.

Prompt shields were not opened on 12 November 2026. The name is unverified here. The control this folder actually has is that message text is data, instructions are not followed, and there is no send tool.
