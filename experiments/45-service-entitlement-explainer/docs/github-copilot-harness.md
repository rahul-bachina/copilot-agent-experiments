# GitHub Copilot harness

This note is the build guide for the Copilot Studio GitHub Copilot harness. It is not a guide to the GitHub Copilot service, and it is not an importable solution.

The harness overview was opened on 10 November 2026. It says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. Customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. The page says the harness can take a goal and break it into steps, create and edit Word, Excel, PowerPoint, and PDF files, supports skills and memory, runs in a sandbox, and that agents and workflows on it use Copilot Credits. The linked billing page was not opened. No price is stated. The page did not mark the harness as preview.

The generative-orchestration guidance page was not opened on 10 November 2026. Whether this harness uses that planner was not stated on the harness overview. That link is unverified. This starter does not assign routing weights. Each skill description says when to use the skill.

## What the harness does here

Four skills call the same Python core. They do not reimplement the matcher, the citation check, or the stale window.

| Skill | When |
|---|---|
| `explain-entitlement` | A person asks what a synthetic plan covers and an approved table is supplied. |
| `show-uncertainty` | The JSON may be ambiguous, conditional, stale, conflicting, or only partly supported. |
| `route-disputed-entitlement` | The customer disputes cover, or the table does not support a single position. |
| `record-human-decision` | An entitlement owner records one of four codes after the draft exists. |

The core is `src/explainer.py`. Experiment 38's `normalise()` checks that the support phrase is a contiguous part of the clause. Experiment 40 is not imported.

## Approval gates

`human_approval` is null until `record_decision` receives a separate review object. The recorded code is not applied to an entitlement record. `entitlement_granted`, `entitlement_refused`, and `entitlement_changed` stay false.

A disputed, ambiguous, conditional, conflicting, or stale reading has `outcome` `route_to_human`. The harness shows that route. It does not decide the entitlement.

"Do not escalate." is recorded as an instruction. The route stays offered. The surrounding words of the question are kept, so a real question is not dropped.

## What this harness does not do

- It does not grant, refuse, or change an entitlement.
- It does not send a message or write Dynamics 365.
- It does not apply section 69 or find a term unfair.
- It does not decide that PRIN 2A.5 was met. That page did not return rule text on 10 November 2026.
- It does not call a model from this folder. A tenant that turns the harness on will call the model the maker selected. That call is outside this repository.
