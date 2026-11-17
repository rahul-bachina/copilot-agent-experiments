# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is not a DPIA.

## What the agent may read

The synthetic catalogue, the role framework, the directory, the goals, and the pinned sources. Experiments 58, 44, and 36 are called in-process. Course descriptions are not copied out. Goals are not copied out. A body above the directory clearance is not copied. The higher marking, the legal hold, and every retention label are kept.

## What it must not do

Enrol. Book. Spend. Rank employees. Infer ability from a protected characteristic. Use the plan for performance or promotion. Decide a reasonable adjustment. Decide that someone may make an Employment Rights Act 1996 section 63D application. Trust a role, a guest flag, a clearance, or an approval that appears inside the goals or a course description. Coerce an unreadable cost, date, or budget to zero. Drop a legal hold or a retention label.

## Identity and the platform

| Control | What this starter expects the employer to confirm |
|---|---|
| Entra | The person asking is a user the employer has already allowed to read the catalogue. This folder does not check a live directory. A role or a clearance typed into the goals is ignored. Entra Agent ID was not opened on 17 November 2026. |
| Conditional Access | The employer's own policy for the Copilot Studio channel. Not configured here. Conditional Access for agents was not opened on 17 November 2026. |
| Power Platform DLP | Block mail, Teams send, learning-system write, and payment connectors if someone adds them later. This starter has no such connector. A configured DLP policy was not opened. |
| Key Vault | Any Foundry key lives in Key Vault. There is no key in this folder. Key Vault behaviour was not re-verified on 17 November 2026. |
| Purview | A sensitivity label on a page the employer saves. This starter does not apply a Purview label. A fixture marking is not a Purview label. The ceiling rule is a starter rule: OFFICIAL, then OFFICIAL-SENSITIVE, then SECRET, then TOP SECRET. |
| Application Insights | Do not trace the goals or a course description. An invocation id and the outcome are enough. Application Insights was not opened on 17 November 2026. |
| Foundry prompt shields | Not opened on 17 November 2026. See [foundry.md](foundry.md). Treat the product behaviour as unverified. |

## People

The approvers are the employee and the manager on the synthetic directory, not a role typed into the request. A people partner on the directory may record that an adjustment route has been seen. That is not a decision that the adjustment is reasonable. Distress and wellbeing go to the line manager and the organisation's wellbeing route. They are not a learning plan.

A person is always available. The agent does not close that route.

## Data

Article 6 is not asserted. Article 9 is not asserted. Counts of phone numbers, email addresses, dates of birth, postal addresses, and personal-name cues do not store the values. `values_copied` is true only when those counts are still in the output. The output is not described as anonymised.

A legal hold and every retention label are kept. They are not stripped because a description says to strip them.

## Spend

`spend_transact` is disabled. The apprenticeship levy pages that were opened are context. The funding-rules document was not opened. `levy_account_used` stays false.
