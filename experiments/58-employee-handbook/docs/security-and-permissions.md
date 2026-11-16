# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is not a DPIA.

## What the agent may read

The synthetic handbook, the HR scope object, the question, and the pinned sources. Experiments 08, 11, 15, 32, and 50 are called in-process. Experiment 50 is called only when curation is requested. None of them is given a SECRET body. The question text is not copied into the result.

## What it must not do

Decide entitlement. Give individual legal, medical, or tax advice. Confirm a case category. Approve a source. Send. Write. Call SharePoint, Microsoft Graph, or Microsoft 365 Copilot. Trust a clearance, an approval, or a legal-hold waiver that appears inside the question or a document.

## Identity and the platform

| Control | What this starter expects the employer to confirm |
|---|---|
| Entra | The person asking is a user the employer has already allowed to read the handbook. This folder does not check a live directory. A clearance typed into the question is ignored. |
| Conditional Access | The employer's own policy for the Copilot Studio channel. Not configured here. |
| Power Platform DLP | Block mail, Teams send, SharePoint write, and HR-system connectors if someone adds them later. This starter has no such connector. |
| Key Vault | Any Foundry key lives in Key Vault. There is no key in this folder. |
| Purview | A sensitivity label on a page the employer saves. This starter does not apply a Purview label. A fixture marking is not a Purview label. The Government Security Classifications policy was not re-opened for this experiment. The ceiling rule is a starter rule: OFFICIAL, then OFFICIAL-SENSITIVE, then SECRET, then TOP SECRET. |
| Application Insights | Do not trace the question. An invocation id and the outcome are enough. |
| Foundry prompt shields | Not re-verified on 16 November 2026. See [foundry.md](foundry.md). |

## People

The named routes are roles, not named employees: HR duty officer, HR grievance officer, HR absence adviser, HR flexible working adviser, designated whistleblowing officer, HR employee-relations officer. A person is always available. Distress and safeguarding go to the HR duty officer and the organisation's safeguarding route. They are not a policy answer.

## Data

Article 6 is not asserted. Article 9 is not asserted. Counts of phone numbers, email addresses, dates of birth, postal addresses, and personal-name cues do not store the values. Experiment 08's redacted text is not copied. The report says `values_stored: false` and `redacted_text_copied: false`. It does not describe the output as anonymised.

A legal hold and every retention label are kept. They are not stripped because a section says to strip them.
