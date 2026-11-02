# Standard harness

This folder is the lighter path. It is one topic: the security reviewer supplies one sandbox bundle and an as-of date, the topic calls `src/run.py`, and the topic shows the JSON.

The harness overview, opened 2 November 2026, describes the standard harness as following topics and rules the maker defines. That matches this intake. There is no skill on this path. Skills belong to the GitHub Copilot harness notes under `skills/`. That harness is a Copilot Studio framework, not the GitHub Copilot service.

Billing and licensing pages were not opened for this experiment. No price is copied. No credit quantity is copied. Experiment 25's stored licence sentences are not repeated here.

## Topic

1. Ask for one sandbox bundle and an as-of date in `YYYY-MM-DD` form. `sandbox` must be true. `production` must be false.
2. Call `run_sandbox`. Do not pass `--assess`, `--remediate`, or `--publish`.
3. Show `DRAFT FOR SECURITY REVIEWER`, then injection and stale flags, then the case rows, then the OWASP coverage, then the approval points.
4. Stop. `reviewer_assessed` stays false. `remediation_applied` stays false. `published` stays false.

The instructions are `system-prompt.md`.

## What stays disabled

The same manifest covers this path and the GitHub Copilot harness path. Writes are off. Sends are off. Assessing findings, applying remediation, publishing, and targeting production are additional high-risk actions and they are off.

## What this folder does not verify

- That a topic cannot be given a connector later. The manifest forbids a send and a write. A Data Loss Prevention policy was not opened for this experiment.
- A licence for the standard harness. That page was not opened on 2 November 2026.
- The Customer Conversation harness. The overview describes it for customer voice and chat. It is not this topic.
