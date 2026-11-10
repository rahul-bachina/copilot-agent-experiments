# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness: an authoring and orchestration framework inside Copilot Studio. It is not the GitHub Copilot service. The overview opened on 10 November 2026 says customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio, and that the harness shares underlying technology and SDK components with GitHub Copilot.

The overview says agents on this harness use Copilot Credits. It does not state a price. The billing page was not opened.

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. That screen was not opened on 10 November 2026. Do not upload them onto a standard-harness agent.

| Skill | When the description applies |
|---|---|
| `assemble-field-brief` | A technician needs the brief from one synthetic pack. |
| `record-technician-confirmation` | A brief already exists and the technician is confirming the asset and the safety context on a separate review object. |
| `refer-safety-hold` | The brief lists a hold and a supervisor records that it was seen. |

Where the harness selects a skill, it uses the description in the skill file. This starter does not assign a weight and does not list trigger phrases. Selection was not exercised in a tenant.

Each skill calls `src/prepare.py`. The same tests cover that call. A skill must not schedule, dispatch, close, authorise entry, or clear a hold. `human_approval` stays null until `record_review` accepts a technician confirmation. That acceptance still leaves `scheduled` false.

The overview says this harness can create and edit Word, Excel, PowerPoint, and PDF files. This experiment does not use that feature. The brief is JSON.

Memory is described on the overview. This starter does not ask the harness to remember a door code, a tenant, or a previous visit. Do not put the narrative into memory.
