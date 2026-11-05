# Security and permissions

Claims Document Triage Agent, Experiment 35. Catalogue ID B007.

This note matches `agent-manifest.yaml`. `permissions.yaml` is the same file. If the note and the manifest disagree, the manifest is the control. It is written for an insurer deciding whether to try the starter, not as a completed DPIA and not as a claims decision.

## What the process may do

Read one synthetic pack the handler supplies. Call Experiment 12, which calls Experiment 08. Score quoted lines with Experiment 29. Return JSON.

## What it must not do

Accept, decline, or settle a claim. Tell the customer anything. Write a claims system. Approve the class from a sentence inside a file. Describe a prompt as a finding. Describe the output as anonymised. Call a model. Recommend autonomy A3.

`accept_claim`, `decline_claim`, `settle_claim`, `tell_customer`, and `write_claims_system` always raise. `decline_from_score` always raises. A handler record of a class does not switch those functions on.

## Identity and access

The local command has no Entra identity. A later host would run it as an app the claims handler can invoke, not as an account that can edit the claims system. The role on the manifest is Claims handler.

These product pages were not opened on 5 November 2026. Anything about their defaults is unverified:

- Entra Agent ID
- Conditional Access
- Microsoft Purview, including DLP
- Key Vault
- Microsoft Foundry prompt shields
- Application Insights

No secret is stored in this folder. There is no key to put in Key Vault. A later connector would need its own least-privilege registration. This manifest does not grant it.

## Data

The samples are synthetic. A live file would be personal data, and a report that describes an injury can be special category data under UK GDPR Article 9. No Article 6 basis and no Article 9(2) condition is asserted. The data protection officer decides both before any live file.

A file with a deterministic identifier finding is not quoted. The body is not stored on the draft. `output_is_anonymised` stays false. Experiment 08 does not detect every name, email address, or telephone number. That limit is inherited.

UK GDPR Article 22, opened 5 November 2026, has no operative text. The Data (Use and Access) Act 2025 section 80 substituted Articles 22A to 22D, in force on 5 February 2026. A decline can be a significant decision where it produces a legal effect or a similarly significant effect and there is no meaningful human involvement. This agent does not take that decision.

## Consumer Duty and claims handling

PRIN 2.1 Principle 12, opened 5 November 2026: a firm must act to deliver good outcomes for retail customers.

PRIN 2A.2, same day: a firm must act in good faith towards retail customers; must avoid causing foreseeable harm to retail customers; and must enable and support retail customers to pursue their financial objectives. Good faith, on that page, is characterised by honesty, fair and open dealing and acting consistently with the reasonable expectations of retail customers. The paragraph numbers beside those three rules were not in the text retrieved.

ICOBS 8.1, same day: an insurer must handle claims promptly and fairly; provide reasonable guidance to help a policyholder make a claim and appropriate information on its progress; not unreasonably reject a claim (including by terminating or avoiding a policy); and settle claims promptly once settlement terms are agreed. A point-in-time view dated 21 January 2025 labels those words ICOBS 8.1.1R. The current retrieved text did not print "8.1.1" beside the first rule.

A prompt that was treated as a reason to reject, or that labelled the policyholder, would sit badly against those rules. The prompt says it is not a finding and not a reason to choose an outcome. The agent does not reject, and it does not speak to the policyholder. The handler still has to handle the claim promptly and fairly. This starter does not do that handling.

## Logging

This starter writes no log. A later host should log the synthetic claim id, the as-of date, whether a threshold was missed, and whether injection was detected. It should not log the file text. Where that log is stored was not chosen. Application Insights is unverified.

## Kill switch

Do not run the command. There is no published agent to disable.
