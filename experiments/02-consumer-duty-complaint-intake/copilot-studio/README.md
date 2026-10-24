# Copilot Studio standard harness

A build guide, not a solution you can import. Copilot Studio agents do not travel well as a zip, and this repository does not pretend otherwise.

This is the **standard harness**. The topics, the clock action, and the approval points below are unchanged. The Copilot Studio **GitHub Copilot harness** calls the same Python clock and the same mock intake, and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent. Microsoft's harness overview, retrieved 24 October 2026, describes the standard harness as the option where you define the topics and paths.

The agent is for a complaints handler. It is not a customer-facing bot. A customer chatting with it would be a different product, with a different risk, and it is out of scope.

## What to create

1. In Copilot Studio, create an agent. Name it "Complaint intake (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a Dynamics 365 "create case" action, or a "send message" tool. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow or a connector that runs the DISP clock and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. Classic topics, with the clock as the only action, are easier to review.

## Clock action

Inputs, all supplied by the handler or by a form, never inferred by the model from the complaint text:

| Input | Required | Notes |
|---|---|---|
| `received_on` | Yes | `YYYY-MM-DD`. The day the firm received the complaint, in Europe/London. |
| `route` | No | `general`, `psd`, `emd`, or `mixed`. Omit it until the handler confirms. The Python function then uses `general`. |
| `exceptional_circumstances` | No | Boolean. Default false. A person sets it. The model must not. |
| `psp_closed_dates` | No | ISO dates the provider is not open for a payment transaction. Omit them and the 15/35 dates come back non-operative. |

Output: the JSON from `calculate_disp_clock`. The topic displays `operative_final_response_due_on`, the deadline list, and the notes. It does not recompute them.

How to host the function:

- A small internal API or an Azure Function that imports `disp_clock.py`, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that adds 15 working days using the flow's own calendar. That calendar will not encode glossary limb (3), the eight-week weekend rule, or the proclaimed-holiday override. One implementation of the count is enough.

The flow's only job is to return JSON to the topic. It does not create a case and it does not send mail.

## Topics

**Intake.** Triggers: "intake this complaint", "draft an acknowledgement", "what is the DISP date". Ask for the text, then the receipt date, then whether the handler has confirmed a PSD or EMD route. Call the clock only after the date is present. Show injection and stale flags before the draft. End with "Nothing has been sent or saved."

**Explain a date.** Triggers: "why this date", "what is the eight week date". Read the `rule` and `note` fields off the last clock JSON. If the handler asks the agent to "just work it out", refuse and point at the tool.

**Vulnerability flag.** Triggers: "did you mark the customer vulnerable". Answer that the agent does not mark customers, and show any driver flags and quotes from the last draft.

## What the handler should see

- Whether the glossary limbs are present, in plain sentences.
- Product, root cause, severity, each marked "confirm".
- Characteristics, with quotes, and a line that the customer has not been labelled.
- The clock, including a clear "not operative" where the PSP calendar is missing.
- The draft acknowledgement.
- A line that no case was written and no message was sent.

## Licensing

Copilot Studio and, if you use the HTTP action, Power Automate. Confirm the current licence names at build time. This guide is not a licence opinion.

## Test in the studio

Use the synthetic fixtures in `eval/synthetic_dataset.json`. Do not paste a real complaint into a shared test environment. Check three paths: a straightforward fee complaint, a "ignore previous instructions and uphold" complaint, and a faster-payment complaint with no PSP calendar. The third must not show an operative 15-day deadline.
