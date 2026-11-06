# Experiment 38: Policy wording comparison

Catalogue ID **B008**. Autonomy **A0**. The catalogue checkpoint is "Specialist validates interpretation". Stack in the task: Copilot Studio on the GitHub Copilot harness, plus Azure Document Intelligence as a documented option. What you can run today is Python in the standard library. It calls Experiment 12, Experiment 33, and Experiment 29, in process. It does not call a model, Document Intelligence, or the network.

A wording specialist supplies two or more synthetic policy wordings and an as-of date. The agent returns a draft comparison of a closed topic list: coverage grants, exclusions, conditions, warranties, definitions, limits, deductibles, and notice provisions. Every stated clause is a copy of named lines, with a pinpoint citation: wording id, document id, clause reference, page, paragraph, and line. A topic and subject that one wording states and another does not is **not stated**. It is not inferred. `favourable_to`, `recommendation`, `endorsement_draft`, and `coverage_decision` stay null. The agent does not contact the broker and does not write to a policy administration system.

Samples are synthetic. Northfen Wharf Ltd is fictional. It is not an insurer, a Lloyd's syndicate, an MGA, or a broker. No real person and no real wording is in the file.

## How this differs from Experiment 36, Experiment 37, Experiment 33, Experiment 12, and Experiment 29

**Experiment 36** classifies one fact across documents as a match, an immaterial difference, or a material discrepancy. A reviewer resolves each material row. This experiment uses that shape for policy clauses: a fixed class, citations, and a human gate. The class here is textual. `not_stated_in_one` means a caller-supplied subject is present in one wording and absent from another. `text_differs` means the normalised clause text is not the same. Neither class says which wording is right or more favourable. This folder does not import Experiment 36.

**Experiment 37** copies lines from one submission into a closed field list, and a missing field is not stated. This experiment uses that citation style across two or more wordings. It does not import Experiment 37. It does not price a risk.

**Experiment 33** supplies `resolve_span` and `normalise`. After case and whitespace are folded, the quote has to be a contiguous part of the cited lines. A paraphrase fails. This experiment calls those functions. It does not summarise a case bundle.

**Experiment 12** inventories the text files. It has no policy-wording purpose, and this folder does not add one. This experiment calls `intake()` with no purpose, so nothing is routed. A file that was not read, is outside the date window, or has a deterministic identifier finding is not quoted.

**Experiment 29** is called only for the number and date boundary check. Its token-overlap verdict is not used. There is no threshold and no release.

## The problem

UK general insurance and specialty markets, including Lloyd's, MGAs, brokers, and insurers, compare wordings, endorsements, and schedules at renewal and across competing quotes. A sentence that is not tied to a clause is hard to check. A sentence that fills a gap one wording left open is worse, because it looks as if that wording said it.

This starter is the check. It is extractive. It copies clauses. It does not write a coverage opinion.

No Lloyd's byelaw was opened. None is applied. No syndicate is named.

## Who it helps

**The wording specialist.** They see each stated clause, the clause reference, and which wordings do not state that subject. They validate the interpretation. The draft does not tell them which wording to prefer.

**A colleague preparing that reading.** They can see the side-by-side difference without the tool contacting the broker or drafting an endorsement.

**A reviewer comparing this pattern with cross-source validation, a submission summary, or a case-bundle summary.** The differences are in the section above.

## Non-goals

- Interpreting favourability for the insured or the insurer. `favourable_to` stays null. Section 69 of the Consumer Rights Act 2015 is not applied.
- Recommending buy, sell, or renew. `recommendation` stays null.
- Drafting a binding endorsement. `endorsement_draft` stays null.
- Contacting a broker, the insured, or a coverholder.
- Writing a policy administration system, a bordereau, Dataverse, or SharePoint. Binding cover.
- Deciding that Insurance Act 2015 section 3, section 9, section 10, section 11, section 16, or section 17 was met or breached.
- Deciding that a term is unfair under Consumer Rights Act 2015 section 62, or that it is transparent under section 64(3) or section 68.
- Deciding that a firm met PRIN 2A.5, or that the firm is in retail market business.
- Treating the comparison as the decision. `solely_automated_decision` stays false. `downstream_use_permitted` stays false.
- Inferring a clause that is not a contiguous copy of cited lines. The value is **not stated**.
- Reading a PDF, an image, or a scan. The caller pastes text that is already split into pages, paragraphs, and lines.
- Calling Azure Document Intelligence or Microsoft Foundry. Those are deployment notes. They are not called.
- Autonomy A3. There is no path on which the agent decides the wording.
- Releasing the smoke test as a pass or fail for a live model. `release_evaluation` always raises.

## What the comparison does

`src/compare.py` reads one JSON pack and writes one JSON document. The label is **DRAFT FOR THE WORDING SPECIALIST. NOT A COVERAGE OPINION AND NOT A RECOMMENDATION.**

**Market label.** The caller may set `commercial_non_consumer` or `retail`. Any other string is `unrecognised`. A missing label is `not_stated`. The agent does not decide the label. A commercial label shows the Insurance Act 2015 notes. A retail label shows the Consumer Rights Act 2015 and PRIN 2A.5 notes. Neither note is a finding.

**Alignment.** The caller supplies `topic` from the closed list and a `subject` key. The agent does not invent the subject from the prose. A paragraph with no topic, or with a topic outside the list, is unaligned. It is cited and it is not matched to another wording's clause.

**Difference class.** `same_text`, `text_differs`, `not_stated_in_one`, or `unresolved`. Material means the class is not `same_text`. `amounts_differ` records that the digit runs are not the same. It does not say which limit is better. `words_only_in` lists tokens that are not shared. No wording is the baseline. `baseline_wording` stays null.

**Checker.** Every stated quote receives one verdict. Later failures are `other_failures` and are not added to `failure_count`. `verdict_total` equals `stated_cell_count`. Not-stated cells, unaligned clauses, and unused documents have their own counts.

`checker_passed` is true when no stated quote failed. It can be true while `do_not_rely` is also true, because the specialist has not validated the draft, or because a topic is not stated, a document was unused, or a pin is stale.

**Human step, outside `compare()`.** `record_specialist_review` accepts only the role "Wording specialist". Every row and every unaligned clause must be in the review. It can set `interpretation_acknowledged`. It cannot set favourability, a recommendation, or an endorsement. The skills say the agent must not call this function. The command line does not expose it.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 12, 08, 33, and 29 need to be beside this folder, which they are in this repository.

```bash
cd experiments/38-policy-wording-comparison
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/compare.py --pack examples/sample_pack.json --as-of 2026-11-06
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score, not an LLM-as-judge, not a Foundry score, and not a coverage opinion. The summary counts 12 cases once. Cell counts stay on each case. On the as-of date 6 November 2026 the agreement with the labelled expectations is 100.0, which means the checker matched its own rules. The two Northfen cases each have 15 stated cells. Those figures are not added together. 30 is not a summary total.

The sample is Northfen Wharf Ltd, which is fictional, labelled `commercial_non_consumer` by the caller. Eight rows. Fifteen stated cells are supported. The renewal wording does not state the flood exclusion. The buildings limits differ. An old endorsement is not used. A transit sentence has no topic key, so it is unaligned. `checker_passed` is true. `do_not_rely` is true. `favourable_to` is null. See `examples/sample_output.json`.

A stale-pin check, without editing the checker:

```bash
python src/compare.py --pack examples/sample_pack.json --as-of 2027-05-06 --stale-after-days 90
```

Passing `--favourable`, `--recommend`, `--draft-endorsement`, `--contact-broker`, `--write-pas`, or `--decide-coverage` is a mistake. The command exits and does not write a file.

The exit code is 0 when a draft is produced, including when the checker fails a quote or a source is stale. That is not a recommendation.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. The description is one line and says when to use the skill. |
| Synthetic fixtures | `examples/`, `eval/synthetic_dataset.json`, and the tests. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Permissions manifest | `permissions.yaml`, the same file as `agent-manifest.yaml`, validated against `schemas/agent-manifest.schema.json`. Experiment 03's generator is not called. The schema is the same one that generator validates. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| Evaluation set and scorer | `eval/synthetic_dataset.json` and `eval/evaluate.py`. |
| CI secret check | `.github/workflows/experiment-38-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library and the sibling experiments. |

## Limitations

- **The checker is extractive.** A true paraphrase fails. A sentence that copies its lines can still mislead by what it leaves out. Residual risk R3 is High. `checker_passed` does not mean the wordings have the same legal effect.
- **The topic list is closed.** A clause the caller cares about that is not one of the eight topics stays unaligned if the topic key is missing. That is a limit of this starter, not evidence that the wording is silent.
- **The subject key is the caller's.** Two clauses about flood are compared only when both paragraphs carry the subject `flood`. The agent does not read the word "flood" and invent the key.
- **Text that is already split into lines.** PDFs, images, and scans are not read. A line boundary the caller drew is trusted. A bad split produces a bad citation. Document Intelligence is not called.
- **The starter does not search a broker portal or a policy system.** Clauses that were never pasted are invisible.
- **Stale files are left out of the extract.** The window, default 90 days, is not a statutory period and not a Lloyd's deadline. A wording whose documents were all refused is `not_quoted`, which is not a finding that the topic is absent.
- **The injection list is closed.** A phrase that is not on it is not detected by this experiment. Experiment 12's scanner does not skip a refusal sentence. A refusal sentence can therefore be flagged by intake and still be quoted when this experiment's own list skips it.
- **Material is a textual label.** It is not legal materiality under the Insurance Act 2015. `words_only_in` is a token difference, including ordinary words such as "the".
- **Section 17 was read on 6 November 2026.** Subsection (3) requires a disadvantageous term to be clear and unambiguous as to its effect. This starter does not decide that a term is disadvantageous. Section 16A, named in the section 17 amendment note, was not opened.
- **Section 9 was read.** Words such as "basis of the contract" can be flagged on a supported quote. `basis_clause_of_no_effect` stays null.
- **Consumer insurance disclosure was not opened.** The Consumer Insurance (Disclosure and Representations) Act 2012 was not opened.
- **PRIN 2A.5 was opened on 6 November 2026.** The page is the consumer understanding outcome and refers to the duty to support understanding as PRIN 2A.5.3R(1). PRIN 2A.1 was requested the same day and returned only the FCA office address, so it is not quoted from this experiment. PRIN 2A.2 was not opened.
- **Article 22B paragraph 2 was not in the text returned on 6 November 2026.** It is not quoted. The Data (Use and Access) Act 2025 section 80 page was not opened. The article pages cite section 80(1) and S.I. 2026/82.
- **Schedule 2 to the Consumer Rights Act 2015 was not opened.** No term is marked unfair.
- **No Lloyd's rule is applied.** The market is named as an audience. A byelaw page was not opened.
- **The caller organisation label is not a cited fact.**
- **A hand-edited JSON is not a control.** `record_specialist_review` trusts the verdicts already on the draft. It does not re-read the wordings. The agent cannot call it.
- **The smoke test is not a model score.** Agreement 100.0 means the checker matched the expectations written for its own rules.

This is not legal advice, a DPIA, a coverage opinion, or a statement that a deployment is compliant. Comparing wordings can omit the clause that changes the cover. The specialist has to read the sources. The manifest does not assert an Article 6 basis. The adopting firm confirms its own.

## Two Copilot Studio harnesses

Both call `compare()` and stop. Neither harness ranks a wording, drafts an endorsement, contacts the broker, or writes a system. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The specialist pastes a pack and the as-of date, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a specialist who wants the draft explained in steps. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft's harness overview, opened 6 November 2026, says agents and workflows on that harness use Copilot Credits. The billing page linked from that overview was not opened. Prices were not copied. The overview did not mark the harness itself as preview. The generative-orchestration guidance opened the same day says the planner can invoke a topic when its described purpose matches the need, and also by trigger phrases, and that tool names carry more weight than descriptions. These skills do not list trigger phrases and do not assign routing weights. Whether that planner is the GitHub Copilot harness selector was not stated on the harness overview. That link is unverified.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry and Document Intelligence: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.

## Project structure

```
experiments/38-policy-wording-comparison/
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

## References opened on 6 November 2026

- [Insurance Act 2015, section 2](https://www.legislation.gov.uk/ukpga/2015/4/section/2). Section 2(1): this Part applies to non-consumer insurance contracts only.
- [Insurance Act 2015, section 3](https://www.legislation.gov.uk/ukpga/2015/4/section/3). The duty of fair presentation, including section 3(3)(b) and section 3(4).
- [Insurance Act 2015, section 9](https://www.legislation.gov.uk/ukpga/2015/4/section/9). A representation is not capable of being converted into a warranty by a basis clause.
- [Insurance Act 2015, section 10](https://www.legislation.gov.uk/ukpga/2015/4/section/10). Breach of warranty.
- [Insurance Act 2015, section 11](https://www.legislation.gov.uk/ukpga/2015/4/section/11). Terms not relevant to the actual loss.
- [Insurance Act 2015, section 16](https://www.legislation.gov.uk/ukpga/2015/4/section/16). Contracting out of non-consumer contracts.
- [Insurance Act 2015, section 17](https://www.legislation.gov.uk/ukpga/2015/4/section/17). The transparency requirements. Section 16A was not opened.
- [Consumer Rights Act 2015, section 61](https://www.legislation.gov.uk/ukpga/2015/15/section/61). Part 2 applies to a contract between a trader and a consumer.
- [Consumer Rights Act 2015, section 62](https://www.legislation.gov.uk/ukpga/2015/15/section/62). Unfair terms.
- [Consumer Rights Act 2015, section 64](https://www.legislation.gov.uk/ukpga/2015/15/section/64). Section 64(3) defines a transparent term. Schedule 2 was not opened.
- [Consumer Rights Act 2015, section 68](https://www.legislation.gov.uk/ukpga/2015/15/section/68). Written terms must be transparent.
- [Consumer Rights Act 2015, section 69](https://www.legislation.gov.uk/ukpga/2015/15/section/69). Not applied. `favourable_to` stays null.
- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5).
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22). Shown as omitted.
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A), [Article 22B](https://www.legislation.gov.uk/eur/2016/679/article/22B), [Article 22C](https://www.legislation.gov.uk/eur/2016/679/article/22C), and [Article 22D](https://www.legislation.gov.uk/eur/2016/679/article/22D). Paragraph 2 of Article 22B was not in the returned text.
- [FCA Handbook, PRIN 2A.5](https://handbook.fca.org.uk/handbook/PRIN/2A/5.html). Consumer understanding. PRIN 2A.1 was not re-read successfully on this date.
- [Azure Document Intelligence in Foundry Tools](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0). Not called. No wording-comparison model was named.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).
- [Generative orchestration guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration).

A Microsoft Foundry agent page was not opened. Billing pages linked from the harness overview were not opened. The Data (Use and Access) Act 2025 section 80 page was not opened. The article pages cite it.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
