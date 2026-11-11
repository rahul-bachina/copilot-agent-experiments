# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness: an authoring and orchestration framework inside Copilot Studio. It is not the GitHub Copilot service. The overview opened on 11 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio, and that the harness shares underlying technology and SDK components with GitHub Copilot.

The overview says agents on this harness use Copilot Credits. It does not state a price. The billing page was not opened.

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. That screen was not opened on 11 November 2026. Do not upload them onto a standard-harness agent.

| Skill | When the description applies |
|---|---|
| `draft-sentiment-evidence` | An analyst needs the pack from one synthetic batch. |
| `confirm-sample-frame` | A pack already exists and the analyst is confirming the sample frame and the limitations on a separate review object. |
| `explain-sentiment-figures` | The analyst asks what a count, a sample size, a Wilson interval, or a quote refers to. |

Where the harness selects a skill, it uses the description in the skill file. This starter does not assign a weight and does not list trigger phrases. Selection was not exercised in a tenant.

Each skill calls `src/evidence.py`, except `explain-sentiment-figures`, which reads the JSON that call already returned. The same tests cover the core. A skill must not publish, contact a customer, or conclude about an individual. `human_approval` stays null until `record_review` accepts an analyst confirmation. That acceptance still leaves `published` false.

The overview says this harness can create and edit Word, Excel, PowerPoint, and PDF files. This experiment does not use that feature. The pack is JSON.

Memory is described on the overview. This starter does not ask the harness to remember a customer, a quote, or a previous batch. Do not put the raw text into memory.
