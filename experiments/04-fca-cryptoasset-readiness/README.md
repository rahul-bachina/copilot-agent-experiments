# Experiment 04: FCA cryptoasset authorisation readiness

Catalogue ID **UK02**. Autonomy **A0**.

A starter for a compliance team preparing a cryptoasset firm for FCA authorisation. It reads a pack of synthetic policy documents and returns a draft register of observations against a pinned list of FCA pages. Each row cites the page it came from. Consultation-stage and planned items are marked as such. The Compliance Officer or the MLRO owns every gap conclusion.

The agent does not say that a firm is ready, and it does not say that a firm is not ready. It does not give regulatory advice or legal advice. The output is labelled **DRAFT FOR HUMAN REVIEW**.

This folder is a deterministic checker, a permissions manifest, synthetic fixtures, and build notes for two Copilot Studio harnesses. The lead shape is the Copilot Studio GitHub Copilot harness (reasoning over a pack of files, skills, a sandbox draft). The standard harness is a lighter intake that runs the same checker and stops. Nothing here calls a model or the network.

Stack in the catalogue: Copilot Studio on the GitHub Copilot harness, Microsoft Foundry, and Azure. The runnable part is Python in the standard library.

The firm in the samples is **Harbourline Markets Ltd**. It is invented. It is not an applicant and not a registered cryptoasset business.

## The problem

Firms that want to carry on the new UK cryptoasset regulated activities need FCA authorisation under FSMA, or a variation of permission if they are already authorised. Registration under the Money Laundering Regulations does not convert into that permission. The FCA has published a fixed application period and a set of policy statements. A compliance team has to read its own policies against that material and keep consultation items separate from rules the FCA has already made.

The pages opened for this starter, all on 24 October 2026, say:

- The application period started on 30 September 2026 and will close on 28 February 2027 ([How the gateway will operate](https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/how-gateway-will-operate), last updated 30 September 2026).
- The new regime starts on 25 October 2027, when the Financial Services and Markets Act 2000 (Cryptoassets) Regulations 2026 take effect ([What you need to do](https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/what-you-need-to-do), last updated 16 September 2026). The regime landing page, last updated 30 September 2026, uses different words: the regime is **expected** to come into force on 25 October 2027. This checker pins 25 October 2027 and records both wordings. It does not decide which sentence is the legal commencement.
- Existing registrations and permissions will not convert automatically ([PS26/18](https://www.fca.org.uk/publications/policy-statements/ps26-18-cryptoasset-perimeter-guidance); the [gateway page](https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/how-gateway-will-operate); the [30 June 2026 overview](https://www.fca.org.uk/publications/policy-statements/cryptoasset-regime)).

The MLR registration page still describes what the FCA looks for in a registration application: a business-wide risk assessment, a customer risk assessment, customer due diligence, on-chain and off-chain monitoring with rules and thresholds, Travel Rule procedures and a flow of funds, a financial promotions policy, and an MLRO. The June 2026 policy statements name the Handbook sourcebooks for the FSMA regime, including safeguarding, the Consumer Duty, operational resilience, and SM&CR. Some of that material is final and not yet in force. Some of it is still a consultation, or only a plan to consult.

## Who it helps

A Compliance Officer or MLRO who already has draft policies and wants a first pass: which documents were in the pack, which expected phrases were missing from the text, which FCA page the expectation came from, and which items must not be treated as in-force rules. They decide what is actually a gap.

It does not help a firm that wants the tool to bless an application.

## Non-goals

- Regulatory advice, legal advice, or a view on whether a permission is required.
- Any conclusion that the firm is ready or is not ready for authorisation or for MLR registration.
- Accepting, rejecting, or editing a gap. The Compliance Officer or MLRO does that.
- Submitting an application, using Connect, emailing the FCA, or booking a pre-application meeting.
- Filing a suspicious activity report, or deciding that activity is suspicious.
- Approving a financial promotion, or acting as a section 21 approver.
- Deciding that the firm has breached the Consumer Duty, the MLRs, the Travel Rule, CASS, or SM&CR.
- Turning a consultation, a guidance consultation, or a plan to consult into a final rule.
- Reading the live FCA website at run time. Citations come from the pinned catalogue in `src/sources.py`.
- Writing a production register, a SharePoint library, or any other record.
- Using real firms, real people, or live policy text. The fixtures are synthetic.

## What the checker does

`src/gap_register.py` reads a pack and writes one JSON document. The same pack and the same as-of date always produce the same JSON. It does not call a model.

A row is an observation about text:

| Observation | Meaning |
|---|---|
| `signal_present` | The expected phrases were found in a document of the relevant type, ignoring lines that look like prompt injection. |
| `signal_not_found` | A document of that type was supplied, and one or more phrases were not found. |
| `document_not_supplied` | The pack had no document of that type. |
| `document_quarantined_prompt_injection` | An instruction aimed at the checker was split across lines. That document is not used as evidence. |
| `not_indicated_in_the_text` | The row only applies if the pack shows the activity, for example stablecoin issuance. The pack does not. |
| `not_scored_consultation_or_planned` | The FCA material is a consultation or a stated plan to consult. Absence is not scored. |

Every row has `accepted_as_gap: false`. Stages are `in_force_expectation`, `final_not_yet_in_force`, `consultation`, and `planned_consultation`. A sentence in a policy cannot promote a consultation to final.

The sources and currency table is in the JSON under `sources_and_currency`. Each source has a `last_verified` date. If that date is older than the threshold (default 90 days) relative to `--as-of`, the source is `stale` and any row that cites it is marked `do_not_rely_until_sources_reverified`. The checker does not refresh the page.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/04-fca-cryptoasset-readiness
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/gap_register.py --pack examples/harbourline --as-of 2026-10-24
python src/gap_register.py --sources --as-of 2026-10-24
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic and the checker is the code under `src/`. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running. It is not a model score. A live Microsoft Foundry run has not been done.

A stale-data check, without editing the catalogue:

```bash
python src/gap_register.py --pack examples/harbourline --as-of 2027-04-01 --stale-after-days 90
```

The exit code is 0 when the JSON is produced, including when phrases are missing or a source is stale. A missing phrase is not a failed run, and it is not a readiness result.

## Sample

Harbourline Markets Ltd is a fictional custodian. The sample pack is missing a risk warning in the promotions policy and does not claim to issue stablecoins. The register still has no readiness field set. The stablecoin backing-asset row is `not_indicated_in_the_text`. See `examples/sample_output.json`.

## Sources and currency

Pinned on **24 October 2026**. The checker does not download these pages. Re-check them before anyone relies on a row. Threshold used by the tests: older than 90 days from `last_verified`.

| ID | Page | Page last updated | Last verified | Body opened |
|---|---|---|---|---|
| `fca-regime-overview` | [Overview of the cryptoassets regime policy statements](https://www.fca.org.uk/publications/policy-statements/cryptoasset-regime) | 30 June 2026 | 24 October 2026 | Yes |
| `fca-mlr-application` | [What we expect in an application for registration](https://www.fca.org.uk/firms/cryptoassets/application-registration) | 30 June 2026 | 24 October 2026 | Yes |
| `fca-gateway` | [How the gateway will operate](https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/how-gateway-will-operate) | 30 September 2026 | 24 October 2026 | Yes |
| `fca-what-you-need-to-do` | [What you need to do](https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/what-you-need-to-do) | 16 September 2026 | 24 October 2026 | Yes |
| `fca-regime-landing` | [A new regime for cryptoasset regulation](https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation) | 30 September 2026 | 24 October 2026 | Yes |
| `fca-ps26-18` | [PS26/18 Cryptoasset perimeter guidance](https://www.fca.org.uk/publications/policy-statements/ps26-18-cryptoasset-perimeter-guidance) | 16 September 2026 | 24 October 2026 | Yes. The PDF linked from the page was not opened. |
| `fca-travel-rule` | [Travel Rule expectations](https://www.fca.org.uk/news/statements/fca-sets-out-expectations-uk-cryptoasset-businesses-complying-travel-rule) | 6 February 2026 | 24 October 2026 | Yes |
| `fca-marketing` | [Marketing to UK consumers](https://www.fca.org.uk/firms/cryptoassets/marketing-uk-consumers) | 6 February 2026 | 24 October 2026 | Yes |

Handbook sourcebooks are cited only where one of those pages names them. CRYPTO 2 to CRYPTO 10, CASS 7, CASS 16, CASS 17, COREPRU and CRYPTOPRU are names on the 30 June 2026 overview. This starter did not open the Handbook or the policy-statement PDFs. PS23/6 and FG23/3 are named on the marketing page and were not opened. GC26/4 and GC26/5 are guidance consultations named on the overview.

## Limitations

- Observations are phrase checks. A policy can contain the words and still be a poor control. A policy can meet the expectation without using these words. The Compliance Officer or MLRO decides.
- The June 2026 overview and the September 2026 gateway page do not use the same sentences about firms that apply after the window. The gateway page distinguishes the saving provision from the transitional provision. The overview says a firm that applies after the window may not be able to rely on "these provisions". This checker does not reconcile those sentences.
- The marketing page, last updated 6 February 2026, still says legislation on the financial-promotions gateway "is currently making its way through Parliament", and it points to GC23/2 as a guidance consultation. Later pages were not used to overwrite that sentence. The s.21 approvers page named by the gateway was not opened.
- Financial Crime Guide updates, DeFi guidance, and resolution rules are plans to consult, on the 30 June 2026 overview ("later this year"). This starter did not verify that a consultation paper has since been published. PS26/18 says the FCA plans to consult on further perimeter guidance in late 2026. That row stays a planned consultation.
- SM&CR is named in the overview as part of applying the Handbook (PS26/13). The MLR registration page says that registering under the MLRs does not of itself subject the firm to SM&CR. Both sentences are in the row. The checker does not collapse them.
- FG26/5 (Consumer Duty) and FG26/6 (operational resilience) are named, not opened. No Handbook paragraph is encoded from them.
- JMLSG Travel Rule guidance is mentioned on the FCA statement and is not an FCA page. It is not in the catalogue.
- `eval/smoke_report.json` is a deterministic smoke test. It is not a model score.

This is not legal advice and it is not a statement of any firm's compliance.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness (lead): [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness (lighter intake): [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Azure boundary: [docs/azure.md](docs/azure.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/04-fca-cryptoasset-readiness/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
├── skills/
├── copilot-studio/
├── docs/
├── eval/
├── examples/
└── tests/
```

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
