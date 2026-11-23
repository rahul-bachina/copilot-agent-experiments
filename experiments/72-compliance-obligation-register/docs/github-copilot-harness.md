# Microsoft Copilot harness

The skills are the Microsoft Copilot harness, packaged in the layout the common brief calls the GitHub Copilot harness. See `harness-comparison.md` for what the overview page did and did not say on 23 November 2026.

| Skill | Calls | Does not |
|---|---|---|
| `propose-obligation-records` | `propose_register()` | Stage, decide applicability, assign accountability, or send |
| `approve-register-change` | `stage_approved_change()` | Read the word approved out of the source |
| `route-to-compliance-owner` | `record_route_seen()` | Copy the cue, or stage a route |

Each `SKILL.md` description is a single frontmatter line and says when to use the skill.
