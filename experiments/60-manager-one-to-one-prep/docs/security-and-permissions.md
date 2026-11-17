# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. `permissions.yaml` is the same file. It is written for an employer deciding whether to try the starter, not as a completed DPIA.

The agent reads one synthetic selection and returns a prep note, or a refusal, or a human flag. Autonomy is A0. The line manager selects the context first and decides whether to rely on the note. The agent cannot rate performance, read a mailbox, or send.

## What it can read

**Read, in this starter.** The selection. The synthetic directory. The selected notes, objectives, shared updates, and calendar items, when the kind is allowed and the marking is at or below the ceiling and the directory clearance. The static pins in `src/sources.py`. Experiments 08, 15, 41, and 51, in process.

**Not read into the note.** A mailbox or a chat, even if the pack contains it or the manager's list names it. A source above the ceiling. A sentence that is an instruction, a denial, a distress sign, or a personal circumstance. Phone numbers, email addresses, dates of birth, postal addresses, and other people's names are masked. The values are not stored. The output is not described as anonymised.

The manifest does **not** assert a UK GDPR lawful basis. Article 5(1)(a) and Article 5(1)(c) were read on 17 November 2026. Article 6 and Article 9 were not opened. A note about health may be special-category data. No Article 9 condition is asserted. The Python starter does not persist the notes.

Articles 22A to 22D were read on 17 November 2026. They were substituted for Article 22 on 19 June 2025 for specified purposes and on 5 February 2026 in so far as not already in force. S.I. 2026/82 regulation 5 was not opened. No Article 22D regulations were read. Whether any have been made is unverified. This starter does not take a significant decision. `performance_rating` stays null. A disabled tool is not, by itself, a claim of meaningful human involvement.

## Controls named for a deployment

This repository does not configure them.

| Control | What a deployment would still decide |
|---|---|
| Entra Agent ID | The agent's identity, separate from the manager. Not created here. |
| Conditional Access | Who may open the agent. Not configured here. |
| Power Platform DLP | Block connectors for mail, chat, and the HR system. This starter has no such connector. |
| Purview | A sensitivity label on a note a person chooses to save. The starter does not apply one. A legal hold on a source is preserved in the JSON. |
| Microsoft Foundry prompt shields | An optional control if a narrative model is added. The tests do not call a model. Announced behaviour was not re-tested here and is unverified. |
| Key Vault | Where a deployment would keep a Foundry credential. This starter has no credential. |
| Application Insights | A UK-resident log of the meeting reference, not the note text. Not configured here. |

## Equality Act 2010

Section 4 lists the protected characteristics. Section 39(2) prohibits discrimination against an employee, and section 39(5) states the duty to make reasonable adjustments. Both pages are England and Wales and Scotland. This starter does not decide that discrimination occurred and does not infer a characteristic. Northern Ireland equality law was not opened.

## ICO monitoring guidance

The monitoring-workers hub and the solely-automated page were opened on 17 November 2026. Both carry a banner that the guidance is under review because of the Data (Use and Access) Act. The automated page still names Article 22. Reconciliation with Articles 22A to 22D is unverified. This starter does not decide that preparing a note from sources a manager selected is monitoring of workers.

## Residual risk

Assessed 17 November 2026 for this starter rather than a named employer. The rows match the manifest. The ones to read first are an unselected mailbox treated as context (R1), a rating presented as the agent's view (R2), a distress sentence placed on the routine agenda (R3), and a SECRET cover or a typed clearance (R4).
