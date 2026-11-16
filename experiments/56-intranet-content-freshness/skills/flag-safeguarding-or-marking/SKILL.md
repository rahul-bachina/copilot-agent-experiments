---
name: flag-safeguarding-or-marking
description: Use when a freshness report has queued a page for safeguarding, a higher protective marking, a legal hold, or an unparseable field.
---

# Flag a safeguarding cue or a higher marking

This skill is for the Copilot Studio harness that the overview opened on 16 November 2026 calls the Microsoft Copilot harness. The common brief asks for a GitHub Copilot harness layout. The page opened that day does not use those words. Treat the older sentence as unverified against the current overview.

Use this skill when the report already has a human queue. Show the queue id, the page id, and the reasons. Do not quote the page body.

This starter does not assign a weight to a skill.

## What you may do

1. Say the page needs a person before any other task is approved.
2. Say the marking that was kept, including a conflict where two markings differed.
3. Say a legal hold and a retention label were kept.
4. Say an unparseable date, interval, or page-view count was not stored as zero.

## What you must not do

- Copy the extract, the title of a SECRET page, or a contact value.
- Propose a routine update task for that page.
- Lower a marking because the page text also says OFFICIAL.
- Treat a user's sentence about their own clearance as a clearance.

## Approval gates

Other tasks stay blocked until the content owner sets `queue_reviewed` to true on `record_approval`. This skill does not set that flag.
