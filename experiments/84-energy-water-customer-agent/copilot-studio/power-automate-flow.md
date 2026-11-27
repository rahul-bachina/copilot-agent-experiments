# Flow shape

This is a description of a Power Automate-style flow. It is not imported. No connector is configured. Dynamics 365 Contact Centre was not opened on 27 November 2026, and no Dynamics environment is configured.

1. Receive one synthetic conversation id, one account reference, the message, and the date the question is about.
2. Call `answer()` in `src/customer.py`. Do not call a billing system.
3. If `outcome` is `human_handover`, show the pinned text and the handover record. Stop. Do not write a case.
4. If `outcome` is `propose_action`, show `proposed_action.exact_text` and wait for a separate confirmation object.
5. Call `confirm_action()` only with that object. If it returns `confirmation_recorded` true, show that the proposal was recorded and that nothing was submitted. If it returns a rejection, show the rejection and do not retry with a rewritten hash.
6. There is no branch that changes a tariff, agrees a plan, writes off debt, installs a meter, or sends a message.

A confirmation sentence inside the message is not step 5.
