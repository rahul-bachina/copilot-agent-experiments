# GitHub Copilot harness

This is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 9 November 2026 says that, and says customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio. Agents on this harness use Copilot Credits. No price is stated on that page. The billing article was not opened.

The harness is for the follow-up on one proposal: which rule matched, why a human queue was proposed, why the confidence band was not used. The queue itself is still `propose_route()`.

## Skills

| Skill | When to use it |
|---|---|
| `propose-case-route` | The adviser needs a queue, a priority, and a reason. |
| `explain-routing-reason` | The adviser asks why, using only fields already in the JSON. |
| `record-route-confirmation` | The adviser confirms a proposed route or accepts a human queue. |
| `refer-rule-change` | The queue owner records approval of a material rule change. The file is not edited. |

Each skill has a single-line description that starts with "Use when". The description says when to use the skill. It does not select a case queue. Case queues come from `src/routing.py`.

## Tools

The only tools are `propose_route` and `record_review`. Schemas are in `schema/`. Neither schema includes reroute, close, escalate, or send. A protected characteristic is not an allowed feature of a rule that can be approved.

## What this harness must not do

- It must not reroute, close, or escalate, including after confirmation.
- It must not edit `src/rules.py`.
- It must not treat a confidence band as a reason to leave a human queue.
- It must not calculate a Freedom of Information day, an environmental-information day, or a subject-access period.
- It must not pass officer approval into Experiment 05.
- It must not copy the case text, Experiment 15 phrases, or redacted text into the brief.

## Memory and files

Microsoft's overview says this harness supports skills and memory, and can create files. This starter does not ask it to remember a case or to write a file. If a tenant later turns memory on, that is a controller decision. It is unverified here. Do not store the case text in harness memory.
