# Microsoft Copilot harness

Catalogue row V007 names the GitHub Copilot harness. On 24 November 2026 the harness overview used the name Microsoft Copilot harness and did not use the words GitHub Copilot harness. See [harness-comparison.md](harness-comparison.md). The skills in this folder are the layout the common brief asks for. They are not a claim that the GitHub Copilot product runs this agent.

The skills are:

- [prepare-grant-package](../skills/prepare-grant-package/SKILL.md) calls `prepare_application()`.
- [record-route-seen](../skills/record-route-seen/SKILL.md) calls `record_route_seen()`.
- [record-applicant-approval](../skills/record-applicant-approval/SKILL.md) calls `record_applicant_approval()`.

Each `SKILL.md` has a single-line `description` that says when to use the skill. The files do not list trigger phrases and they do not assign routing weights.

The harness page says this harness can create and edit files and can use memory. This starter does not give the agent a memory of other charities' bids, and it does not use the file tools to edit the monitoring rows or to produce a document that is then sent. Whether an administrator can turn memory off was not verified.

Tool contracts are the JSON schemas in [../schema/](../schema/). They do not include a submit, a contact, or a send field. `additionalProperties` is false.

The same Python core, the same manifest, and the same tests back the standard-harness guide. Approving a hash writes the synthetic staging row and does not submit the bid.
