# Microsoft Copilot harness

The overview opened on 19 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. This folder is the layout the common brief calls the GitHub Copilot harness: `skills/<name>/SKILL.md`, with the tool contract and the approval gate in the skill. The overview does not use those words. Treat the name in this folder as packaging.

Skills:

- `skills/propose-skills/SKILL.md` calls `propose_inventory()`.
- `skills/record-employee-decision/SKILL.md` calls `record_employee_decision()`.
- `skills/record-hr-validation/SKILL.md` calls `record_hr_validation()`.
- `skills/route-a-person/SKILL.md` calls `record_route_seen()`.

Each description is one line and says when to use the skill. The files do not list trigger phrases and do not assign a routing weight. Where a tenant uses generative orchestration, selection is from the description. That behaviour was not re-tested in a tenant on 19 November 2026. Treat a live routing result as unverified.

The harness can create files, on the overview page. This starter does not ask it to. A Word file of the inventory would still have to come from the JSON, and the employee would still have to confirm each skill. Creating that file was not tested.

Memory, on the overview page, is a harness feature. This starter does not store a skill as memory. A remembered confirmation would not replace the hash check.

Copilot Credits are the billing unit named on the page. No price is stated there. The billing article was not opened.
