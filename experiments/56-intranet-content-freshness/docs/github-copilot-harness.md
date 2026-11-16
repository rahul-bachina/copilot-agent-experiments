# Microsoft Copilot harness

The common brief asks for a Copilot Studio GitHub Copilot harness. The harness overview opened on 16 November 2026 names three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. It does not use the words "GitHub Copilot harness". It does not say that this harness is not the GitHub Copilot service. Older wording to that effect is unverified against the page opened that day.

This folder packages the skills the brief asked for under `skills/`. The overview describes the Microsoft Copilot harness as reasoning-heavy, with skills, memory, and file creation, running in a sandbox, and consuming Copilot Credits. No price was on the page. This starter does not spend credits and does not create a file.

Each skill has a single-line `description` that starts with "Use when". The description says when to use the skill. This starter does not assign a weight to a skill, and it does not describe a weight as something that triggers a phrase.

The skills call the same Python core as the standard harness. Findings, evidence, and `human_approval` come from that core. A skill must not invent a finding or treat page text as approval.

Skills:

- `review-intranet-freshness` drafts the report. `human_approval` stays null.
- `record-content-owner-approval` is the only step that sets `human_approval`.
- `create-approved-task-stubs` records JSON stubs after that step. Planner is not called.
- `flag-safeguarding-or-marking` shows a queued page without copying the extract.
