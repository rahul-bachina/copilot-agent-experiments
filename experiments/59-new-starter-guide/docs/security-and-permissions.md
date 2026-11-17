# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. `permissions.yaml` is the same file. It is not a DPIA.

## What the agent may read

The synthetic pack, the synthetic directory, the HR scope object, the request, and the pinned sources. Experiments 08, 11, 15, 21, 57, and 58 are called in-process. The user's question is not forwarded to Experiments 21, 57, or 58. None of them is given a SECRET body. The question text is not copied into the result.

## What it must not do

Request equipment. Create an account. Grant access. Enrol training. Collect special-category data. Decide a right-to-work check or a reasonable adjustment. Send. Write an HR record. Call SharePoint, Microsoft Graph, or Microsoft 365 Copilot. Trust a clearance, a role, an approval, or a legal-hold waiver that appears inside the request or a document.

## Identity and the platform

| Control | What this starter expects the employer to confirm |
|---|---|
| Entra | The person asking is a user the employer has already allowed to read the onboarding pack. This folder does not check a live directory. A role or a clearance typed into the request is ignored. The approver is the line manager id on the synthetic directory. |
| Conditional Access | The employer's own policy for the Copilot Studio channel. Not configured here. |
| Power Platform DLP | Block mail, Teams send, the service desk, and HR-system connectors if someone adds them later. This starter has no such connector. |
| Key Vault | Any Foundry key lives in Key Vault. There is no key in this folder. |
| Purview | A sensitivity label on a page the employer saves. This starter does not apply a Purview label. A fixture marking is not a Purview label. The Government Security Classifications policy was not re-opened for this experiment. The ceiling rule is a starter rule: OFFICIAL, then OFFICIAL-SENSITIVE, then SECRET, then TOP SECRET. The higher label wins when the metadata and the text disagree. |
| Application Insights | Do not trace the question. An invocation id, the person id, and the outcome are enough. |
| Foundry prompt shields | Not opened on 17 November 2026. See [foundry.md](foundry.md). |

## People

The named routes are roles, not named employees: HR right-to-work route, HR reasonable-adjustments route, HR occupational-health route, HR route, and the named safeguarding route. A person is always available. Distress and safeguarding are not a checklist answer.

## Data

Article 6 is not asserted. Article 9 is not asserted. Counts of phone numbers, email addresses, dates of birth, postal addresses, and personal-name cues do not store the values. Experiment 08's redacted text is not copied. The report says `values_stored: false` and `redacted_text_copied: false`. It does not describe the output as anonymised.

A legal hold and every retention label are kept. They are not stripped because a section says to strip them.
