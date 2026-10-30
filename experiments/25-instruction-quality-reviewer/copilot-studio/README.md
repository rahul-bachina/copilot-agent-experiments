# Standard harness

This folder is the lighter path for the reviewer itself. It is one topic: the agent owner supplies one instruction file and an as-of date, the topic calls `src/review.py`, and the topic shows the JSON.

It is not a recommendation that the prompt under review should use the standard harness. That question belongs to Experiment 14 when a structured use case is supplied. This folder only says how to run this reviewer when the steps are already fixed.

The harness overview, opened 27 October 2026 by Experiment 14 and not re-opened for this experiment, describes the standard harness for rule-based agents and structured, repeatable conversations, with topics and paths the maker defines. That matches this intake. There is no skill on this path. Skills belong to the GitHub Copilot harness notes under `skills/`.

## Topic

1. Ask for one instruction file, an optional permissions manifest, and an as-of date in `YYYY-MM-DD` form.
2. Call `review_instructions`. Do not pass `--approve` or `--apply`.
3. Show `DRAFT FOR AGENT OWNER REVIEW`, then injection, then the nine checks, then the score, then the approval points, then the proposed diff if it is not empty.
4. Stop. `diff_applied` stays false. `owner_approved` stays false.

The instructions are `system-prompt.md`.

## What stays disabled

The same manifest covers this path and the GitHub Copilot harness path. Writes are off. Sends are off. Applying a diff, deploying, and marking a manifest approved are additional high-risk actions and they are off.

## Licensing, as stored from 27 October 2026

Experiment 25 did not re-open these pages. The sentences are the ones Experiment 14 stored.

The assign-licences page, as stored by Experiment 14, says creating and managing agents needs a user licence and a tenant licence. Users of a published agent do not need a special licence. A trial can be used in the test chat panel and cannot publish. The licensing guide that page points to was not opened by Experiment 14.

The standard-harness licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for the GitHub Copilot harness. The cost-management page says GitHub Copilot harness consumption is not included with a Microsoft 365 Copilot licence, and that standard-harness agents are covered by that licence in Microsoft 365 channels and billed outside that case. Both sentences are kept. No quantity is copied. No price is copied.

The usage-based billing overview says the standard harness starts billing after publish. The GitHub Copilot harness starts when you start building, including testing. No diagram from that page is copied.

## What this folder does not verify

- That a topic cannot be given a connector later. The manifest forbids a send and a write. A Data Loss Prevention policy was not opened for this revision.
- The Customer Conversation harness. The overview describes it for customer voice and chat. It is not this topic.
