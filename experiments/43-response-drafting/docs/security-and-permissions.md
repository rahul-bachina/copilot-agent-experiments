# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

Autonomy **A1**. The representative sends the response. Writes are disabled. Sends are disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. So are redress, case closure, and choosing a recipient address.

## What a run may read

The one case the representative supplies, the approved snippets, the pinned citations in `src/sources.py`, and Experiments 08 and 09 by calling them. The Python starter does not persist the case. A call that is not marked synthetic is refused, and the text is not copied out.

Experiment 08 `propose()` counts UK identifiers. The redacted text is not copied out. `release()` is not called. `output_is_anonymised` stays false. Experiment 08 does not redact names, email addresses, or telephone numbers.

Experiment 09 `line_applicability()` decides whether a snippet may be cited. The correspondence drafter is not run.

## What a run must not do

- Send an email, an SMS, a letter, or a chat reply, including after the representative approves a draft for their own channel.
- Write a Dynamics 365 case or a mailbox.
- Offer redress, close a case, or promise an outcome.
- Treat case text as approval of a recipient. The review object is separate and has no email field.
- Quote a snippet the citation gate refused, or copy that wording into the output.
- Decide that PRIN 2A.5, Article 12, or Equality Act section 20 has been met.

## Platform controls this starter does not configure

These product pages were not opened on 9 November 2026. Treat the names as unverified here. None of these objects is created in this folder.

**Microsoft Entra Agent ID.** Not opened. This starter does not register an agent identity. A deployment that needs one would use a dedicated identity with no mail role and no Dynamics 365 write role. That design was not verified here.

**Conditional Access.** Not opened. This starter does not describe a Conditional Access policy for agents. Confirm the tenant before relying on one.

**Power Platform DLP.** Not opened as a configured policy. The manifest says a later mail, Dynamics 365 write, or payment connector should be blocked. This folder does not create that policy.

**Microsoft Foundry prompt shields.** Not opened. The core does not call a model. The injection tests in this folder are the control on the stand-in. A filter is not a substitute for having no send tool. The portal label is unverified here.

**Key Vault.** Not opened. This starter has no secret to store. A later Foundry key, if one is added, belongs in a vault the organisation already operates. That wiring is unverified here.

**Microsoft Purview.** Not opened. This starter does not set a sensitivity label and does not claim a Copilot Studio audit schema. An organisation that already uses Purview decides whether prompts and drafts are in scope.

**Application Insights.** Not opened. This starter writes no telemetry. Do not put the case text in an application trace.

## Data protection

No lawful basis is asserted. Article 6 and Article 9 were not opened on 9 November 2026. Article 12(1) was opened. It requires clear and plain language for privacy information and for communications under Articles 15 to 22D and Article 34. This service reply is not presented as that information. `article_12_met` stays false.

The case text is not copied into the draft. That is this starter's minimisation practice. It is not a quoted finding under Article 5, which was not opened on 9 November 2026.

Article 22A was not opened on 9 November 2026. This starter does not send, does not decide a complaint, and does not offer redress. It does not certify that a deployment has meaningful human involvement.

## Logging

This starter writes no log. Before live use, log the case id, the snippet ids cited and refused, whether the screens passed, and whether the review was refused. Do not log the case narrative. Experiment 08's audit record omits raw identifier values. Do not add them back.

## Kill switch

Turn the Copilot Studio agent off, remove any later Foundry credential, and block a mail or Dynamics 365 write connector if one is added. Times are the platform's, not a measured drill. Contacts on `harberton.example` are placeholders. Harberton Service is invented.

Reviewed for this starter on 9 November 2026. Next review 9 May 2027, and sooner if PRIN 2A.5, Article 12, or Equality Act section 20 changes.
