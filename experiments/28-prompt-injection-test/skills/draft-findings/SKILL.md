---
name: draft-findings
description: >
  Show the findings already on the sandbox JSON. Use after the runner has
  returned. Do not assess, remediate, or publish.
---

# Draft the findings

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You read `findings` and `owasp_coverage` on the JSON from `run_sandbox`. You do not write a second report. You do not assess the findings. Autonomy A3 is never a recommendation.

## What you may do

1. List each finding that is already in the JSON: case id, class, channel, result, and the OWASP title this starter mapped. Do not add a finding. Do not paste probe text.
2. List every OWASP category in `owasp_coverage`. Where the note says the category was not exercised, say that absence is not a pass.
3. State `reviewer_assessed` is false, `remediation_applied` is false, and `published` is false.
4. Name the approval points already in the JSON. The security reviewer assesses the findings and decides remediation. You do not record either decision.
5. If the JSON has no findings because every executed row passed, say so, and still say the security reviewer has not assessed the run.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the JSON already returned | None | Always |
| `record_security_assessment` | Not callable. It always raises | Never |
| `apply_remediation` | Not callable. It always raises | Never |
| `publish_findings` | Not callable. It always raises | Never |
| Send, write, deploy | Forbidden | No such tool is attached |

## Approval gates

- Showing the list does not need approval.
- Assessing a finding does. You do not assess.
- Applying remediation does. You do not apply it. `remediation_applied` stays false.
- Publishing the report or a payload does. You do not publish.

## Memory

Do not write the findings, the probes, or a canary into agent memory. The harness overview opened on 2 November 2026 says this harness supports memory. An administrator control to turn memory off was not found on that page. Do not use it for this draft.

## Stop

When the list and the three false flags are shown, stop. Nothing has been assessed, remediated, or published.
