---
name: approve-rubric
description: Record the directory recruiter's decision on one rubric hash. Use when that recruiter has accepted or rejected the scoring rubric for this pack hash. Do not score a candidate.
---

# Approve the rubric

Call `record_rubric_approval()` with item `rubric`, the pack hash, and the rubric hash. The approver must be a directory recruiter. An unreadable scale is refused. A missing anchor is not filled in. This file does not assign a weight.

The rubric does not score a person. `scored` stays false. Accepting the rubric does not by itself approve the pack.

Do not contact a candidate. Do not schedule an interview. Do not score or rank anyone.
