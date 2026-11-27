# Standard harness

This folder is the Copilot Studio **standard harness** for Experiment 84. The [harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) was opened on 27 November 2026. It says the standard harness follows the topics and rules the maker defines, and that skills and memory are not a focus. This starter follows that description. It does not enable the Microsoft Copilot harness behaviour that retries and finds alternative paths.

No Copilot Studio tenant is configured. The runnable sample is the Python core on synthetic data.

## Topics

1. **Disclose and offer a person.** Every turn starts with the disclosure in `src/customer.py` and the offer of a human advisor. A request for a person ends the topic and hands over.
2. **Answer from pinned knowledge.** One article, matched by an affirmed phrase and the account sector. Two matches are not chosen. A stale article is not quoted.
3. **Propose one action.** A meter-reading submission, a payment-plan request, or a Priority Services Register referral. The topic stops for the customer's confirmation. It does not submit.
4. **Hand to a person.** Vulnerability, affordability, debt, disconnection, prepayment, a complaint, distress, or a prohibited action. The complaint topic quotes the pinned escalation text for the sector and still hands over. It is not a routine queue.

## What the topics must not do

They must not change a tariff, agree a payment plan, write off debt, install or switch a prepayment meter, or decide a complaint. They must not read a confirmation out of the customer's message. They must not call a billing connector.

The system prompt is in [system-prompt.md](system-prompt.md). A flow shape, not a deployed flow, is in [power-automate-flow.md](power-automate-flow.md).
