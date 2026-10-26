# Experiment 08: Sensitive Data Redaction Agent

UK identifier PII gateway. Catalogue ID **O005**.

A small gateway other experiments can call before text goes to a model. It proposes redactions for UK identifiers: National Insurance number, NHS number, sort code and account number, UK postcode, Companies House company number, and two close carriers (a GB IBAN, and a labelled Unique Taxpayer Reference). It writes a DPO audit record that does not contain the raw values.

**Autonomy A1.** A privacy reviewer approves the redacted output before anyone releases it. The agent never releases or sends that output. It has no tool that does so.

This is not a generic PII agent. It does not look for names, email addresses, or telephone numbers. It does not call Azure AI Language. Checksums run only where a published rule exists (NHS number modulus 11, and the ISO 13616 rearrangement for a GB IBAN). Everything else is a format or a label. Misses and over-redactions are both expected. The output is never described as anonymised.

Stack: Azure and Power Platform, in the catalogue's labels. What you can run today is Python in the standard library. No Azure credentials and no network.

## The problem

A council, an NHS corporate team, or a regulated firm that sends free text to a model needs UK identifiers taken out first, and a log a DPO can read. Generic redactors are built around US shapes. They are weak on a National Insurance number, an NHS number, a sort code, a UK postcode, and a Companies House number, and they rarely keep a decision log that does not itself repeat the identifier.

The DWP Whitemail record describes redacting personal data before processing. The ICO's anonymisation guidance, read on 26 October 2026, says replacing an identifier is pseudonymisation when the original can be tied back, and that pseudonymous data is still personal data. Calling the result "anonymised" is the mistake this gateway is built to refuse.

## Who it helps

**Other experiments in this repository.** They call `propose()` on one text, pass their own experiment id as `caller`, and receive redacted text plus an audit record. They still do not release anything. Experiment 08 does not reach into their stores.

**A privacy reviewer.** They see each proposed span, the detector, and whether a checksum passed. They approve, reject, or send it back. Approval still does not release the text. A person releases it in the organisation's own channel, if they decide to.

**A DPO.** The audit record has a hash of the input, the entity type, the character offsets, the detector, and the checksum result. It does not contain the identifier. The reversible token map, if the caller asked for one, is a separate object and is not written into that log.

## Non-goals

- Deciding that text is anonymised, de-identified, or safe to publish.
- Releasing, sending, filing, or copying the redacted text anywhere.
- Approving its own output. The privacy reviewer is a person. The agent cannot call the decision function. The skills say so.
- Detecting names, email addresses, telephone numbers, dates of birth, postal addresses beyond the postcode, or free-text descriptions of a person.
- Detecting UK driving licence numbers, electoral roll numbers, passport numbers, or VAT numbers. Azure AI Language lists some of these. This gateway does not copy that list, and the VAT checksum was not opened.
- Implementing the Pay.UK sort-code modulus specification. A sort code here is a shape, not a directory lookup.
- Distinguishing a Scottish Community Health Index number or a Northern Ireland Health and Care Number from an NHS number. Those schemes are not encoded.
- Reading a case system, a mailbox, the Companies House register, or the NHS Personal Demographics Service.
- Training or calling a model. Optional model assistance is an interface. The default implementation returns nothing.

## What the gateway does

`src/gateway.py` calls the detectors in `src/detectors.py`. The same text and the same rules always produce the same spans. Nothing in that path reads the network.

| Identifier | What is detected | Checksum |
| --- | --- | --- |
| National Insurance number | Two letters, six digits, suffix A–D, with or without single spaces. HMRC's three prefix rules are recorded, not used to drop the span. | None. HMRC does not publish one. |
| NHS number | Grouped 3-3-4 when the [NHS Data Dictionary](https://www.datadictionary.nhs.uk/attributes/nhs_number.html) modulus 11 check passes. A failed check is redacted only when the text labels it as an NHS number. An unlabelled continuous 10-digit number is not redacted. | Modulus 11, weights 10 down to 2. A step-4 result of 10 means invalid. A result of 11 is check digit 0. |
| Sort code | `NN-NN-NN`. A value that also looks like a day and month is left in place unless the words "sort code" are next to it. | Not the Pay.UK modulus check. |
| Account number | Six to ten digits after an account-number label, or eight digits shortly after a sort code that was redacted. | None. |
| UK postcode | The six shapes in the 2015 ILR postcode annex, with a single space, excluding C, I, K, M, O, and V from the inward code. | None. Not a Royal Mail lookup. |
| Companies House number | A prefix from the 2011 URI customer guide, plus six digits, or eight digits after a company-number label. | None. The register is not queried at runtime. |
| GB IBAN | `GB` plus the usual length. | ISO 13616 rearrangement, mod 97 remainder 1. The paid ISO text was not opened. See limitations. |
| Unique Taxpayer Reference | Ten digits after "UTR" or "unique taxpayer reference" only. | Not implemented. The HMRC checksum was not opened. |

A model may suggest extra spans. Those suggestions are not applied unless the caller sets `apply_model_suggestions=True`, and even then they are marked as model suggestions. The default model returns nothing. A suggestion cannot clear a deterministic hit, cannot set the anonymisation flag, and cannot release the text.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/08-uk-pii-redaction-gateway
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/gateway.py --input examples/sample_input.txt --caller exp-08-readme
```

`eval/evaluate.py` prints a **smoke test of the deterministic rules** against synthetic fixtures. It is not a model score and it is not a real-world recall rate. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running.

Another experiment calls the same function:

```python
import sys
from pathlib import Path

sys.path.insert(0, "experiments/08-uk-pii-redaction-gateway/src")
from gateway import propose, release

proposal = propose("NHS number 999 000 0018", caller="exp-07-consultation-themes")
assert proposal["anonymisation"]["output_is_anonymised"] is False
assert proposal["release"]["agent_may_release"] is False
release(proposal)  # raises ReleaseForbidden
```

## Sample

The sample text uses only the synthetic values documented under Limitations. The proposal redacts them, keeps the audit record free of the raw values, and leaves `agent_may_release` false.

## Limitations

Honest misses and over-redactions, measured on the synthetic fixtures rather than on live text:

- **False negatives.** An unlabelled continuous NHS number, even one that passes modulus 11. An unlabelled account number that is not next to a sort code. A postcode with the space missing. `GIR 0AA` and BFPO forms, which are not in the six ILR shapes. A company number of eight digits with no label. A VAT number. A name, an email address, or a telephone number. A sort code written as six digits with no hyphens and no label. Text that describes a person without using one of these shapes.
- **False positives.** A National Insurance shape is distinctive and still collides with some reference codes. A grouped 3-3-4 number that happens to pass modulus 11 (about one in eleven random 10-digit values pass) is redacted even when it is not an NHS number. A hyphenated `NN-NN-NN` that is not a date shape is redacted even when it is not a sort code. A postcode shape is redacted even when it is not a live delivery point.
- **The e-RS example does not pass the dictionary check.** [NHS England's synthetic-data note](https://digital.nhs.uk/services/e-referral-service/document-library/synthetic-data-in-live-environments), read on 26 October 2026, gives `999 123 4566` and says numbers starting 999 will never be issued to real patients. Applying the Data Dictionary steps to `9991234566` produces a step-4 result of 10, which the dictionary says is invalid. This gateway follows the dictionary. The [NHS service manual](https://service-manual.nhs.uk/design-system/patterns/ask-for-nhs-numbers) example `999 123 4567` fails the same way. Neither is redacted unless the text labels it as an NHS number. Fixtures use `999 000 0018` and `999 000 0026`, which this repository calculated so the check digit matches. They were not issued by the NHS England test-data team. Do not use them as live synthetic patients.
- **National Insurance fixtures are not allocatable.** `QQ 12 34 56 A` is the example in [NIM39110](https://www.gov.uk/hmrc-internal-manuals/national-insurance-manual/nim39110), which says it must not be used as an actual number. Q is not an allowed prefix letter. `BG`, `GB`, `KN`, `NK`, `NT`, `TN`, and `ZZ` are the prefixes NIM39110 says are not to be used. No fixture uses a prefix that passes those three rules.
- **Company number.** `SC000000` is a shape from the [2011 URI guide](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/809682/uniformResourceIdentifiersCustomerGuide.pdf) (prefix `SC`, six digits). On 26 October 2026 the public page `https://find-and-update.company-information.service.gov.uk/company/SC000000` returned HTTP 404. That is a point-in-time check, not a reservation, and the register is not queried again at runtime. The guide's own examples `02050399` and `SC002180` are not used here.
- **Postcode.** `ZZ99 9ZZ` is the generic postcode the 2015 [ILR annex](https://assets.publishing.service.gov.uk/media/5a7f4a19ed915d74e62298dd/ILRSpecification_2015_16_Appendix_C_Feb2015_v1.pdf) tells providers to return when the postcode is unknown. It is not a person's address. The annex was published in February 2015. Later Royal Mail rules were not opened.
- **IBAN.** `GB76XXXX00000000000000` was calculated in this repository so the mod-97 remainder is 1. Bank code `XXXX` and sort code `000000` are not an issued account. The ISO 13616 text was not purchased. The steps used are the published rearrangement (move the first four characters to the end, A=10 … Z=35, remainder 1). Treat the link to the paid standard as unverified.
- **Sort code `00-00-00`** is a shape illustration. It was not checked against the Extended Industry Sort Code Directory.
- **Not anonymisation.** Redaction of these spans leaves everything else. A reversible map would make the output pseudonymous at best, in the ICO's sense, and only if the map is held separately. This starter does not persist the map. `output_is_anonymised` is always false.
- **Rules go stale.** The pinned date is 26 October 2026. A caller who passes an earlier `rules_as_of` is told the rules may be stale. Detection still uses the pinned rules. A sentence in the text cannot switch them off.
- **Azure AI Language** was not called. On the [entity list](https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/concepts/entity-categories) read on 26 October 2026, UK National Insurance number, UK National Health number, and UK Unique Taxpayer number are categories. Sort code and bank account number are marked preview. Zip code is marked preview, and the tag cell in the retrieved page did not match the heading, so this note does not claim UK postcode detection there. Companies House numbers were not in the UK section that was read.

This is not legal advice, a DPIA, or a statement that a deployment is compliant.

## Two Copilot Studio harnesses

Both call `propose()` and both stop before release. Neither harness sends. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. Paste text, show the proposal, stop for the privacy reviewer. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a reviewer who wants the findings explained. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft bills that harness in Copilot Credits. Prices were not copied.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- How another experiment calls the gateway: [docs/calling-the-gateway.md](docs/calling-the-gateway.md).
- Microsoft Foundry path, optional and not deployed: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/08-uk-pii-redaction-gateway/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── detectors.py
│   ├── gateway.py
│   ├── identifiers.py
│   └── model_assist.py
├── copilot-studio/
│   ├── README.md
│   ├── system-prompt.md
│   └── power-automate-flow.md
├── skills/
│   ├── propose-redaction/SKILL.md
│   └── explain-redaction-finding/SKILL.md
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened for this revision

Read on 26 October 2026 unless the page itself carries an older publication date.

- [NHS NUMBER, NHS Data Dictionary](https://www.datadictionary.nhs.uk/attributes/nhs_number.html), modulus 11
- [Synthetic data in live environments, NHS England](https://digital.nhs.uk/services/e-referral-service/document-library/synthetic-data-in-live-environments)
- [NHS numbers, NHS service manual](https://service-manual.nhs.uk/design-system/patterns/ask-for-nhs-numbers)
- [NIM39110, HMRC](https://www.gov.uk/hmrc-internal-manuals/national-insurance-manual/nim39110)
- [Companies House URI customer guide (2011)](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/809682/uniformResourceIdentifiersCustomerGuide.pdf), prefix list
- [ILR specification 2015 to 2016, Annex C](https://assets.publishing.service.gov.uk/media/5a7f4a19ed915d74e62298dd/ILRSpecification_2015_16_Appendix_C_Feb2015_v1.pdf), postcode shapes
- [ICO, introduction to anonymisation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/introduction-to-anonymisation/)
- [ICO, pseudonymisation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/pseudonymisation/)
- [PII entity categories, Azure Language in Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/concepts/entity-categories)
- [Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Conditional Access for agents, Microsoft Entra](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
