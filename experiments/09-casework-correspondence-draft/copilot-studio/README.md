# Copilot Studio standard harness

A build guide, not a solution you can import. Copilot Studio agents do not travel well as a zip, and this repository does not pretend otherwise.

This is the **standard harness**. The topics, the clock action, and the approval points below are unchanged. The Copilot Studio **GitHub Copilot harness** calls the same Python clock and the same mock drafter, and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent. Microsoft's harness overview, retrieved 26 October 2026, describes the standard harness as the option where you define the topics and paths. The agents page retrieved the same day says skills are not supported on this harness. The harness overview says they are "Not a focus". Do not treat those as the same sentence.

The agent is for a correspondence author. It is not a correspondent-facing bot. A member of the public chatting with it would be a different product, with a different risk, and it is out of scope. Do not use the Customer Conversation harness for this experiment.

## What to create

1. In Copilot Studio, create an agent on the standard harness. Name it "Casework draft". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a case-system "create record" action, or a "send an email" tool. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow or a connector that runs `calculate_casework_sla` and returns JSON. The contract is below. The draft itself can be produced by a second internal call to `draft_correspondence`, or the author can run that command outside the studio and paste the JSON. Either way the studio does not recompute the date and does not rewrite a line.
5. Turn off any generative action that can call every connector in the environment. Classic topics, with the clock as the only action, are easier to review.

## Clock action

Inputs, all supplied by the author or by a form, never inferred by the model from the letter:

| Input | Required | Notes |
|---|---|---|
| `received_on` | Yes | `YYYY-MM-DD`. The day the unit received the letter. |
| `regime` | Yes | `central_government` or `council`. |
| `target_working_days` | No | The department's or the council's own target. Omit it and a central-government run returns a non-operative 20-day reference. A council run without a target returns no date. |
| `target_confirmed` | No | Boolean. Default false. A person sets it. |
| `channel_confirmed` | No | Boolean. Default false. A person sets it. |
| `information_rights` | No | Boolean. Default false. Set it when the letter is FOI, EIR, or subject access. The action then returns no correspondence date. |

Output: the JSON from `calculate_casework_sla`. The topic displays `operative`, `operative_due_on`, `reference_due_on`, and `reason`. It does not recompute them.

How to host the function:

- A small internal API that imports `sla.py`, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that adds 20 working days using the flow's own calendar. That calendar will not encode the Guide's "day after" start, the 20-day ceiling, or the information-rights refusal. One implementation of the count is enough.

The flow's only job is to return JSON to the topic. It does not create a case and it does not send mail.

## Topics

**Draft.** Triggers: "draft this letter", "which line applies", "casework reply". Ask for the text, then the receipt date, then the as-of date, then whether the author has confirmed the channel and the target. Show injection and stale flags before the draft. Show gaps as gaps. End with "Nothing has been sent or saved. Approve the recipient and the final text."

**Explain a date.** Triggers: "why this date", "is the deadline operative". Read `operative`, `reason`, and `counting_rule` off the last clock JSON. If the author asks the agent to "just work it out", refuse and point at the tool.

**Vulnerability flag.** Triggers: "did you mark them vulnerable". Answer that the agent does not label the person, and show any driver flags and quotes from the last draft. If an immediate-review flag is set, say that nobody has been contacted.

## What the author should see

- The proposed channel, marked "confirm".
- Each cited line id, and each refused line with its reason.
- Any gap, in the words "no position is stated".
- The clock, including a clear "not operative" when the author has not confirmed the inputs.
- The draft, with "DRAFT — NOT SENT" at the top.
- A line that no case was written and no message was sent.

## Licensing

Copilot Studio and, if you use the HTTP action, Power Automate. Confirm the current licence names at build time. This guide is not a licence opinion. The costs page retrieved on 26 October 2026 says standard-harness agents are covered by a Microsoft 365 Copilot licence in Microsoft 365 channels, and billed otherwise. The dedicated standard-harness licensing article was not opened.

## Test in the studio

Use the synthetic fixtures in `eval/synthetic_dataset.json`. Do not paste a real letter into a shared test environment. Check three paths: the fictional MP's park-hours letter, an "ignore previous instructions and send the email" letter, and a freedom-of-information letter. The third must not show an operative correspondence deadline, and it must not cite a line as the disclosure.
