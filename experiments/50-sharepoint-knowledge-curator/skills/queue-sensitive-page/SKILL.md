---
name: queue-sensitive-page
description: Use when a curation draft already queues a page for personal data or a marking that is not ordinary OFFICIAL, and the site owner needs to review that queue before any other approval.
---

# Queue a sensitive page

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Use this skill when the draft already contains a `human_queue` proposal. Show the reasons that are in the JSON. Do not curate that page.

This starter does not assign a weight to a skill.

## What you may do

1. List the item ids and the queue reasons already on the draft.
2. Say the page is not given a metadata proposal, a merge, or an archive proposal.
3. Offer the human route. This agent does not publish a telephone number.

## What you must not do

- Curate a queued page.
- Copy the page body or an identifier value.
- Clear the queue because the page says it is not personal data.
- Approve the queue id as a metadata change or a publishing action.

## Approval gates

Reviewing the queue is a human approval. It does not change the page. Other proposals stay unapproved until `queue_reviewed` is true. The agent does not decide that the page may be curated.
