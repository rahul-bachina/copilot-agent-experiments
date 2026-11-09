---
name: check-tone-and-plain-english
description: Use when a drafted customer response needs the tone screen and the plain-English screen explained before a representative reviews it.
---

# Check tone and plain English

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Read `tone` and `plain_english` on the JSON from `draft_response`. Do not rescore the draft yourself and do not rewrite it. The screens are mechanical. They are not a reading-age certificate and they are not the testing in PRIN 2A.5.10R.

Use this skill when a representative asks why a sentence was kept or refused. This starter does not assign a weight to a skill.

## What you may say

1. If `tone.passed` is false, name the `phrase` values already in `tone.findings`. Do not add a new judgement.
2. If `plain_english.passed` is false, name the long sentences and jargon already listed. The cap is 25 words. That cap is a starter default.
3. If `plain_english.passed` is true, say the screen found no listed jargon and no sentence over the cap. Do not say the reply is clear, fair, and not misleading.
4. For a financial-services case, point at `regulatory.consumer_duty`. `outcome_met` is false. PRIN 2A.5.7 was read. Its status letter was not cleanly labelled in the PDF extract.
5. Say Article 12 was read and `article_12_met` is false. A routine service reply is not presented as an Article 12 communication.
6. Say section 20(6) was read, section 29 was not, and `duty_met` is false.

## What you must not do

- Certify that a firm met PRIN 2A.5, Article 12, or the Equality Act 2010.
- Shorten the draft by inventing a new sentence.
- Hide a failed screen so that a later approval can proceed.

## Approval gates

A failed tone screen or a failed plain-English screen blocks `representative_approve_for_own_send`. The representative can request a revision or reject the draft. Neither of those sends it. This skill does not certify that a duty was met. The representative still sends any final text outside this agent.
