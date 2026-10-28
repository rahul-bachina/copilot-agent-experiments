# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

## Autonomy

A1. The AP reviewer approves the recommended resolution. When the draft flags a bank-detail change, a bank-detail verifier acknowledges that route first. The agent does not record either step. It does not post, approve, hold, or pay an invoice, and it does not change supplier bank details.

## Data

**Read, in this starter.** One synthetic case the reviewer supplies: invoice text, a purchase order, a goods receipt, a supplier master of name, VAT number, and a bank fingerprint token, and the as-of date. Experiment 12, called in-process, which calls Experiment 08.

**Not read.** A finance ledger, a supplier bank master in a payment system, HMRC, Companies House, a mailbox, SharePoint, Dataverse. The fingerprint is a token the caller computed. This agent does not collect the sort code or the account number into the draft.

The Python starter does not persist the text. The draft stores labelled fields that pass a shape check, hashes, and closed phrases. It does not store the file body. A case that is not marked synthetic is refused, and the refusal does not echo the body. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

UK GDPR: the lawful basis is not asserted. A sole-trader invoice can be personal data. No Article 9 condition is asserted. The output is not described as anonymised.

## Controls named, and not configured here

| Control | What this starter does |
|---|---|
| Entra Agent ID | Not registered. The product page was not opened for this revision. **Unverified here.** |
| Conditional Access | Not configured. A deployment decision. |
| Power Platform DLP | Block connectors for finance, mail, SharePoint, Dataverse, and a supplier bank master. This starter has no such connector. |
| Microsoft Foundry prompt shields | Not enabled, because no model is called. The product page was not opened. **Unverified here.** |
| Key Vault | No secret in this starter. A later narrative deployment would put a secret here, or use a managed identity. |
| Purview | Not applied. Coverage of a Copilot Studio agent was not verified. |
| Application Insights | No telemetry. Do not trace invoice bodies, VAT numbers, or bank tokens. |

## Bank details

A phrase such as "update the bank details", or a fingerprint that does not match the master, sets `bank_detail_change`. The recommended resolution is `route_to_separate_bank_verification`. The account value is not copied into the draft. `change_supplier_bank_details` always raises. The verifier's record does not verify the account and does not change it. The AP reviewer cannot approve the resolution until that route is recorded, and the approval still does not pay.

## Prompt payment

Procurement Act 2023 sections 68 and 88 are arithmetic on dates the reviewer typed. The draft does not decide that a sum is due, or that an invoice is valid or undisputed. Public Contracts Regulations 2015 regulation 113 is revoked and is not applied. Saving provisions in SI 2024/716 regulations 5 and 6 were not encoded. Nothing is paid, and section 68(4)'s notice to the payee is not sent.

## Kill switch

Turn the Copilot Studio agent off. Remove the in-process import of Experiment 12, and do not describe the run as having inventoried the file. Revoke any later Foundry credential. Block a finance connector with DLP. Times are the platform's, not a measured drill. Contacts on `example.com` are placeholders.

## Review

Assessed 28 October 2026 for this starter rather than a named organisation. Next review 28 April 2027, and sooner if VAT Notice 700/21 sections 4.1, 4.4, or 4.5 change, or if the Procurement Act payment sections change. Residual risk is not all Low. The rows match the manifest.

This starter writes no log. Before live use, log who ran it, the case id, the file hashes rather than the bodies, the exception classes, and the two later human decisions. Do not log the invoice text or a bank value.

There is no ATRS mapping in the manifest. A public body that used this triage on live invoices would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record.
