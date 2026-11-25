# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

Autonomy **A1**. The only write is the synthetic staging row, after the named reviewer matches the agent-held hash. Sends are off. Deciding an application, writing production, performing a call-back, and sending are disabled.

## What is read

The pinned schemas, the pinned directory, one pasted synthetic form, and a separate approval object. Experiment 12 does not confirm the file. Experiment 08 does not describe the text as anonymised. A caller-supplied schema is compared and not applied.

## What is stored

The Python starter keeps the agent-held draft in memory for the process, and the approved row in the same process. It does not write a production system. The form body is not copied into the result. Unexpected lines keep a location and not the value. Material field values stay on the review sheet for the named reviewer. The `audit_log` object does not copy them. `described_as_anonymised` stays false. A count below 5 is withheld, including percentages and counts under other field names.

A form that is not marked synthetic is refused, and the refusal does not echo the body.

## People

Distress, safeguarding, and whistleblowing cues, including paraphrases in the fixture, are routed. The cue text is not copied. A negated sentence such as "it is not true that this form includes a safeguarding concern" is not that cue. "I do not feel safe" is.

A signature is present or absent. It is never verified. A bank-details change is flagged for a human call-back and the call-back is not performed.

## UK GDPR

Article 5(1)(c) and Article 5(1)(d) were opened on 25 November 2026 and are quoted in `src/sources.py`. The quotes are data minimisation and accuracy. They are not a finding that this starter meets them. Article 6 and Article 9 were not opened. No lawful basis is asserted.

## Controls that were not opened

[Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id) was not opened for this experiment on 25 November 2026. Treat the current licence names and the distinction between an agent identity and a user account as unverified here. This starter does not register an agent identity or a Conditional Access policy.

[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/overview) was not opened on 25 November 2026. This starter has no secret and no model endpoint. A deployment that added a narrative model would put a secret there if a managed identity could not be used.

Microsoft Purview audit of Copilot activity was not verified for this starter. Do not assume a draft record is audited.

Power Platform DLP is the control that would block a mail, SharePoint, Dataverse, or bank connector if one were added later. This starter has no such connector. The DLP product page was not opened on 25 November 2026.

Application Insights is where a deployment would send a trace. This starter writes no application log. Do not put the form body or a bank value in a trace. Log the extraction id, the form type, the question date, and whether a flag was raised.

Microsoft Foundry prompt shields were not opened on 25 November 2026. Treat that product behaviour as unverified. They would not replace the missing send tool.

## Logging before live use

This starter writes no log. Before live use, log who ran it, the extraction id, the question date, the content hash rather than the form body, whether a route was raised, and the reviewer's later decision. The agent does not write that decision except through the approval function, and only into the synthetic store.

## ATRS

There is no ATRS mapping that submits a record. A public body that used this extractor on live forms would consider the Algorithmic Transparency Recording Standard separately. Experiment 03 can draft an assurance pack. This experiment does not.

Reviewed for this starter on 25 November 2026. Next review 25 May 2027, and sooner if Article 5 or Experiment 08 or 12 changes.
