# Standard harness

This folder is the lighter path for the intake itself. It is one topic: the team supplies one proposal and an as-of date, the topic calls `src/classify.py`, and the topic shows the JSON.

It is not a recommendation that the proposed agent should use the standard harness. `platform_selected` stays null. This folder only says how to run this intake when the steps are already fixed.

The harness overview, opened 30 October 2026, describes the standard harness for rule-based agents and agent flows, and for structured, repeatable workflows. That matches this intake. There is no skill on this path. Skills belong to the GitHub Copilot harness notes under `skills/`.

The GitHub Copilot harness is a Copilot Studio framework, not the GitHub Copilot service. This topic is the standard harness, so that sentence is here so the two are not confused.

## Topic

1. Ask for one proposal file and an as-of date in `YYYY-MM-DD` form.
2. Call `classify`. Do not pass a key that sets `approved`, `provisioned`, or `governance_decision`.
3. Show `DRAFT FOR THE GOVERNANCE TEAM`, then injection, then the suggested autonomy, then the risk tier, then the DPIA and ATRS indications, then the resemblance, then the approval points.
4. Stop. The governance team approves or changes the classification outside this topic.

The instructions are `system-prompt.md`. A flow shape, with no connector that provisions anything, is `power-automate-flow.md`.

## What stays disabled

The same manifest covers this path and the GitHub Copilot harness path. Writes are off. Sends are off. Approving a use case, provisioning an agent, and marking an ATRS or DPIA record submitted are additional high-risk actions and they are off.

## Licensing, as opened on 30 October 2026

The licensing article linked from the harness overview was not opened. No price is copied. No statement about a Microsoft 365 Copilot licence is copied, because that statement was not on the page opened for this folder.

## What this folder does not verify

- That a topic cannot be given a connector later. The manifest forbids a send and a write. A data loss prevention policy was not opened for this experiment.
- The Customer Conversation harness. The overview describes it for customer voice and chat, using Copilot Credits. It is not this topic.
