---
name: answer-how-do-i
description: Answer one how-do-I question from the approved onboarding sources, with the section and the effective date. Use when a new starter asks how a step works and the checklist is already on screen. Do not decide a check or send the answer.
---

# Answer a how-do-I question

This skill calls the same `draft_guide()` function. It does not keep a second copy of the pins.

The `name` and `description` above are the skill fields. This file does not assign trigger phrases or routing weights.

## When to use this skill

Use it when the person asks how a step works: a laptop proposal, the written statement, the privacy notice, or the handbook leave section. Drafting the whole checklist is the other skill.

## Tool contract

Same inputs and the same empty side effects as `draft_starter_guide`. The user's words are not forwarded to Experiment 21, Experiment 57, or Experiment 58. Those calls use a fixed synthetic question.

If `outcome` is `routed_to_human`, give the named route and stop. Do not collect a passport, a share code, a health detail, or a pregnancy detail. Do not decide that a step is a reasonable adjustment. Do not decide that section 1 or section 15 was met.

If a pin lists `unverified`, read that line out. Do not fill it from general knowledge. Sections 2(2) to 2(4) of the Employment Rights Act 1996 were not opened. The Home Office PDF was not opened. Schedule 8 was not opened. An ICO page was not opened.

A quantity that cannot be read, or that is outside 1 to 5, is not replaced with zero. Say that a person has to look at it.

The agent must not call `approve_checklist`. It does not decide the manager's approval, and it does not send the answer.
