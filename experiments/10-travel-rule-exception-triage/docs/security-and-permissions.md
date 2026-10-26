# Security and permissions

Travel Rule exception triage, Experiment 10. Catalogue ID UK05.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for a firm deciding whether to try the starter, not as a completed DPIA.

## Purpose

The agent reads one transfer and returns a draft triage against the pinned Part 7A text and the FCA Travel Rule statement. Autonomy is A1. An analyst decides hold, return, or escalate. The agent cannot execute that decision.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Hold, delay, return, reject, or release a transfer.
- Make a cryptoasset available to a beneficiary.
- Contact a counterparty, a customer, the FCA, or law enforcement.
- File, draft, or suppress a suspicious activity report.
- Report repeated failure to the FCA.
- Confirm a regulation 64A exclusion, or decide that the firm has breached the Money Laundering Regulations.
- Write a production record or send a message.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. `tests/test_triage.py` and `tests/test_injection.py` check that an instruction inside a record does not become an action.

## Data

**Read, in this starter.** The one record the analyst supplies. The as-of date and the stale threshold. The static catalogue.

**Not read.** Wallets and private keys, chain nodes, Travel Rule messaging networks, customer files beyond the fields pasted for this transfer, suspicious-activity-report systems, FCA Connect, other customers' transfers, and the Experiment 04 policy pack.

Names on a transfer are personal data. The manifest does **not** assert a UK GDPR lawful basis. A candidate for the firm to confirm is Article 6(1)(c), legal obligation, because Part 7A requires the firm to handle this information. Do not copy a public-task basis from Experiment 01. Special-category data is out of scope. A date and place of birth is not treated here as special-category data. The firm confirms that.

The Python starter does not persist the record. A record that is not marked synthetic is refused, and the refusal does not echo the narrative. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use Harbourline Markets Ltd, the invented firm from Experiment 04, and wallet strings that start with `SYNTH-WALLET-`. They are not live addresses.

## Prompt injection and stale data

Notes and name fields are untrusted. The scanner quarantines a field that tells the checker to ignore instructions, release the transfer, file or suppress a report, contact the counterparty, or change the threshold. A quarantined name does not count as information received. A payload key that purports to set the analyst's decision is stripped.

The stale-data test compares `last_verified` (26 October 2026 in this catalogue) with the as-of date. Older than the threshold, default 90 days, is stale. Equal to the threshold is not. The same rule applies to `counterparty.status_recorded_on`. A stale jurisdiction status is not treated as sunrise. The checker does not download the page.

The August 2023 JMLSG annex still says 1,000 euros. The operative threshold is £800, from the revised regulation. `flags.jmlsg_euro_threshold_used` is false. That is tested.

The residual risk is a misleading brief if a model is later wrapped around the JSON. The analyst is the control. There is no autonomous action behind a bad draft.

## Human approval

Autonomy A1 means a person decides. The agent still has no tool that carries the decision out. Approving a sentence in the chat does not hold or return a transfer.

| Decision | Who |
|---|---|
| Hold, return, or escalate | Analyst |
| Treat a field as missing or as non-corresponding | Analyst |
| Rely on a counterparty Travel Rule status | Analyst, after the register is current |
| Rely on a row after a source is marked stale | Analyst, after someone re-opens the page |
| Confirm a regulation 64A exclusion | Analyst |
| Request missing information from a counterparty | Analyst, through the firm's own channel |
| File a suspicious activity report, or report repeated failure to the FCA | MLRO or other authorised person. Outside the agent. |

Viewing a draft and re-running it do not need a separate approval.

## Controls a tenant would discuss

Named here, and not configured in this repository. Product pages for these controls were not opened on 26 October 2026, except the Copilot Studio harness overview cited in the harness notes. Treat detailed behaviour as unverified.

| Control | How a firm might use it |
|---|---|
| Entra Agent ID | An identity for the agent, separate from the analyst, with no wallet or messaging role. |
| Conditional Access | Limit who can open the agent, and from where. |
| Power Platform DLP | Block connectors for mail, Travel Rule messaging, and case writes. This starter has no such connector. |
| Microsoft Foundry prompt shields | On, if a model sees the record. Not a substitute for the missing release tool. |
| Key Vault | Any later secret for a Foundry deployment. The checklist has no secret. |
| Purview | A sensitivity label on a draft the analyst chooses to save. The starter does not apply one. |
| Application Insights | Invocation logs without the transfer narrative. Not wired up here. |

Experiment 01 records Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access as announced, with availability unverified. This folder did not re-check that announcement.

## Risk register

Assessed 26 October 2026 for this starter rather than a named firm. Residual risk is not all Low. The rows match the manifest.

| ID | Risk | Residual | Owner in the manifest |
|---|---|---|---|
| R1 | A missing field is treated as a breach, or a complete record is treated as a release | Medium | Financial crime operations |
| R2 | The JMLSG euro figure is applied instead of £800 | Low | Financial crime operations |
| R3 | A stale sunrise flag, or a sunrise receipt treated as waiving regulation 64D | Medium | Financial crime operations |
| R4 | Prompt injection releases a transfer, files a report, or contacts a counterparty | Low | Information security |
| R5 | A live transfer is pasted into a shared test run | Medium | Data protection officer |
| R6 | A pinned page changes and the checklist is still treated as current | Medium | Financial crime operations |

## Logging

This starter writes no log. Before live use, log who ran it, the transfer id rather than the names, the as-of date, whether a source was stale, and the analyst's later decision. Do not log the note text in an application trace.

## Kill switch

Turn the Copilot Studio agent off. Remove any Foundry access, using Key Vault or the role assignment if one was created. Block a later connector in a Power Platform DLP policy.

Contacts in the manifest use `example.com`. They are placeholders.

## Review

26 October 2026. Next review 26 April 2027, and sooner if Part 7A, the FCA statement, or the JMLSG annex changes.

There is no ATRS mapping. ATRS is a public-sector standard. A firm does not complete an ATRS record by using this starter. Experiment 03 can draft an assurance pack. This experiment does not.
