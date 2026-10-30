# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. The harness overview, opened 30 October 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for a team that drops in one proposal and then asks follow-up questions: which rule fired, why the DPIA flag is null, why the ATRS line is a recommendation. The standard harness is the fixed topic. Both call `src/classify.py`.

The overview says this harness is for reasoning-heavy, multi-step work. It can create and edit Word, Excel, PowerPoint, and PDF files, and it supports skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No rate is copied. The overview does not mark this harness as preview.

The comparison page was not opened on 30 October 2026. The licensing article linked from the overview was not opened. No price and no licence sentence from those pages is stored here.

## Skills

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent. A skills-upload article was not opened on 30 October 2026. Treat the click-path as something to confirm in the tenant.

| Skill | Calls | Stops |
|---|---|---|
| `read-proposal` | No classifier. It lists structured fields and flags instructions in the text. | When the file is described and handed on. |
| `draft-classification` | `classify()` in `src/classify.py` | When the JSON is shown. `approved` is false. |
| `explain-classification` | No second call. It reads the JSON already on screen. | When the explanation is given. It does not approve. |

The tool `classify` has no side effect. There is no tool that approves a use case, provisions an agent, sends an ATRS record, or writes a production system. Do not add one.

## What the team sees

1. Injection and stale flags, before the classification.
2. A suggested autonomy of A0, A1, or A2. Never A3. A request for A3 is flagged out of scope.
3. A risk tier, with the note that it is a queue heuristic.
4. `dpia_likely_needed` and `dpia_required` (the second stays null).
5. `atrs_likely_needed`, with mandatory scope still not decided.
6. A resemblance, or a list of candidates when more than one pattern matches.
7. Approval points, including the governance team approving or changing the classification.

A sandbox file `draft-classification.json` is the tool JSON. It is not a decision record. The governance team's approval is made outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not on the page opened on 30 October 2026. The skills say not to store the proposal. Assume memory is a risk and do not use it for names, narratives, or the classification.

Holding only the GitHub Copilot service does not make this harness available. The overview says the harness is a Copilot Studio framework.

## What this note does not verify

- Credit amounts, monthly limits, or a billing-rates table.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids a send and a write. A data loss prevention policy was not opened.
- The Customer Conversation harness. The overview describes it for customer voice and chat. This experiment does not use it.
