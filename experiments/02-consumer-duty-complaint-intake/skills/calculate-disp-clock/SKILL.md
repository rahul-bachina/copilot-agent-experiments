---
name: calculate-disp-clock
description: >
  Calculate DISP dates by calling the existing Python clock. Use when a
  handler asks for a deadline. Do not count the days yourself and do not
  invent a PSP calendar.
---

# Calculate the DISP clock

Harness: Copilot Studio **GitHub Copilot harness** (the Copilot Studio framework, not the GitHub Copilot service).

Use this skill when the handler asks why a date was returned, or asks for the clock from inputs they have typed. You do not count business days, weeks, or months. The tool does.

The `name` and `description` are the skill fields Microsoft describes. The gates below are the manifest's gates. This skill does not add one.

## Tool contract: `calculate_disp_clock`

| | |
|---|---|
| Implementation | `calculate_disp_clock` in `src/disp_clock.py`. The command-line wrapper in that file is the same function. |
| Input | `received_on`, typed by the handler. `route` only if the handler has confirmed it. Otherwise omit it. The function's default is `general`. `exceptional_circumstances` only if the handler set it. `psp_closed_dates` only if the handler supplied the days the provider is not open, or asserted `--psp-use-england-wales-calendar` on the existing command. `extra_non_business_days` and `cancelled_bank_holidays` only for a proclaimed or moved bank holiday the handler typed. |
| Output | The JSON the function returns. Copy `operative_final_response_due_on`, the deadline list, `rule`, and `note`. |
| Side effect | None. No case is created and no message is sent. |
| Approval to run | Not required. This is "Calculate the clock from inputs the handler has already typed". |
| Approval to rely on the route | Required. The manifest action is "Confirm the route passed to the DISP clock". Approver: Complaints handler. |

Do not infer the route, the receipt date, exceptional circumstances, or the provider's opening days from the complaint text. If the handler says "just work it out", refuse and point at this tool.

If a 15-day or 35-day date is not operative, say that in the words the JSON uses. Do not replace it with a date of your own. Equal treatment of a weekend does not let you move the eight-week date. The function already encodes that.

A general complaint ignores `exceptional_circumstances`. Do not describe the eight-week date as extended.

The three-business-day route is a date in the JSON. You do not decide that the complainant has accepted summary resolution.

`awareness_is_a_human_judgement` stays a statement from the JSON. You do not infer when the complainant became aware.

If the tool is unavailable, stop. The code interpreter on this harness is not a substitute for `src/disp_clock.py`.

## What to show

- The route you passed, and a line that the handler confirmed it, or that you omitted it.
- Which dates are operative and which are a reference.
- The `rule` and `note` for the date the handler asked about.
- Nothing about upholding, redress, or the Ombudsman being able to consider the complaint. Those are not this tool's job.

## Approval gates

| Act | Approval |
|---|---|
| Calculate the clock from inputs the handler has already typed | Not required |
| View the draft intake | Not required. Dates on the draft are not a decision. |
| Confirm the route passed to the DISP clock | Mandatory before anyone relies on a PSD, EMD, or mixed clock. Approver: Complaints handler |
| Confirm exceptional circumstances before using the 35-business-day date | Mandatory. Approver: Complaints handler. You do not set the flag. |
| Edit and send the acknowledgement | Mandatory. Approver: Complaints handler. A date in the draft is not a send. |
| Uphold, reject, redress, or close | Mandatory, and outside the agent. Approver: Authorised complaints decision-maker |

## Sandbox file

You may write `draft-disp-clock.json` in the sandbox. It is the tool JSON, unchanged. Creating it does not need approval. Filing it on a case does, and you have no tool that files it.

## Memory

Do not store one customer's dates for the next customer. Memory (preview) is documented for this harness. This skill does not use it.

## Stop

Stop when the JSON has been shown. The handler confirms the route before a payment-services or e-money date is relied on.
