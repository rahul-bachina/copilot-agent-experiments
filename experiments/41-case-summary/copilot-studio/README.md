# Standard harness

This is the Copilot Studio standard harness, not the GitHub Copilot service and not the GitHub Copilot harness. One topic. The service representative pastes one synthetic case and an as-of date. A flow runs `src/summarise.py` and returns the JSON. The topic stops.

Microsoft's harness overview, opened on 9 November 2026, describes the standard harness as following the topics and rules the maker defines. This note is a build guide. It is not an importable solution. Licensing for the standard harness is on a separate page. That page was not opened. No price is copied. The overview did not mark the harness as preview.

## Topic

Name the topic by what it does: draft a cited case summary and stop. Do not give it a routing weight. Do not list classic-orchestration trigger phrases. A separate page on generative orchestration was not opened on 9 November 2026. How a tenant selects a topic is unverified.

Instructions to paste are in [system-prompt.md](system-prompt.md).

## What the topic must not do

- Contact the customer. No email, SMS, letter, or telephone connector.
- Update a Dynamics 365 case, or any other case record.
- Close a complaint or offer redress.
- Call `record_accuracy_check`. The representative checks accuracy outside the topic.
- Call Microsoft Foundry. The core does not.

## Human approval

The topic does not contain an approval action that changes the case. The approval point is the representative, reading the JSON, before they do anything in their own system. The diagram in the architecture note shows that point.

## Customer Conversation harness

The same overview describes a Customer Conversation harness for customer voice and chat. It is not built here. This topic is for a service representative, not for the customer.
