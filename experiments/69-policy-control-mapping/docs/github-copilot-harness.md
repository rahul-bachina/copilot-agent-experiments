# Microsoft Copilot harness

Catalogue row L003 names this harness first, with Microsoft 365. The layout is the skills folder the common brief calls the GitHub Copilot harness.

The overview opened on 20 November 2026 calls it the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, and it says agents on this harness use Copilot Credits. It states no price. It does not use the words GitHub Copilot harness.

Skills:

- `skills/propose-control-mappings/SKILL.md` calls `map_controls()`.
- `skills/record-mapping-approval/SKILL.md` calls `record_owner_approval()`.
- `skills/route-to-control-owner/SKILL.md` stops a routine proposal when the outcome is `human_route`.

The description in each skill is one line and says when to use the skill. The files do not list trigger phrases and do not assign routing weights. Where a tenant uses generative orchestration, the platform selects from the description. That selection is the platform's. This folder does not claim a weight.

File creation on this harness is not used to edit a policy. No skill writes to a GRC system. No skill connects to SharePoint. Microsoft 365 is where a deployment would read policies from, and this starter does not.

Approval is the separate object. A sentence in a policy that says the control owner has approved is recorded and not followed.
