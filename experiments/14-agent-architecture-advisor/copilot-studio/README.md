# Standard harness

This folder is the lighter path for the advisor itself. It is one topic: the architect supplies one use case and an as-of date, the topic calls `src/advise.py`, and the topic shows the JSON.

It is not a recommendation that the proposed use case should use the standard harness. That question is answered by the JSON. This folder only says how to run this advisor when the steps are already fixed.

The harness overview, opened 27 October 2026, describes the standard harness for rule-based agents and structured, repeatable conversations, with topics and paths the maker defines. That matches this intake. There is no skill on this path. Skills belong to the GitHub Copilot harness notes under `skills/`.

## Topic

1. Ask for one use-case file and an as-of date in `YYYY-MM-DD` form.
2. Call `advise`. Do not pass `--approve`.
3. Show `DRAFT FOR ARCHITECT REVIEW`, then injection, then the five options, then the autonomy line, then the approval points, then whether the skeleton validated.
4. Stop. `platform_selected` stays null.

The instructions are `system-prompt.md`.

## What stays disabled

The same manifest covers this path and the GitHub Copilot harness path. Writes are off. Sends are off. Selecting a platform, approving a manifest, and deploying are additional high-risk actions and they are off.

## Licensing, as opened on 27 October 2026

The assign-licences page says it describes the standard harness, and that creating and managing agents needs a user licence and a tenant licence. Users of a published agent do not need a special licence. A trial can be used in the test chat panel and cannot publish. The licensing guide that page points to was not opened.

The standard-harness licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for the GitHub Copilot harness. The cost-management page says GitHub Copilot harness consumption is not included with a Microsoft 365 Copilot licence, and that standard-harness agents are covered by that licence in Microsoft 365 channels and billed outside that case. Both sentences are kept. No quantity is copied. No price is copied.

The usage-based billing overview says the standard harness starts billing after publish. The GitHub Copilot harness starts when you start building, including testing. No diagram from that page is copied.

## What this folder does not verify

- That a topic cannot be given a connector later. The manifest forbids a send and a write. A Data Loss Prevention policy was not opened for this revision.
- The Customer Conversation harness. The overview describes it for customer voice and chat. It is not this topic, and it is not one of the five options the advisor scores.
