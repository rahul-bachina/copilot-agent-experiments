---
name: flag-retention-blockers
description: Flag a legal hold, an open FOI SAR litigation or inquiry, a missing or unreadable trigger, conflicting lines, personal data, or distress for the records owner. Use when the advice outcome is a referral or a blocker is present. Do not dispose of the series and do not copy the cue.
---

# Flag retention blockers

This skill reads the same JSON as `advise_retention()`. It does not calculate a second date and it does not decide.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the result routes to the records owner or the legal owner: a legal hold, an open FOI, SAR, litigation, or inquiry, conflicting or missing lines, an unreadable date, personal data and Article 5(1)(e), a public record selected for permanent preservation, or a distress or safeguarding cue. Do not copy the cue text.

## Do not decide

Do not suggest disposal for a hold or an open matter. Do not lift a hold. Do not drop a retention label. Do not treat a negated sentence as the absence of a hold when the pinned inventory says the hold is there. Do not process distress as a routine retention question.
