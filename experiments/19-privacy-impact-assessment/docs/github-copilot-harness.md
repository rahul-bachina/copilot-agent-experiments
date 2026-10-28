# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. Microsoft's harness overview, opened 28 October 2026, says it is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic. A last-updated date was not in the text retrieved for this experiment.

It is the path for a privacy officer who drops in one brief and then asks follow-up questions: which comment held an instruction, why a combination item is incomplete, why a high residual is not a consultation. The standard harness is the fixed topic. Both call `src/assess.py`.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The harness section says agents and workflows on this harness use Copilot Credits. The comparison table points at a separate billing overview. That article was not opened on 28 October 2026. No price is copied here. Whether a Microsoft 365 Copilot licence covers this harness was not on the overview page. Treat that as unverified.

The overview did not use the word preview for the harness itself. The skills-upload article was not opened on 28 October 2026. Treat the authoring click-path as something to confirm in the tenant.

## Skills

Two skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent.

| Skill | Calls | Stops |
|---|---|---|
| `draft-dpia` | `assess()` in `src/assess.py` | When the JSON is shown. `approved`, `signed_off`, and `residual_risk_accepted` are false. `dpia_required` is null. |
| `explain-screening` | No second screen and no second redactor. It reads the JSON. | When the explanation is tied to fields that are already there. |

The tool `draft_dpia` has no side effect. There is no tool that approves, rejects, or signs off a DPIA, accepts residual risk, or sends a consultation. Do not add one. Do not call `record_external_attestation`. That function exists for tests. It is not an agent tool, and it still does not approve the assessment.

## What the reviewer sees

1. Injection signals, including where the phrase was hidden, before the sections.
2. Whether `sources_stale` is true. A sentence in the brief does not clear it.
3. `screening.screen_result` and `automated_decision_screen.screen_result`. `dpia_required` and `lawful` stay null.
4. The sections, with gaps left as gaps, and which fields were copied from an inventory or a manifest.
5. `prior_consultation`. A high residual is a flag. `article_36_consultation_required` is null. `prior_consultation_sent` is false.
6. A line that nothing was approved, signed off, accepted, or sent, and that the text is not anonymised.

A sandbox file `draft-dpia.json` is the tool JSON. It is not an approval. The privacy officer approves the assessment outside the agent. The project owner accepts residual risk outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 28 October 2026. The skills say not to store the brief text or the identifiers. Assume memory is a risk and do not use it.

## What this note does not verify

- Credit amounts, monthly limits, or a preview label. The billing article linked from the overview was not opened on 28 October 2026. The overview text retrieved for this experiment did not call the harness preview.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control. It is not applied here.
- The Customer Conversation harness. It is for customer voice and chat. This experiment does not use it. The users are a project team and a privacy officer.
