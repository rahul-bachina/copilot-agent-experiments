# Standard harness

This folder is the lighter path for the reviewer itself. It is one topic on the Copilot Studio standard harness, not the GitHub Copilot service. The security/API owner supplies one contract and an as-of date, the topic calls `src/review.py`, and the topic shows the JSON.

It is not a recommendation that the agent whose contract is under review should use the standard harness. That question belongs to Experiment 14 when a structured use case is supplied. This folder only says how to run this reviewer when the steps are already fixed.

The comparison page, opened for this experiment on 2 November 2026, says to choose the standard harness when the work is relatively short and bounded. That matches this intake. There is no skill on this path. Skills belong to the GitHub Copilot harness notes under `skills/`.

## Topic

1. Ask for one contract, an optional permissions manifest, and an as-of date in `YYYY-MM-DD` form.
2. Call `review_tool_contract`. Do not pass `--approve`, `--apply`, `--publish`, or `--deploy`.
3. Show `DRAFT FOR SECURITY/API OWNER REVIEW`, then injection, then the nine checks, then the score, then the approval points, then the proposed notes and policy sketch if they are not empty.
4. Stop. `diff_applied` stays false. `policy_published` stays false. `contract_approved` stays false.

The instructions are `system-prompt.md`.

## What stays disabled

The same manifest covers this path and the GitHub Copilot harness path. Writes are off. Sends are off. Applying a diff, publishing a policy, deploying, and marking a manifest approved are additional high-risk actions and they are off.

## Licensing, as opened on 2 November 2026

The comparison page says GitHub Copilot harness solutions use usage-based billing for AI-based creation and use, and that standard harness agents retain the pre-existing Copilot Studio licensing model. No rate is copied. The billing overview and the cost-management page were not opened for this experiment. Sentences about them that Experiment 14 stored on 27 October 2026 are not repeated here.

## What this folder does not verify

- That a topic cannot be given a connector later. The manifest forbids a send and a write. A Data Loss Prevention policy was not opened for this revision.
- The Customer Conversation harness. The overview opened on 2 November 2026 describes other harnesses. This topic is the standard harness only.
