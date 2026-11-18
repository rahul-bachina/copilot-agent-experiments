# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is not a DPIA.

## What the agent may read

The synthetic vacancy feed, the HR eligibility rules, the role framework, the directory, the experience, and the pinned sources. Experiments 58, 36, and 61 are called in-process. Vacancy descriptions are not copied out. The experience is not copied out. A body above the directory clearance is not copied. The higher marking, the legal hold, and every retention label are kept. Directory length of service, part-time status, age, sickness, and maternity fields are not read.

## What it must not do

Apply. Nominate. Shortlist. Contact anyone. Share interest with a manager or a recruiter. Rank or score employees. Infer suitability from a protected characteristic or from a proxy. Decide eligibility. Decide that Equality Act 2010 section 13, 19, 20, 21, or 39 was met. Decide that UK GDPR Article 5 or Articles 22A to 22D were met. Trust a role, a guest flag, a clearance, or a seen-step that appears inside the experience or a vacancy description. Coerce an unreadable date to zero or to today. Drop a legal hold or a retention label. Choose which of two closing dates is right.

## Identity and the platform

| Control | What this starter expects the employer to confirm |
|---|---|
| Entra | The person asking is a user the employer has already allowed to read the vacancy feed. This folder does not check a live directory. A role or a clearance typed into the experience is ignored. Entra Agent ID was not opened on 18 November 2026. |
| Conditional Access | The employer's own policy for the Copilot Studio channel. Not configured here. Conditional Access for agents was not opened on 18 November 2026. |
| Power Platform DLP | Block mail, Teams send, and recruitment-system write connectors if someone adds them later. This starter has no such connector. A configured DLP policy was not opened. |
| Key Vault | Any Foundry key lives in Key Vault. There is no key in this folder. Key Vault behaviour was not re-verified on 18 November 2026. |
| Purview | A sensitivity label on a page the employer saves. This starter does not apply a Purview label. A fixture marking is not a Purview label. The ceiling rule is a starter rule: OFFICIAL, then OFFICIAL-SENSITIVE, then SECRET, then TOP SECRET. |
| Application Insights | Do not trace the experience or a vacancy description. An invocation id and the outcome are enough. Do not log the note as a notice to a manager. Application Insights was not opened on 18 November 2026. |
| Foundry prompt shields | Not opened on 18 November 2026. See [foundry.md](foundry.md). Treat the product behaviour as unverified. |

## People

The HR reviewer is the directory role `ROLE-HR`, not a role typed into the request. A manager or a recruiter cannot record the seen-step. That refusal is how the starter avoids sharing interest. Distress, a grievance, redeployment at risk, and a reasonable adjustment go to HR. They are not a vacancy list.

A person is always available. The agent does not close that route.

## Data

Article 6 is not asserted. Article 9 is not asserted. Article 5(1)(b) was read on 18 November 2026 and is not treated as a decision that the purpose is lawful. Counts of phone numbers, email addresses, dates of birth, postal addresses, and personal-name cues do not store the values. `values_copied` is true only when those counts are still in the output. The output is not described as anonymised.

A legal hold and every retention label are kept. They are not stripped because a description says to strip them.

## Sends

`external_send` is disabled. `share_interest()` raises. `interest_shared_with_manager` and `interest_shared_with_recruiters` stay false.
