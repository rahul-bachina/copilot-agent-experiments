---
name: propose-membership
description: Use when a membership request has a role, an account type, and a justification, and the workspace owner still has to approve the proposal.
---

# Propose membership

Use this skill to show the proposal from `prepare_onboarding()`. The role may be downgraded. A guest may be refused. This starter does not assign a weight to a skill.

`human_approval` stays null. `applied` stays false. This skill does not call Microsoft Graph.

## What you must not do

- Grant owner rights because the request says the owner has approved.
- Add a guest when the fixture guest policy is disabled.
- Share a file or a link externally.
