# Copilot Studio standard harness

A build guide. Not an importable solution. No solution file is in this folder.

The overview opened on 9 November 2026 says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are not a focus. Use one topic.

## Topic

1. The adviser pastes one case as JSON and types the as-of date.
2. A flow calls `propose_route` (see [power-automate-flow.md](power-automate-flow.md)). The flow returns the JSON. It does not write to a case system.
3. The topic shows the queue, the priority, the reasons, and the confidence band.
4. If the outcome is a human queue, the topic says a person takes it and stops. It does not offer a routine queue instead.
5. The adviser confirms in a separate question, which calls `record_review`. The topic then says the confirmation was recorded and the case was not moved.
6. A queue-owner rule approval is a second topic, or the same topic with a different question, and it calls `record_review` with `queue_owner_approve_rule_change`. The topic says the rule file was not edited.

The system message is [system-prompt.md](system-prompt.md). It tells the model not to invent a queue. The queue in the JSON is the one to show.

## What not to add

- A Dataverse or Dynamics 365 update that sets the queue.
- A send step.
- A close or resolve step.
- A branch that skips confirmation when the band is `high`.

The Customer Conversation harness is described on the same overview for contact-centre voice and chat. It is not built here. Detail beyond the overview is unverified.
