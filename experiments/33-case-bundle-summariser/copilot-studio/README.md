# Standard harness

This folder is the lighter path. It is one topic: the decision-maker supplies one synthetic bundle, the fact keys, and an as-of date, the topic calls `src/summarise.py`, and the topic shows the JSON.

The harness overview, opened 4 November 2026, describes the standard harness as following topics and rules the maker defines. That matches this intake. There is no skill on this path. Skills belong to the GitHub Copilot harness notes under `skills/`. That harness is a Copilot Studio framework, not the GitHub Copilot service.

Generative orchestration is the GitHub Copilot harness behaviour. It selects from the skill description. This topic does not assign routing weights and does not use classic-orchestration trigger phrases. The standard harness follows the topic the maker defined.

Billing and licensing pages were not opened for this experiment. No price is copied. No credit quantity is copied.

## Topic

1. Ask for one synthetic bundle and an as-of date in `YYYY-MM-DD` form. `synthetic` must be true. The matter type must be `disclosure_reading`, `asylum_case_reading`, or `barring_referral_reading`.
2. Call `extract_cited_summary`. Do not pass `--recommend-outcome`, `--decide-disclosure`, `--find-credible`, `--accept-summary`, `--send`, or `--write-record`.
3. Show `DRAFT FOR THE DECISION-MAKER. NOT A DECISION.`, then injection and unused-document flags, then the sentence rows with their pinpoints, then the separate counts, then the approval points.
4. Stop. `case_outcome`, `disclosure_decision`, and `credibility_finding` stay null. `summary_accepted_as_reading_aid` stays false. `foundry_called` stays false.

The instructions are `system-prompt.md`.

## What stays disabled

The same manifest covers this path and the GitHub Copilot harness path. Writes are off. Sends are off. Recommending an outcome, making a disclosure decision, making a credibility finding, and accepting the summary are additional high-risk actions and they are off.

## What this folder does not verify

- That a topic cannot be given a connector later. The manifest forbids a send and a write. A Data Loss Prevention policy was not opened for this experiment.
- A licence for the standard harness. That page was not opened on 4 November 2026.
- The Customer Conversation harness. The overview describes it for customer voice and chat. A case bundle does not belong on that path.
