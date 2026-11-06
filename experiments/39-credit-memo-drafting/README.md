# Experiment 39: Credit memo drafting

Catalogue ID **B009**. Autonomy **A1**. The catalogue checkpoint is "Credit officer owns recommendation and approval". Stack in the catalogue: Microsoft Foundry and Fabric. What you can run today is Python in the standard library. It calls Experiment 12, the number and date check in Experiment 29, and Experiment 36 when the pack supplies a comparisons object. It does not call a model and it does not call the network.

A credit officer supplies one synthetic pack and an as-of date. The agent returns a draft with a closed set of sections: company profile, financial highlights, limit request, security, covenants, risk flags, and information gaps. Every stated figure and claim is a copy of named lines, with a pinpoint citation: document id, page, paragraph, and line. A section with no usable current paragraph is **not stated**. It is not inferred. `credit_decision`, `recommendation`, and `limit_set` stay null. The agent does not contact the customer or a bureau, does not post to a core banking or CRM system, and does not file a SAR.

Samples are synthetic. Mereholt Components Ltd is fictional. It is not a lender, an invoice-finance house, a trade-credit insurer, or a real company. No real person and no real facility is in the file.

## How this differs from Experiment 12, Experiment 16, Experiment 36, and Experiment 37

**Experiment 12** inventories text files. It has no credit purpose, and this folder does not add one. This experiment calls `intake()` with no purpose, so nothing is routed and nothing is queued. A file that was not read, is outside the date window, or has a deterministic identifier finding is not quoted.

**Experiment 16** drafts a Money Laundering Regulations checklist. This experiment mirrors that checklist shape: a status, `sufficient` false, and `decides_the_credit` false. It does not import Experiment 16. That package lives under the module name `src`, which would collide with this one. Regulation 28 was not re-opened here. The checklist does not decide that a duty is met, and it does not onboard anyone.

**Experiment 36** classifies the same fact across sources. This experiment calls `compare()` when the pack includes a `comparisons` object. It does not choose a source, query a bureau, or edit a record. Comparison counts stay on `cross_source`. They are not added to `stated_fact_count`. No comparisons object is not a finding that the sources agree.

**Experiment 37** copies a contiguous span and checks a pinpoint. This experiment uses that same rule for memo sections. It does not import Experiment 37, for the same module-name reason. It does not decide coverage or price, and it does not decide credit.

## The problem

UK lenders, invoice-finance houses, trade-credit insurers, and corporate credit teams prepare a credit memo from financials, a pasted bureau extract, and internal notes. A sentence that is not tied to a line is hard to check. A sentence that fills a gap the pack left open is worse, because it looks like the file said it.

This starter is the check. It is extractive. It copies lines. It does not write a fluent credit opinion. The recommendation and every approval stay with the credit officer. The draft is not for use until that officer has approved it, and that approval is outside this agent. `draft_approved_for_use` stays false.

## Who it helps

**The credit officer.** They see each stated figure, the document, the page, the paragraph, and the lines, and they see which sections are not stated. They decide the recommendation, any approval or decline, and any limit. The draft does not tell them to approve or decline.

**The MLRO.** A financial-crime phrase in a cited risk flag is narrative for that person. The agent does not decide suspicion and does not file a SAR.

**A colleague preparing the reading.** They can see a missing-information checklist without the tool contacting the customer or a bureau. A gap is not an enquiry.

## Non-goals

- Approving, declining, or recommending credit. `credit_decision` and `recommendation` stay null.
- Setting a limit, a facility, or a price. `limit_set` stays null. A requested figure in the pack is not a limit the agent sets.
- Deciding that the Consumer Duty or PRIN 2A was met, or that the firm is in retail market business. PRIN 3 was not opened. The glossary definition of a retail customer was not opened.
- Deciding that the Equality Act 2010 was contravened. Schedule 3 was not opened.
- Applying an Article 9 condition, or taking a solely automated credit decision. Article 22 was shown as omitted on 6 November 2026.
- Contacting the customer or a credit bureau.
- Posting to a core banking system, a CRM, Dataverse, or SharePoint.
- Writing a Microsoft Fabric lakehouse, warehouse, or report. A Fabric product page was not opened.
- Filing a SAR, making an authorised disclosure, or producing customer text. The MLRO decides. Section 333A was not opened, so tipping-off wording is not quoted.
- Treating the memo as the decision. `summary_accepted_as_decision` stays false. `draft_approved_for_use` stays false. `solely_automated_decision` stays false.
- Inferring a figure that is not a contiguous copy of cited lines. The value is **not stated**.
- Reading a PDF, an image, or a scan. The caller pastes text that is already split into pages, paragraphs, and lines.
- Calling Microsoft Foundry. That is a deployment option in the Foundry note. It is not called.
- Autonomy A3. There is no path on which the agent decides the credit.
- Releasing the smoke test as a pass or fail for a live model. `release_evaluation` always raises.

## What the drafter does

`src/draft.py` reads one JSON pack and writes one JSON document. The same pack, the same as-of date, and the same window produce the same JSON. The label is **DRAFT FOR THE CREDIT OFFICER. NOT A CREDIT DECISION AND NOT A LIMIT.**

**Product label.** The caller may set `commercial_non_consumer`, `retail`, or `sme_consumer_facing`. Any other string is `unrecognised`. A missing label is `not_stated`. The agent does not decide the label. `product_label_decided_by_agent` stays false. A retail or SME label shows the PRIN 2A note and does not find that the Duty was met. A commercial label does not apply that note as if the Duty covered the pack. The SME label is not a decision that the applicant is a retail customer. That glossary was not opened.

**Intake.** Every file goes through Experiment 12. No purpose is requested. A file outside the window, not read, or with a deterministic identifier finding is listed in `not_used` and is not quoted. `output_is_anonymised` stays false.

**Extract.** Each stated fact is the text of one contiguous paragraph whose `fact_key` is in the closed list, from a document Experiment 12 read and whose review date is inside the window. A paragraph that contains an instruction, or wording that would approve, decline, set a limit, contact, post, or file a SAR, is not copied. A refusal such as "Do not approve the facility." is not treated as that wording.

**Several lines in one section.** Security, covenants, risk flags, and information gaps may hold more than one cited line. Those lines are a list. Company profile, financial highlights, and the limit request are single-value sections. Two different current texts in a single-value section are both shown. `chosen_value` stays null. That is not a limit and not a recommendation.

**Comparison.** When the pack has a `comparisons` object, Experiment 36 classifies the fields the caller listed. On the sample, turnover of GBP 4200000 and GBP 4,200,000.00 is an immaterial formatting difference. A facility request of GBP 250000 against GBP 180000 is a material discrepancy. The agent does not choose. `occurrence_count` is not part of `fact_count`, and neither count is added to the memo's `stated_fact_count`.

**Checklist.** The shape follows Experiment 16: an id, a status, `sufficient` false, and `decides_the_credit` false. A current cited line is `evidenced`. A section that exists only on a stale document is `evidenced_but_stale` and is still **not stated** in the memo. A section with no paragraph is `missing`.

**Checker.** Every shown fact receives one verdict, in this order: missing citation, incomplete pinpoint, document not in the pack, pinpoint not in the document, prohibited wording, an instruction, a withheld identifier, a stale or unread document, a number or ISO date that is not in the cited lines, then a span that does not contain the fact. The first failure is the verdict. Later failures are `other_failures`. They are not added to `failure_count`. `verdict_total` equals `stated_fact_count`.

`checker_passed` is true when no shown fact failed. It can be true while `do_not_rely` is also true, because a gap, a contradiction, a stale document, a material discrepancy, an equality theme, or a financial-crime phrase is a reason not to rely on the draft as a complete picture. `checker_passed` is not an approval.

**Human step, outside `draft_memo()`.** `record_credit_officer_review` accepts only the role "Credit officer". Every shown fact and every gap must be in the review. It can set `reading_acknowledged`. It cannot set a credit decision, a limit, a contact, a post, or a SAR, and it cannot set `draft_approved_for_use`. The skills say the agent must not call this function. The command line does not expose it. `approve_credit`, `decline_credit`, `set_limit`, `contact_customer`, `contact_bureau`, `post_core_banking`, `post_crm`, `file_sar`, and `release_evaluation` raise `MemoForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 12, 08, 29, and 36 need to be beside this folder, which they are in this repository.

```bash
cd experiments/39-credit-memo-drafting
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/draft.py --pack examples/sample_pack.json --as-of 2026-11-06
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score, not an LLM-as-judge, not a Foundry score, and not a credit decision. The summary counts 12 cases once. Fact counts stay on each case. On the as-of date 6 November 2026 the agreement with the labelled expectations is 100.0, which means the checker matched its own rules. The two Mereholt cases each have 9 stated facts. Those figures are not added together. 18 is not a summary total. The comparison `fact_count` of 2 is not added to 9.

The sample is Mereholt Components Ltd, which is fictional, labelled `sme_consumer_facing` by the caller. Nine facts are supported. Covenants are not stated. An old extract is not used. The two turnover sentences are both shown, and the currency comparison classes the field values as immaterial. The two facility figures are a material discrepancy. A risk flag mentions an unusual payment narrative, for the MLRO, and the director's age, as an equality theme. `checker_passed` is true. `do_not_rely` is true. `credit_decision` is null. See `examples/sample_output.json`.

A stale-pin check, without editing the checker:

```bash
python src/draft.py --pack examples/sample_pack.json --as-of 2027-02-10 --stale-after-days 90
```

On that date the sample documents are also outside the 90-day window, so the extract does not quote them. The sections are not stated. The figures are not invented.

Passing `--approve`, `--decline`, `--set-limit`, `--contact-customer`, `--contact-bureau`, `--post-core`, `--post-crm`, or `--file-sar` is a mistake. The command exits and does not write a file.

The exit code is 0 when a draft is produced, including when the checker fails a fact or a source is stale. That is not an approval and it is not a limit.

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
| CI secret check | `.github/workflows/experiment-39-tests.yml`. |
| CI licence check | The same workflow. MIT, and this README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library and the sibling experiments. |

## Limitations

- **The checker is extractive.** A true paraphrase fails. A sentence that copies its lines can still mislead by what it leaves out. Residual risk R3 is High. `checker_passed` does not mean the credit should be approved.
- **The section list is closed.** A point the caller cares about that is not one of the seven sections is invisible. That is a limit of this starter, not evidence that the pack is silent.
- **Text that is already split into lines.** PDFs, images, and scans are not read. A line boundary the caller drew is trusted.
- **The starter does not search a core system or a bureau.** Items that were never pasted are invisible. A `register_extract` kind on the comparison object is the caller's label for a paste. `register_queried` stays false.
- **Stale files are left out of the extract.** The window, default 90 days, is not a statutory period. The day the window ends is still current. The next day is stale.
- **The injection list is closed.** A phrase that is not on it is not detected. A refusal sentence is not treated as an instruction.
- **Single-value contradictions are not resolved.** Two different current texts are both shown. `chosen_value` stays null.
- **Article 5, Article 9, and Articles 22A to 22D were read on 6 November 2026.** Article 22 was shown as omitted. No Article 9 condition is applied. Data Protection Act 2018 section 10 was not opened. This starter does not certify meaningful human involvement.
- **Equality Act 2010 sections 4, 13, 19, and 29 were read.** Section 19(3) does not list pregnancy and maternity. Schedule 3 was not opened. A theme word is not a finding. The word list can miss a paraphrase and can match a word that is not about the applicant.
- **PRIN 2A.1 was read.** PRIN 2A.2 was requested and the rule text was not returned, so the cross-cutting obligations are not quoted. PRIN 3 and FG22/5 were not opened. The retail-customer glossary, including any SME limb, was not opened.
- **Money Laundering Regulations 2017 regulation 21(3) and 21(5) were read.** Regulation 28 was not re-opened. JMLSG guidance was not opened.
- **Proceeds of Crime Act 2002 sections 330, 331, and 338 were read.** Schedule 9 was not opened, so this starter does not decide that a firm is in the regulated sector. Section 333A was not opened.
- **Microsoft Foundry and Microsoft Fabric product pages were not opened.** Both are unverified here. Neither is called.
- **The caller name is not a cited fact** unless it appears inside a cited company-profile line. If it does not, `caller_label_differs_from_cited_name` is true. The label is not copied into that field.
- **A hand-edited JSON is not a control.** `record_credit_officer_review` trusts the verdicts already on the draft. It does not re-read the pack. The agent cannot call it.
- **The smoke test is not a model score.** Agreement 100.0 means the checker matched the expectations written for its own rules.

This is not legal advice, a DPIA, a credit opinion, or a statement that a deployment is compliant. Drafting a memo can omit the line that changes the picture. The credit officer has to read the sources. The manifest does not assert an Article 6 basis. The adopting firm confirms its own.

## Two Copilot Studio harnesses

Both call `draft_memo()` and stop. Neither harness approves or declines, sets a limit, contacts the customer or a bureau, posts a system, or files a SAR. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The credit officer pastes a pack and the as-of date, the flow returns JSON, the topic stops. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for a credit officer who wants the draft explained in steps. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft's harness overview, opened 6 November 2026, says agents and workflows on that harness use Copilot Credits. The billing page linked from that overview was not opened. Prices were not copied. The overview did not mark the harness itself as preview. The generative-orchestration guidance opened the same day says the planner can invoke a topic when its described purpose matches the need, and also by trigger phrases, and that names carry more weight than descriptions. It does not describe numeric routing weights. These skills do not list trigger phrases and do not assign routing weights. Whether that planner is the GitHub Copilot harness selector was not stated on the harness overview. That link is unverified.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry and Fabric: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.

## Project structure

```
experiments/39-credit-memo-drafting/
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

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5). Principles, including lawfulness, fairness, transparency, data minimisation, and accuracy. Article 5(3) was inserted by the Data (Use and Access) Act 2025.
- [UK GDPR Article 9](https://www.legislation.gov.uk/eur/2016/679/article/9). Article 9(1) prohibits the special categories it lists unless a condition applies. No condition is applied here.
- [UK GDPR Article 22](https://www.legislation.gov.uk/eur/2016/679/article/22). Shown as omitted. Substituted by Chapter 3 Section 4A.
- [UK GDPR Article 22A](https://www.legislation.gov.uk/eur/2016/679/article/22A). A decision is based solely on automated processing if there is no meaningful human involvement.
- [UK GDPR Article 22B](https://www.legislation.gov.uk/eur/2016/679/article/22B). Paragraphs 1 to 4 were read, including the explicit-consent condition in paragraph 2.
- [UK GDPR Article 22C](https://www.legislation.gov.uk/eur/2016/679/article/22C). Safeguards in paragraph 2. This starter does not take the decision, so it does not provide them.
- [UK GDPR Article 22D](https://www.legislation.gov.uk/eur/2016/679/article/22D). A power to make regulations. No such regulations were opened.
- [Equality Act 2010, section 4](https://www.legislation.gov.uk/ukpga/2010/15/section/4). The protected characteristics.
- [Equality Act 2010, section 13](https://www.legislation.gov.uk/ukpga/2010/15/section/13). Direct discrimination. Section 13(1) was read. Section 13(2) is not applied.
- [Equality Act 2010, section 19](https://www.legislation.gov.uk/ukpga/2010/15/section/19). Indirect discrimination. Section 19(3) omits pregnancy and maternity.
- [Equality Act 2010, section 29](https://www.legislation.gov.uk/ukpga/2010/15/section/29). Services. Section 29(1) and 29(2) were read. The page said the section is up to date with all changes known to be in force on or before 5 November 2026.
- [FCA Handbook, PRIN 2A.1](https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html). The Consumer Duty applies to a firm's retail market business. The application is set out in PRIN 3, which was not opened.
- [Money Laundering Regulations 2017, regulation 21](https://www.legislation.gov.uk/uksi/2017/692/regulation/21). Regulation 21(3) and 21(5).
- [Proceeds of Crime Act 2002, section 330](https://www.legislation.gov.uk/ukpga/2002/29/section/330). Failure to disclose in the regulated sector. The page said the section is up to date with all changes known to be in force on or before 6 November 2026.
- [Proceeds of Crime Act 2002, section 331](https://www.legislation.gov.uk/ukpga/2002/29/section/331). Nominated officers.
- [Proceeds of Crime Act 2002, section 338](https://www.legislation.gov.uk/ukpga/2002/29/section/338). Authorised disclosures. This starter does not make one.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).
- [Generative orchestration guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration).

PRIN 2A.2 was requested on 6 November 2026 and the rule text was not returned. A Foundry product page was not opened. A Fabric product page was not opened. Billing pages linked from the harness overview were not opened. FG22/5, PRIN 3, Equality Act Schedule 3, Proceeds of Crime Act section 333A, and Schedule 9 were not opened.

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
