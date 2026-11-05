# Architecture

Experiment 35, catalogue ID B007, autonomy A1. The claims handler approves the class. The agent does not accept, decline, settle, tell the customer, or write to a claims system.

Experiment 12 inventories the pack and calls Experiment 08. Experiment 29 scores the quoted lines. Those three are called. They are not re-implemented. Experiment 12 does not call this experiment back.

```
Handler pack and as-of date
        |
        v
triage()  -- calls -->  Experiment 12 intake()  -- calls -->  Experiment 08 propose()
        |
        +--> quoted lines and one policy pointer
        +--> prompts (not findings)
        +--> proposed class (not approved)
        +--> Experiment 29 score_claim on the quotes
        |
        v
DRAFT FOR THE CLAIMS HANDLER
        |
        v
Handler checks prompts, reviews a missed threshold, and approves or changes the class
        |
        v
Outside this agent: accept, decline, settle, tell the customer, write the claims system
```

`record_handler_classification` checks the role "Claims handler", the file ids, the as-of date, and the confirmations. The skills say the agent must not call it. After it runs, the outcome flags are still false, and `write_claims_system` still raises.

A score under a draft threshold sets `human_escalation_required`. The three criteria are not added together. The flag does not decline the claim. Thresholds are not approved. No model is called.

The rendered diagram is `docs/architecture_diagram.png`. Regenerate it with `docs/generate_diagram.py` if the boxes change. Matplotlib is used only by that script.
