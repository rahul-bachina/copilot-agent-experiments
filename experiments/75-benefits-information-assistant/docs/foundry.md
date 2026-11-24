# Microsoft Foundry

Microsoft Foundry is an optional note beside the JSON. It is not a third harness and no resource is deployed.

If a team turns a note on, the model may rephrase fields that are already in the JSON returned by `answer_question()`. It must not add an eligibility decision, an amount, a claim, or a send. `award_amount` stays null. A page that was not cited must not appear. A stale page must not be quoted.

Prompt shields in Microsoft Foundry were not opened on 24 November 2026. Treat that product behaviour as unverified. The deterministic checks in `src/assistant.py` remain the control: instructions in the question are not followed, and the resident's approval is a separate object bound to the content hash.

Use a UK region if the organisation requires UK residency. This repository cannot enforce the region.
