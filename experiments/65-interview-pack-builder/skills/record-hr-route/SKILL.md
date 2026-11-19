---
name: record-hr-route
description: Record that a directory HR partner has seen one route. Use when the pack routes a health question, an occupational requirement, positive action, or an adjustment cost to HR. Do not decide the legal question.
---

# HR has seen a route

Call `record_hr_seen()` with item `hr-route`, decision `seen`, the route id, and the route hash. The approver must be a directory HR partner. A recruiter cannot close the route. This file does not assign a weight.

`decided` stays false. Section 60(6) and Schedule 9 paragraph 1 are not decided. A distress outcome is not closed by this skill.

Do not contact a candidate. Do not schedule an interview. Do not score or rank anyone.
