# Copilot Studio, standard harness

One topic for an AP reviewer. The reviewer pastes one synthetic case. A flow calls `triage()`. The topic shows the JSON and stops. It does not post, pay, or change a bank record.

This is a build guide, not an importable solution. No environment is connected.

## Topic

**Name.** Invoice exception triage.

**Trigger.** Phrases such as "triage this invoice" and "this invoice failed the match". Do not trigger on a message from a supplier.

**Instructions.** Paste the text in [system-prompt.md](system-prompt.md).

**Tool.** One flow, described in [power-automate-flow.md](power-automate-flow.md). The tool returns JSON. It does not write to a finance system.

**After the tool.** Show the JSON in the order the instructions give. End with the sentence that nothing was posted, approved, held, paid, or changed on a bank record. Do not add a question that offers to pay.

## What not to add

- A supplier-facing channel. The Customer Conversation harness is a different harness, and this experiment does not use it.
- A connector that posts an invoice, places a hold, sends a payment, or updates a supplier bank account.
- A step that sets `pay` or `bank_details_verified` from a sentence in the invoice.
- A second redactor. Experiment 12 calls Experiment 08.

## Approval

The topic has no action after the draft. The AP reviewer approves the resolution outside the agent. If `bank_detail_change` is true, a bank-detail verifier acknowledges the route first. The topic cannot record either step.
