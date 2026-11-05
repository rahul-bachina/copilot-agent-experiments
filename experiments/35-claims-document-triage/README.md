# Experiment 35: Claims Document Triage Agent

Catalogue ID **B007**. A claims handler's reading of one synthetic first notification of loss, with invoices, a report, and a policy-wording extract. Stack in the catalogue: Copilot Studio and AI Builder. This folder also documents a Microsoft Foundry option that is not called. Autonomy **A1**. The claims handler approves the classification.

It calls [Experiment 12](../12-document-intake/) (O001) with purpose `claims_fnol`. That intake calls [Experiment 08](../08-uk-pii-redaction-gateway/) (O005). Faithfulness uses [Experiment 29](../29-groundedness-evaluation/) `score_claim`. The checklist shape follows [Experiment 16](../16-kyc-evidence-intake/): one pack in, one draft out, prohibited paths raise. This experiment does not ship a second inventory, a second redactor, or a second groundedness checker.

**Status.** Available as a local starter. The draft runs in Python with no Azure credentials and no network. It is not an importable Copilot Studio solution, and a live model has not been scored.

The agent never accepts, declines, or settles a claim. It never tells a customer anything. It never writes to a claims system, including after the handler records a class. An inconsistency line is a prompt for a person to check. It is not a finding, and it is not a statement about the policyholder's conduct.

Samples are synthetic. The firm is fictional (Reedmarsh General). The policyholder is Policyholder A. The National Insurance value in one fixture is the non-allocatable example documented in Experiment 08.

## The problem

Claims intake is a pile of documents. A handler needs a short reading that stays inside the files: what the first notification says, which policy words might be relevant, and where two documents do not use the same figure or the same date. Summary quality varies, and a sentence inside an invoice can try to make the tool decline the claim.

The FCA's good and poor practice note of 19 October 2026, case study K, describes a firm that assessed AI-generated claims information for completeness, faithfulness to source information, conciseness, adequacy of reasoning, and safety, combining staff checks with an automated assessment, including LLM-as-a-judge. This starter is the staff-facing draft plus a deterministic scorecard for faithfulness, completeness, and unsupported coverage statements. It is not that firm's system, and it is not an LLM judge.

## Who it helps

**A claims handler.** They see quoted lines, coverage pointers, prompts, and a scorecard. They approve or change the class. Approving the class does not accept the claim.

**An evaluation owner.** They can score a summary someone else wrote, including one that states a coverage outcome the files do not contain. A miss asks a person to look. The thresholds in this starter are not approved.

**A reader of Experiment 12.** That intake names B007 and does not call it. This folder calls the intake. It still does not decide the claim.

It does not help a team that wants the tool to accept, decline, settle, or write to the customer.

## Non-goals

- Accepting, declining, or settling a claim.
- Deciding that a loss is or is not within the policy, or that a figure is the right quantum.
- Producing a fraud indicator, or any statement about the policyholder's conduct. The opportunity note mentioned fraud indicators. A conduct label on an unchecked mismatch is the unfair outcome that note is trying to avoid, so this starter does not emit one.
- Telling the customer anything, including a progress update. ICOBS 8.1.1R(2) is the insurer's duty. This agent has no customer message.
- Writing a claims system, a Dataverse row, or any production record.
- Approving the class from a sentence inside a file.
- Re-implementing Experiment 12, Experiment 08, or Experiment 29.
- Calling Microsoft Foundry, Document Intelligence, or an LLM-as-a-judge.
- Scoring conciseness or adequacy of reasoning. Case study K names them. This checker does not.
- Treating the 90-day freshness window as a claims time limit.
- Autonomy A3.

## What the triage does

`src/triage.py` reads one JSON pack and writes one JSON document. The same pack and the same as-of date produce the same JSON.

**Intake.** Files go to Experiment 12 `intake()` with `requested_purpose` `claims_fnol`. That call hashes each file, suggests a keyword class, previews the O001 checklist, scans for that experiment's injection phrases, flags document dates, and calls Experiment 08. This draft does not copy file bodies. `purpose_confirmed` stays false. Experiment 12 does not call B007. This experiment calls Experiment 12.

**Summary.** Labelled lines are quoted: date of loss, peril, amounts, names, invoice dates, and the policy period. One policy line that contains the peril words is a coverage pointer. The pointer says the handler decides whether the words apply. `coverage_decided` stays false.

**Prompts.** Where two labelled values can be compared and they differ, the draft asks the handler to check. A document date outside the freshness window is the same kind of prompt. `is_a_finding` stays false.

**Class.** A single peril line from a closed list (`escape_of_water`, `storm`, `accidental_damage`, `theft`) is proposed. Anything else is `not_proposed`. `classification_approved_by_handler` stays false until `record_handler_classification` is called with the role "Claims handler". The skills say the agent must not call it. The record still does not accept, decline, settle, tell the customer, or write the claims system.

**Scorecard.** Faithfulness is Experiment 29 `score_claim` on the quoted lines. Completeness is a closed list of labelled lines that were read and not withheld. Unsupported coverage is a closed list of decision phrases that are not a quote from a file this run read. The three results are not added together. A miss sets `human_escalation_required`. That flag does not decline the claim. `threshold_approved_by_evaluation_owner` stays false. `llm_as_judge` stays false.

**Withheld files.** If Experiment 08 reports a deterministic identifier, that file is not quoted. The draft does not say the text was anonymised.

**Prompt injection.** Decline, accept, settle, and "ignore previous instructions" phrases, including inside an HTML comment or split by a zero-width character, are recorded. `followed` is false. A labelled line that carries one is not quoted.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 12, 08, and 29 must sit beside this folder, which they do in this repository.

```bash
cd experiments/35-claims-document-triage
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/triage.py --pack examples/sample_pack.json --as-of 2026-11-05
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score and it is not an LLM-as-a-judge result. On the run checked in with this folder, 13 cases passed and 3 of those cases asked for a person because a supplied summary missed a draft threshold. The case count is not added to the escalation count.

The exit code is 0 when a draft is produced, including when a prompt or an injection phrase is present. A pack that is not marked synthetic is refused. `--accept-claim`, `--decline-claim`, `--settle-claim`, `--tell-customer`, `--write-claims-system`, and `--approve-thresholds` exit 2 and write nothing.

## Limitations

- **Text only.** Whatever Experiment 12 cannot read, this summary cannot quote. `not_read` is a gap. Microsoft Foundry Document Intelligence is not called. See [docs/foundry.md](docs/foundry.md).
- **Labelled lines only.** A date or an amount written in a sentence, rather than after `Date of loss:` or `Invoice total:`, is not extracted. That is a gap, not a clean file.
- **The pointer is not coverage.** Quoting a policy line does not say the loss is within the contract.
- **The scorecard is not case study K.** Conciseness and adequacy of reasoning are not scored. The checker is not an LLM. A paraphrase that uses different words from the file fails faithfulness even when a person would accept the sense. That limit is inherited from Experiment 29.
- **Draft thresholds are not approved.** The default is every quoted line supported, every applicable checklist row met, and no unsupported coverage phrase. An evaluation owner would set real thresholds outside this starter.
- **The 90-day window is not a claims time limit.** It is the same freshness flag Experiment 12 uses.
- **Experiment 08's misses are inherited.** Names, email addresses, and telephone numbers are not detected. A file is withheld only when a deterministic identifier finding is reported. The output is not anonymised.
- **A file over 20,000 characters is not scanned** by Experiment 12. An instruction in it is not detected here either.
- **PRIN 2A.2 paragraph numbers** beside the three cross-cutting rules were not in the text retrieved on 5 November 2026. They are not cited as numbered rules.
- **The smoke test is not a model score.**

This is not legal advice, a Consumer Duty assessment, or a statement that a deployment complies with ICOBS. The manifest does not assert an Article 6 basis. The adopting insurer confirms its own.

## Why a decline is not automated

UK GDPR Article 22, as shown on legislation.gov.uk on 5 November 2026, has no operative text. Textual amendment F1 says Chapter 3 Section 4A was substituted for Article 22, in force on 5 February 2026, by the Data (Use and Access) Act 2025 section 80(1) and S.I. 2026/82 regulation 2(j). Section 80 inserts Articles 22A to 22D.

Article 22A(1), in that section: a decision is based solely on automated processing if there is no meaningful human involvement in the taking of the decision, and it is a significant decision if it produces a legal effect for the data subject or has a similarly significant effect. Article 22C requires safeguards where a significant decision based solely on automated processing is taken: information, representations, human intervention, and a way to contest it.

A decline can be that kind of decision. This starter does not take it. Whether a particular decline meets Article 22A is for the firm's data protection officer. This note is not that determination. Article 22B, which restricts some significant decisions that use special category data, is not applied here because no decision is taken.

## Two Copilot Studio harnesses

Both call `triage()` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness accepts a claim or speaks to a customer. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic for a handler. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution. It is not a customer chat. The Customer Conversation harness is the wrong harness, because this agent does not tell the customer anything.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a handler who wants the draft explained. It is not the GitHub Copilot service. Skills are in [skills/](skills/). The overview, opened 5 November 2026, says agents on that harness use Copilot Credits. Prices were not copied. A last-updated line was not in the text retrieved. The overview did not mark the harness itself as preview.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.
- The intake this experiment calls: [../12-document-intake/](../12-document-intake/).
- The gateway that intake calls: [../08-uk-pii-redaction-gateway/](../08-uk-pii-redaction-gateway/).
- The checker this experiment calls: [../29-groundedness-evaluation/](../29-groundedness-evaluation/).

## Project structure

```
experiments/35-claims-document-triage/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened on 5 November 2026

The operative words are in `src/sources.py`.

- [ICOBS 8.1](https://www.handbook.fca.org.uk/handbook/ICOBS/8/1.html). An insurer must handle claims promptly and fairly; provide reasonable guidance to help a policyholder make a claim and appropriate information on its progress; not unreasonably reject a claim (including by terminating or avoiding a policy); and settle claims promptly once settlement terms are agreed. A point-in-time chapter view dated 21 January 2025 labels those words ICOBS 8.1.1R. The current page's retrieved text did not print "8.1.1" beside the first rule. The next numbered rule on the current page is ICOBS 8.1.2.
- [PRIN 2.1, Principle 12](https://www.handbook.fca.org.uk/handbook/PRIN/2/1.html). "A firm must act to deliver good outcomes for retail customers."
- [PRIN 2A.2](https://www.handbook.fca.org.uk/handbook/PRIN/2A/2.html). A firm must act in good faith towards retail customers. Acting in good faith is a standard of conduct characterised by honesty, fair and open dealing and acting consistently with the reasonable expectations of retail customers. A firm must avoid causing foreseeable harm to retail customers. That section includes ensuring that no aspect of its business involves unfairly exploiting behavioural biases displayed or characteristics of vulnerability held by retail customers. A firm must enable and support retail customers to pursue their financial objectives. The paragraph numbers beside those three rules were not in the text retrieved.
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22). The article text is omitted. See the substitution note above.
- [Data (Use and Access) Act 2025, section 80](https://www.legislation.gov.uk/ukpga/2025/18/section/80). Articles 22A to 22D. The page says there are no known outstanding effects. Commencement on 5 February 2026, in so far as not already in force, is by S.I. 2026/82 regulation 2(j).
- [FCA, AI in financial services: good practice and areas for improvement](https://www.fca.org.uk/publications/good-poor-practice/ai-financial-services). Published 19 October 2026. Last updated 20 October 2026. Case study K.
- [Microsoft Foundry RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators). Groundedness, and Groundedness Pro marked preview. Not called.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview). A last-updated date was not in the text retrieved.

Not opened, and not applied:

- ICOBS 8.1.2 and 8.1.2A, beyond seeing that they follow 8.1.1 on the same page. The fraud exception in the older-contract rule is not applied. This starter does not accuse.
- The billing overview and the standard-harness licensing article linked from the harness overview.
- A separate Learn page on generative orchestration. This folder does not assign a weight to a phrase.
- Entra Agent ID, Conditional Access, Purview, Key Vault, prompt shields, and Application Insights product pages. They are named in the security note as unverified deployment controls.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
