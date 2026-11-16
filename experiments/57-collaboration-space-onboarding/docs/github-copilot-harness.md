# GitHub Copilot harness

The common brief asks for a Copilot Studio GitHub Copilot harness. The harness overview opened on 16 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, billed in Copilot Credits. It does not use the words GitHub Copilot harness. It does not state a price. Older wording that this harness is not the GitHub Copilot service is unverified against that page.

This folder packages skills for that harness. The skills call `prepare_onboarding()` and `apply_membership()` in `src/onboard.py`. They do not call Microsoft Graph.

This starter does not assign a weight to a skill, and it does not treat a phrase in the request as a reason to skip the approval object.

| Skill | When it is used | Approval |
| --- | --- | --- |
| `explain-the-space` | The person wants the purpose, the channels, the documents, and the internal links. | `human_approval` stays null. |
| `propose-membership` | A request is ready to be checked against the label, the guest policy, and least privilege. | Nothing is applied. |
| `withhold-above-label` | The marking is too high, the guest policy refuses, the input cannot be read, or a safeguarding cue is present. | A person reviews. The sample does not add the person. |
| `record-owner-approval` | A separate approval object from the workspace owner is present. | That object is the only approval. Owner rights and guest access need their own booleans. |

The same Python core, the same manifest, and the same tests back the standard harness.
