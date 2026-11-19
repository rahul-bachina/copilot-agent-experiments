---
name: approve-pack
description: Record the directory recruiter's approval of one pack hash for their own use. Use when the questions and the rubric are already accepted and every HR route has been seen. Do not contact candidates.
---

# Approve the pack

Call `record_pack_approval()` with item `pack`, decision `approve`, and the pack hash. The approver must be the directory recruiter. The questions decision and the rubric decision must already be `accept`, and every HR route must have `hr_seen` true. A boolean such as `pins_seen` counts only when it is the boolean true. This file does not assign a weight.

`approved_for_use` means the recruiter may use that text. `contacted`, `scheduled`, `scored`, `ranked`, and `hiring_decision` stay false.

Do not contact a candidate. Do not schedule an interview. Do not score or rank anyone. Do not make a hiring decision.
