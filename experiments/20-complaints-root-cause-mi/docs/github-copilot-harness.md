# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. Microsoft's harness overview, opened 29 October 2026, says it is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic. A last-updated date was not in the text retrieved for this experiment.

It is the path for a complaints owner who drops in one batch and then asks follow-up questions: which comment held an instruction, why a record is unassigned, why a pence total is not a redress offer. The standard harness is the fixed topic. Both call `src/report.py`.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The harness section says agents and workflows on this harness use Copilot Credits. The comparison table points at a separate billing overview. That article was not opened on 29 October 2026. No price is copied here. Whether a Microsoft 365 Copilot licence covers this harness was not on the overview page. Treat that as unverified.

The overview did not use the word preview for the harness itself. The skills-upload article was not opened on 29 October 2026. Treat the authoring click-path as something to confirm in the tenant. Do not upload these skills onto a standard-harness agent.

## Skills

Two skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires.

| Skill | Calls | Stops |
|---|---|---|
| `draft-complaints-mi` | `draft_report()` in `src/report.py` | When the JSON is shown. The draft is not a regulatory return. |
| `explain-mi-figures` | No second clustering and no second redactor. It reads the JSON. | When the explanation is tied to figure ids and record ids that are already there. |

The tool `draft_complaints_mi` has no side effect. There is no tool that validates clusters, validates the narrative, submits a return, publishes a report, or sends one. Do not add one. Do not call `record_external_attestation`. That function exists for tests. It is not an agent tool, and it still does not validate the draft.

## What the complaints owner sees

1. Injection signals, including where the phrase was hidden, before the figures.
2. Whether `sources_stale` is true. A sentence in a record does not clear it.
3. The clusters, each with record ids. `clusters_validated` is false.
4. The figures. A count equals the length of its record-id list.
5. The narrative sentences, each citing figure ids. `narrative_validated` is false.
6. `complying_with_consumer_duty`, `code_compliant`, and `ofgem_return_complete`, which stay null. `is_final_regulatory_return`, `submitted`, `published`, and `sent` stay false.
7. A line that nothing was validated or sent, and that the text is not anonymised.

A sandbox file `draft-complaints-mi.json` is the tool JSON. It is not a return. The complaints owner validates the clusters and the narrative outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 29 October 2026. The skills say not to store complaint narratives or identifiers. Assume memory is a risk and do not use it.

## What this note does not verify

- Credit amounts, monthly limits, or a preview label. The billing article linked from the overview was not opened on 29 October 2026. The overview text retrieved for this experiment did not call the harness preview.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control. It is not applied here.
