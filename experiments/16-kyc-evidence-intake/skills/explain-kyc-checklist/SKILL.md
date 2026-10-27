---
name: explain-kyc-checklist
description: >
  Explain a KYC checklist JSON that review() has already returned. Use when
  the reviewer asks why a row is missing, stale, or only a phrase. Do not
  re-score the customer, confirm the documents, or send the note.
---

# Explain a checklist that is already on screen

Harness: Copilot Studio **GitHub Copilot harness**. That harness is an authoring and orchestration framework. It is not the GitHub Copilot service.

This skill reads the JSON from `review-kyc-file`. It does not call a second model to decide regulation 33, and it does not call Experiment 08 again.

## Tool contract

There is no second tool. If the JSON is not already in the conversation, use `review-kyc-file` instead of guessing.

## What to say

Tie every sentence to a field that is in the JSON.

- A missing row means a closed-list marker was not on a file Experiment 12 read. It does not mean the duty is failed, and it does not mean the customer is approved.
- `evidenced_but_stale` means the marker was on a file older than the freshness window. That window is not regulation 40.
- A regulation 33 status of `phrase_present` means the words were in a file. `edd_applied` is false. Do not call the customer high risk, medium risk, or low risk. `final_risk_rating` is null.
- `country_stated_in_the_file` means the wrapper named a country. The FATF list was not downloaded.
- `customer_facing.text` is the only wording that could later be shown to a customer, and only after the reviewer decides to use it. Do not mix reviewer questions into it. `hints_at_suspicion` must be false.
- `jmlsg_part_i_opened` is false. Do not cite a JMLSG paragraph.

## Approval gates

The same gates as `review-kyc-file`. Explaining the draft does not confirm the documents. The approver for that confirmation is the KYC reviewer. Do not call `record_reviewer_confirmation`. Do not approve the customer, assign a rating, file a report, or send the note.

## Stop

Stop when the explanation is tied to the JSON. Say that nothing has been confirmed, approved, rated, filed, or sent.
