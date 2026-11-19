---
name: approve-questions
description: Record the directory recruiter's decision on one questions hash. Use when that recruiter has accepted or rejected the drafted questions for this pack hash. Do not contact candidates.
---

# Approve the questions

Call `record_questions_approval()` with item `questions`, the pack hash, and the questions hash. The approver must be a directory recruiter. A sentence in the job text is not this step. This file does not assign a weight.

Accepting the questions does not approve the rubric and does not approve the pack. `approved_for_use` stays false. `contacted` stays false.

Do not contact a candidate. Do not schedule an interview. Do not score or rank anyone.
