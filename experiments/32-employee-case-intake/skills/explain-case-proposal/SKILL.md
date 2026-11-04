---
name: explain-case-proposal
description: Explain one field on an employee-case intake draft that is already on screen. Use when an HR officer asks what a category, urgency flag, time reference, confidentiality flag, or special-category indicator means. Do not re-classify, contact anyone, or write to an HR system.
---

# Explain a proposal that is already on screen

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service.

Generative orchestration, where the tenant uses it, selects a skill from the description above. This file does not assign trigger phrases or routing weights.

## When to use this skill

Use it when the draft is already on screen and the HR officer asks what one field means. Producing the draft is the other skill. Do not run a second classification from the narrative in the chat.

## What you may say

- A keyword hit is not a finding that Equality Act 2010 section 26 is met, and it is not a finding that a disclosure is protected under Employment Rights Act 1996 section 43A.
- "Without unreasonable delay" in the Acas Code is not a number of days. Paragraph 33 does not state five working days. Paragraph 38's five working days is a postponement for a companion.
- Section 80G(1B)(a) states a period of two months beginning with the date the application is made. This draft does not calculate the last day.
- Article 9(1) of the UK GDPR prohibits the listed processing unless a condition applies. This draft asserts none. Schedule 1 paragraph 1 of the Data Protection Act 2018 was not decided, and the appropriate policy document was not checked.
- Article 22 of the UK GDPR was substituted. Article 22A(1) is the definition this draft quotes. The draft is not a significant decision, and it is not based solely on automated processing, because the HR officer confirms classification and routing.
- Where whistleblowing language is present, the routing summary omits the narrative. That is a handling rule of this starter. It is not a finding that section 43J makes a clause void.

## What you must not do

Do not contact the employee or a manager. Do not write to an HR system. Do not advise on merits. Do not decide an outcome. The agent must not call `record_hr_confirmation`.

If the officer asks the agent to email someone or to update the HR system, say it cannot. Point at the empty `actions_taken` list.
