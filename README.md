# Copilot Agent Experiments

A series of small, well-documented AI agent experiments exploring practical applications of Microsoft Copilot, Microsoft Foundry, and Power Platform technologies.

**By [Rahul Bachina](https://github.com/rahul-bachina)** — UK-based Microsoft-stack AI builder specialising in Power Platform, Microsoft Foundry, Copilot Studio, and GitHub Copilot.

## Briefing site

A site for heads of service, complaints and FOI leads, data protection officers, security leads, and architects is built from [`docs-site/`](docs-site/).

Expected address, once an administrator sets GitHub Pages to deploy from GitHub Actions:

<https://rahul-bachina.github.io/copilot-agent-experiments/>

## About This Series

Each experiment in this repository tackles a real-world problem with AI agents, providing:

- 🎯 Clear problem statement and context
- 🏗️ Architecture diagrams and design rationale
- 💻 Working code (Python + Microsoft Foundry)
- 🤖 Copilot Studio implementation guides
- 📊 Evaluation datasets and metrics
- 📝 Responsible AI considerations
- 💡 Lessons learned

The goal is to share practical, reproducible experiments that demonstrate how AI agents can augment human work — always with humans in the loop.

## Experiments

Forty-four starters are in `experiments/`. The folders are 01 to 43 and 45. The count is the number of folders.

| # | Name | Description | Status |
|---|------|-------------|--------|
| 01 | [FOI Complaint Triage](experiments/01-foi-complaint-triage/) | Triage long FOI requests and complaints into structured data for public sector staff | ✅ Complete |
| 02 | [Complaint Intake — Consumer Duty / DISP](experiments/02-consumer-duty-complaint-intake/) | Draft a DISP complaint intake for a handler. Dates are computed in code. The agent does not send, decide, or write a case. | ✅ Starter |
| 03 | [Agent inventory and ATRS assurance pack](experiments/03-agent-inventory-atrs-assurance/) | Draft an ATRS record, a playbook mapping, a DPIA skeleton, a DUAA screen, and an FCA-style inventory row. The governance owner approves every lifecycle status change. | ✅ Starter |
| 04 | [FCA cryptoasset authorisation readiness](experiments/04-fca-cryptoasset-readiness/) | Draft a gap register against pinned FCA cryptoasset pages. The Compliance Officer or MLRO owns every gap conclusion. Autonomy A0. | ✅ Starter |
| 05 | [Awaab's Law hazard triage](experiments/05-awaabs-law-hazard-triage/) | Draft a hazard triage and statutory clock for a social landlord in England. The officer approves the category, the clock, and every summary. Dates are computed in code. The agent does not send or write a housing system. | ✅ Starter |
| 06 | [Policy questions for NHS corporate services](experiments/06-nhs-policy-qa/) | Quote an approved corporate policy, with its version and review date, or say "I don't know". Clinical questions are refused. The policy owner approves sources. Autonomy A0. | ✅ Starter |
| 07 | [Consultation themes](experiments/07-consultation-themes/) | Code one consultation question for a public body or charity. The analyst approves the framework and every sampled assignment. Counts keep minority views and link every theme to response IDs. The agent does not publish. | ✅ Starter |
| 08 | [Sensitive Data Redaction Agent — UK identifier PII gateway](experiments/08-uk-pii-redaction-gateway/) | Propose redactions for UK identifiers before text goes to a model. Checksums run where a published rule exists. A privacy reviewer approves the output. The agent does not release it and does not describe it as anonymised. | ✅ Starter |
| 09 | [Correspondence Draft Agent](experiments/09-casework-correspondence-draft/) | Draft one ministerial, MP, or resident reply. The author approves the recipient and the final text. Dates and line citations come from code. The agent does not send or invent a policy position. | ✅ Starter |
| 10 | [Travel Rule exception triage](experiments/10-travel-rule-exception-triage/) | Draft a reading of one synthetic cryptoasset transfer: missing or mismatched originator and beneficiary information, including a sunrise jurisdiction. The analyst decides hold, return, or escalate. Autonomy A1. The agent does not hold, return, release, file, or contact a counterparty. | ✅ Starter |
| 11 | [Employment Rights Act 2025 HR assistant](experiments/11-era-2025-hr-assistant/) | Draft a reading of one synthetic employer pack against pinned commencement dates. The HR lead decides. Autonomy A1. The agent does not decide compliance, discipline, publish, or send. | ✅ Starter |
| 12 | [Document Intake Agent](experiments/12-document-intake/) | Inventory one synthetic batch of text files. The user confirms the files and the permitted purpose. An intake reviewer decides the routing suggestion. UK identifiers are proposed by Experiment 08. Autonomy A1. The agent does not queue, release, write, or send. | ✅ Starter |
| 13 | [Council contact-centre front door](experiments/13-council-contact-front-door/) | Draft a reply from a fixed catalogue for a local-authority contact centre, or a handover to a person. The adviser accepts a published sentence. Autonomy A1. The agent does not decide eligibility, send a message, or write a case. | ✅ Starter |
| 14 | [Agent Architecture Advisor](experiments/14-agent-architecture-advisor/) | Draft platform options for one proposed agent: Copilot Studio standard harness, Copilot Studio GitHub Copilot harness, Microsoft Foundry Agent Service, Power Automate, or no agent. The architect confirms every option. Autonomy A0. The advisor does not select, approve a manifest, or deploy. | ✅ Starter |
| 15 | [Vulnerability and urgency scanner](experiments/15-vulnerability-urgency-scanner/) | Flag possible safeguarding, self-harm, financial hardship, and deadline indicators in inbound post and email. The duty officer reviews every flag. Autonomy A1. UK identifiers go through Experiment 08 before any model call. The agent does not close, deprioritise, send, or label a person as vulnerable. | ✅ Starter |
| 16 | [KYC Evidence Intake Agent](experiments/16-kyc-evidence-intake/) | Draft a Money Laundering Regulations 2017 checklist for one synthetic customer file. The KYC reviewer confirms the documents and the purpose. Experiment 12 inventories the files. Autonomy A1. The agent does not approve, reject, onboard, rate, file a report, or send. | ✅ Starter |
| 17 | [Invoice Exception Triage Agent](experiments/17-invoice-exception-triage/) | Draft a resolution for one synthetic invoice that failed a 2-way or 3-way match. The AP reviewer approves the resolution. A bank-detail change is routed to a separate verifier first. Experiment 12 inventories the file. Autonomy A1. The agent does not post, approve, hold, pay, or change supplier bank details. | ✅ Starter |
| 18 | [Evidence Pack Builder](experiments/18-evidence-pack-builder/) | Draft an index for one synthetic evidence pack. The evidence pack approver records the exact item list and the redaction decisions. Experiment 12 inventories in-scope items. Autonomy A1. The agent does not apply an exemption, disclose, write, or send. | ✅ Starter |
| 19 | [Privacy Impact Assessment Assistant](experiments/19-privacy-impact-assessment/) | Draft a DPIA for one synthetic project brief against UK GDPR Article 35 and Articles 22A to 22D. The privacy officer approves the assessment. The project owner accepts residual risk. Experiment 08 proposes identifier redactions. Autonomy A1. The agent does not approve, reject, sign off, accept residual risk, or send a consultation. | ✅ Starter |
| 20 | [Complaints root-cause and regulatory MI](experiments/20-complaints-root-cause-mi/) | Draft management information from one synthetic complaint batch for a Consumer Duty board report, a Housing Ombudsman Code self-assessment, or Ofgem complaints reporting. The complaints owner validates the clusters and the narrative. Every count lists source record ids. Experiments 02 and 08 are called in-process. Autonomy A0. The agent does not validate, submit, publish, or send. | ✅ Starter |
| 21 | [IT Service Desk Agent](experiments/21-it-service-desk/) | Draft a reading of one synthetic IT ticket from a fixed knowledge base. The member of staff confirms a device change. Password resets, MFA changes, and access grants go to an analyst. Experiment 08 counts UK identifiers. Autonomy A1. The agent does not reset, grant, execute, write a ticket, or send. | ✅ Starter |
| 22 | [On-chain alert investigator and SAR narrative drafter](experiments/22-onchain-alert-sar-drafter/) | Draft an internal timeline and a SAR narrative from one synthetic on-chain alert. The nominated officer decides whether to file. Experiments 10, 16, and 08 can be called. Autonomy A1. The agent does not file, request a defence, freeze or move a cryptoasset, or draft customer-facing content. | ✅ Starter |
| 23 | [Cryptoasset financial promotions pre-checker](experiments/23-crypto-financial-promotions-prechecker/) | Draft a checklist for one synthetic cryptoasset promotion. The section 21 approver signs off. Experiments 08, 04, and 03 can be called. Autonomy A0. The agent does not approve, publish, rewrite, or give a compliance opinion. | ✅ Starter |
| 24 | [Agent use-case intake](experiments/24-agent-use-case-intake/) | Draft a classification of one proposed agent for the governance team. Suggested autonomy is A0, A1, or A2. Experiments 14, 19, and 03 are called. Autonomy A1. The governance team approves or changes the classification. The agent does not approve the use case or provision anything. | ✅ Starter |
| 25 | [Instruction Quality Reviewer](experiments/25-instruction-quality-reviewer/) | Score one system prompt, SKILL.md, or topic prompt against a fixed checklist and propose a diff. The agent owner approves prompt changes. Experiments 03 and 14 can be called. Autonomy A0. The reviewer does not edit, apply, approve, or deploy. | ✅ Starter |
| 26 | [Skill Selection Evaluator](experiments/26-skill-selection-evaluator/) | Score whether a labelled utterance would select the right skill or topic, and propose a description diff. The maintainer validates routing tests. Experiments 25, 03, and 14 can be called. Autonomy A0. The evaluator does not edit, apply, validate, or deploy. | ✅ Starter |
| 27 | [Tool Contract Review Agent](experiments/27-tool-contract-review/) | Score one tool or action contract against a fixed checklist and propose contract notes and an API Management policy sketch. The security/API owner approves the contract. Experiments 03, 14, and 25 can be called. Autonomy A0. The reviewer does not modify, publish, approve, or deploy. | ✅ Starter |
| 28 | [Prompt Injection Test Agent](experiments/28-prompt-injection-test/) | Run a versioned suite of synthetic prompt-injection fixtures against a sandbox target and draft findings mapped to pinned OWASP titles. A security reviewer assesses the findings. Experiments 08, 25, and 03 can be called. Autonomy A0. The runner does not target production, assess, remediate, or publish. | ✅ Starter |
| 29 | [Groundedness Evaluation Agent](experiments/29-groundedness-evaluation/) | Score each claim in a synthetic Q&A bundle against the passages the agent was shown. The evaluation owner approves thresholds and any pass or fail release. Experiment 03 can draft an unapproved skeleton. Autonomy A0. The checker does not approve, release, or call Microsoft Foundry. | ✅ Starter |
| 30 | [Agent Regression Test Generator](experiments/30-agent-regression-test-generator/) | Draft regression cases from a synthetic manifest, skill files, a tool contract, and failure or change notes. The maintainer approves the tests and any pull request. Autonomy A1. The generator does not merge, push, or edit the agent under test. | ✅ Starter |
| 31 | [Agent Cost and Capacity Agent](experiments/31-agent-cost-capacity/) | Draft per-agent cost, unit cost per case, a flat forecast, and quota headroom from synthetic usage and a rate card with an effective date. The FinOps owner validates rates and the forecast. Autonomy A0. The agent does not change a quota, a budget, or a subscription, and it does not store a Microsoft price. | ✅ Starter |
| 32 | [Employee Case Intake Agent](experiments/32-employee-case-intake/) | Propose a category, an urgency flag, a statutory or Acas time reference, and a route for one synthetic HR case. An HR officer confirms the classification and the routing. Experiments 15, 12, and 08 are called in-process. Autonomy A1. The agent does not decide an outcome, contact the employee or a manager, or write to an HR system. | ✅ Starter |
| 33 | [Evidence and case-bundle summariser](experiments/33-case-bundle-summariser/) | Draft an extractive reading of one synthetic case bundle. Every sentence carries a pinpoint citation. The decision-maker reviews every cited sentence. Autonomy A0. The agent does not recommend an outcome, make a disclosure decision, or make a credibility finding. | ✅ Starter |
| 34 | [EHCP Draft Assembler](experiments/34-ehcp-draft-assembler/) | File synthetic SEND advice under the regulation 12 section headings, with citations, gaps, conflicts, and unsupported statements. The caseworker authors the final plan. Autonomy A1. The agent does not decide needs, provision, placement, or outcomes, and it does not send the draft. | ✅ Starter |
| 35 | [Claims Document Triage](experiments/35-claims-document-triage/) | Draft a reading of one synthetic FNOL pack with coverage pointers, inconsistency prompts, and a scorecard. The claims handler approves the class. Autonomy A1. The agent does not accept, decline, settle, tell the customer, or write a claims system. | ✅ Starter |
| 36 | [Cross-Source Validation Agent](experiments/36-cross-source-validation/) | Compare the same fact across synthetic source documents and classify each difference as a match, an immaterial difference, or a material discrepancy. The reviewer resolves every material discrepancy. Experiments 12, 08, and 33 are called in-process. Autonomy A0. The agent does not choose which source is right, edit a record, contact anyone, or query a live register. | ✅ Starter |
| 37 | [Underwriting Submission Summary](experiments/37-underwriting-submission-summary/) | Draft a cited summary of one synthetic broker submission. A missing field is not stated. The underwriter owns coverage and price. Autonomy A0. The agent does not accept or decline, suggest a price or terms, contact the broker, or write to an underwriting system. | ✅ Starter |
| 38 | [Policy Wording Comparison](experiments/38-policy-wording-comparison/) | Compare two or more synthetic policy wordings with a pinpoint citation on every clause. A topic that one wording does not state is not stated. Autonomy A0. A wording specialist validates every interpretation. The agent does not rank favourability, recommend buy, sell, or renew, draft an endorsement, contact a broker, or write to a policy administration system. | ✅ Starter |
| 39 | [Credit Memo Drafting](experiments/39-credit-memo-drafting/) | Draft a cited credit memo from one synthetic pack. A missing section is not stated. The credit officer owns the recommendation and every approval. Autonomy A1. The agent does not approve or decline, set a limit, contact the customer or a bureau, post to a core system, or file a SAR. | ✅ Starter |
| 40 | [Customer Self-Service Agent](experiments/40-customer-self-service/) | Answer one synthetic enquiry from a fixed knowledge base and prepare an address or appointment draft for confirmation. Autonomy A1. The agent does not reset a password, take a payment, close a complaint, change a tariff or a contract, write a record, or send. A person is always offered. | ✅ Starter |
| 41 | [Case Summary Agent](experiments/41-case-summary/) | Draft a cited reading of one synthetic contact-centre case. Every sentence names its event, paragraph, and line. Autonomy A0. The service representative checks accuracy. The agent does not contact the customer, change the record, close a complaint, or offer redress. | ✅ Starter |
| 42 | [Case Routing Assistant](experiments/42-case-routing-assistant/) | Propose a queue, a priority, and a reason for one synthetic case. Autonomy A1. The adviser confirms a route. The queue owner approves a material rule change. Vulnerability and statutory-clock cases always propose a human queue. The agent does not reroute, close, escalate, or edit a rule. | ✅ Starter |
| 43 | [Response Drafting Agent](experiments/43-response-drafting/) | Draft one customer response from a synthetic case and approved snippets, with source references and tone and plain-English screens. Autonomy A1. The representative sends. The agent does not send, write a case, offer redress, or decide that PRIN 2A.5 was met. | ✅ Starter |
| 45 | [Service Entitlement Explainer](experiments/45-service-entitlement-explainer/) | Explain what an approved entitlement table says about one synthetic service plan, quote the clause, and show uncertainty. Autonomy A0. A human decides a disputed entitlement. The agent does not grant, refuse, or change cover, and it does not decide that PRIN 2A.5 was met. | ✅ Starter |

## Getting Started

Each experiment is self-contained in its own folder under `experiments/`. Navigate to any experiment and follow its README for setup instructions.

### Prerequisites

- Python 3.10+
- Azure subscription (for Microsoft Foundry) — or use `--mock` mode for demos
- Copilot Studio license (for low-code implementations)

### Quick Start

```bash
# Clone the repo
git clone https://github.com/rahul-bachina/copilot-agent-experiments.git
cd copilot-agent-experiments

# Try an experiment in mock mode (no Azure credentials needed)
cd experiments/01-foi-complaint-triage
pip install -r requirements.txt
python src/triage_agent.py --mock --input examples/sample_request.txt

# Experiment 02 needs no credentials either. The DISP clock is deterministic.
cd ../02-consumer-duty-complaint-intake
pip install -r requirements.txt
python -m pytest tests/ -q
python src/disp_clock.py --received 2026-01-02 --route general

# Experiment 03 drafts an assurance pack. It does not approve it.
cd ../03-agent-inventory-atrs-assurance
pip install -r requirements.txt
python -m pytest tests/ -q
python src/pack.py --inventory fixtures/inventory/exp-01-foi-triage.json --as-of 2026-10-24

# Experiment 04 needs no credentials either. The gap register is deterministic.
cd ../04-fca-cryptoasset-readiness
pip install -r requirements.txt
python -m pytest tests/ -q
python src/gap_register.py --pack examples/harbourline --as-of 2026-10-24

# Experiment 05 needs no credentials either. The statutory clock is deterministic.
cd ../05-awaabs-law-hazard-triage
pip install -r requirements.txt
python -m pytest tests/ -q
python src/statutory_clock.py --aware-at 2026-01-08T09:00:00+00:00 --category significant --hazard-family damp_mould_fungal_growth --social-home-in-england --approve-category --approve-clock

# Experiment 06 needs no credentials either. The policy register is deterministic.
cd ../06-nhs-policy-qa
pip install -r requirements.txt
python -m pytest tests/ -q
python src/answer.py --question "How much notice do I need to book annual leave?" --as-of 2026-10-24

# Experiment 07 needs no credentials either. The codebook is deterministic.
cd ../07-consultation-themes
pip install -r requirements.txt
python -m pytest tests/ -q
python -m src.cli analyse --input eval/synthetic_dataset.json --as-of 2026-10-24

# Experiment 08 needs no credentials either. The detectors are deterministic.
cd ../08-uk-pii-redaction-gateway
pip install -r requirements.txt
python -m pytest tests/ -q
python src/gateway.py --input examples/sample_input.txt --caller exp-08-readme

# Experiment 09 needs no credentials either. The casework clock is deterministic.
cd ../09-casework-correspondence-draft
pip install -r requirements.txt
python -m pytest tests/ -q
python src/draft.py --received 2026-01-02 --as-of 2026-10-26 --input examples/sample_letter.txt --confirm-target --confirm-channel

# Experiment 10 needs no credentials either. The Travel Rule checklist is deterministic.
cd ../10-travel-rule-exception-triage
pip install -r requirements.txt
python -m pytest tests/ -q
python src/triage.py --input examples/sample_transfer.json --as-of 2026-10-26

# Experiment 11 needs no credentials either. The commencement checklist is deterministic.
cd ../11-era-2025-hr-assistant
pip install -r requirements.txt
python -m pytest tests/ -q
python src/review.py --input examples/sample_pack.json --as-of 2026-10-27

# Experiment 12 needs no credentials either. The inventory is deterministic.
cd ../12-document-intake
pip install -r requirements.txt
python -m pytest tests/ -q
python src/intake.py --input examples/sample_batch.json --as-of 2026-10-27

# Experiment 13 needs no credentials either. The catalogue is deterministic.
cd ../13-council-contact-front-door
pip install -r requirements.txt
python -m pytest tests/ -q
python src/front_door.py --input examples/sample_enquiry.json --as-of 2026-10-27

# Experiment 15 needs no credentials either. The phrase scan is deterministic.
# Experiment 08 has to be present beside it. The scanner calls that gateway.
cd ../15-vulnerability-urgency-scanner
pip install -r requirements.txt
python -m pytest tests/ -q
python src/scan.py --input examples/sample_letter.txt --synthetic

# Experiment 16 needs no credentials either. The checklist is deterministic.
cd ../16-kyc-evidence-intake
pip install -r requirements.txt
python -m pytest tests/ -q
python src/review.py --input examples/sample_customer_file.json --as-of 2026-10-27

# Experiment 17 needs no credentials either. The triage is deterministic.
# Experiments 12 and 08 have to be present beside it. The triage calls that intake.
cd ../17-invoice-exception-triage
pip install -r requirements.txt
python -m pytest tests/ -q
python src/triage.py --input examples/sample_case.json --as-of 2026-10-28

# Experiment 18 needs no credentials either. The index is deterministic.
# Experiments 08 and 12 have to be present beside it. The builder calls that intake.
cd ../18-evidence-pack-builder
pip install -r requirements.txt
python -m pytest tests/ -q
python src/pack.py --input examples/sample_request.json --as-of 2026-10-28 \
  --pack-type sar_bundle --scopes case_file,correspondence \
  --search-from 2026-01-01 --search-to 2026-10-28

# Experiment 19 needs no credentials either. The draft is deterministic.
# Experiment 08 has to be present beside it. The assistant calls that gateway.
cd ../19-privacy-impact-assessment
pip install -r requirements.txt
python -m pytest tests/ -q
python src/assess.py --input examples/sample_project.json --as-of 2026-10-28

# Experiment 20 needs no credentials either. The draft is deterministic.
# Experiments 02 and 08 have to be present beside it. The draft calls both.
cd ../20-complaints-root-cause-mi
pip install -r requirements.txt
python -m pytest tests/ -q
python src/report.py --input examples/sample_batch.json --as-of 2026-10-29

# Experiment 21 needs no credentials either. The draft is deterministic.
# Experiment 08 has to be present beside it. The desk calls that gateway.
cd ../21-it-service-desk
pip install -r requirements.txt
python -m pytest tests/ -q
python src/desk.py --input examples/sample_ticket.json --as-of 2026-10-29

# Experiment 22 needs no credentials either. The draft is deterministic.
# Experiments 04, 08, 10, 12, and 16 have to be present beside it.
cd ../22-onchain-alert-sar-drafter
pip install -r requirements.txt
python -m pytest tests/ -q
python src/investigate.py --input examples/sample_alert.json --as-of 2026-10-29

# Experiment 23 needs no credentials either. The checklist is deterministic.
# Experiments 03, 04, and 08 have to be present beside it.
cd ../23-crypto-financial-promotions-prechecker
pip install -r requirements.txt
python -m pytest tests/ -q
python src/precheck.py --input examples/sample_web.json --as-of 2026-10-30

# Experiment 24 needs no credentials either. The classification is deterministic.
# Experiments 03, 14, and 19 have to be present beside it.
cd ../24-agent-use-case-intake
pip install -r requirements.txt
python -m pytest tests/ -q
python src/classify.py --input examples/sample_proposal.json --as-of 2026-10-30

# Experiment 25 needs no credentials either. The checklist is deterministic.
# Experiments 03 and 14 sit beside it. The reviewer calls them only when the bundle asks.
cd ../25-instruction-quality-reviewer
pip install -r requirements.txt
python -m pytest tests/ -q
python src/review.py --bundle examples/sample_bundle.json --as-of 2026-10-30

# Experiment 26 needs no credentials either. The router is deterministic.
# Experiments 25, 03, and 14 sit beside it. The evaluator calls them only when the bundle asks.
cd ../26-skill-selection-evaluator
pip install -r requirements.txt
python -m pytest tests/ -q
python src/report.py --bundle examples/sample_bundle.json --as-of 2026-11-02

# Experiment 27 needs no credentials either. The checklist is deterministic.
# Experiments 03, 14, and 25 sit beside it. The reviewer calls them only when the bundle asks.
cd ../27-tool-contract-review
pip install -r requirements.txt
python -m pytest tests/ -q
python src/review.py --bundle examples/sample_bundle.json --as-of 2026-11-02

# Experiment 28 needs no credentials either. The suite is deterministic.
# Experiments 03, 08, and 25 sit beside it. The runner calls them only when the bundle asks.
cd ../28-prompt-injection-test
pip install -r requirements.txt
python -m pytest tests/ -q
python src/run.py --bundle examples/sample_bundle.json --as-of 2026-11-02

# Experiment 29 needs no credentials either. The claim checker is deterministic.
# Experiment 03 sits beside it. The checker calls it only when the bundle asks for a skeleton.
cd ../29-groundedness-evaluation
pip install -r requirements.txt
python -m pytest tests/ -q
python src/report.py --bundle examples/sample_bundle.json --as-of 2026-11-03

# Experiment 30 needs no credentials either. The case list is deterministic.
# Experiment 03 sits beside it. The generator calls it only when the bundle asks.
cd ../30-agent-regression-test-generator
pip install -r requirements.txt
python -m pytest tests/ -q
python src/generate.py --bundle examples/sample_bundle.json --as-of 2026-11-03

# Experiment 31 needs no credentials either. The report is deterministic.
# Rates come from the rate-card file. There is no built-in Microsoft price.
cd ../31-agent-cost-capacity
pip install -r requirements.txt
python -m pytest tests/ -q
python src/report.py --bundle examples/sample_bundle.json --rate-card examples/sample_rate_card.json --as-of 2026-11-03

# Experiment 32 needs no credentials either. The draft is deterministic.
# Experiments 15, 12, and 08 sit beside it. The intake calls them in-process.
cd ../32-employee-case-intake
pip install -r requirements.txt
python -m pytest tests/ -q
python src/draft.py --input examples/sample_case.json --as-of 2026-11-04

# Experiment 33 needs no credentials either. The reading is deterministic.
# Every sentence carries a pinpoint citation. The decision-maker reviews each one.
cd ../33-case-bundle-summariser
pip install -r requirements.txt
python -m pytest tests/ -q
python src/summarise.py --bundle examples/sample_bundle.json --as-of 2026-11-04
```

## Repository Structure

```
copilot-agent-experiments/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contribution guidelines
├── .gitignore
├── schemas/
│   └── agent-manifest.schema.json  # Reusable schema for agent permissions
├── tests/
│   └── test_agent_manifest_schema.py  # Schema validation tests
└── experiments/
    ├── 01-foi-complaint-triage/
    ├── 02-consumer-duty-complaint-intake/
    ├── 03-agent-inventory-atrs-assurance/
    ├── 04-fca-cryptoasset-readiness/
    │   ├── README.md              # Experiment documentation
    │   ├── agent-manifest.yaml    # Permissions and governance manifest
    │   ├── requirements.txt
    │   ├── src/                   # Python implementation
    │   ├── copilot-studio/        # Copilot Studio guides
    │   ├── eval/                  # Evaluation data and scripts
    │   ├── docs/                  # Architecture and security docs
    │   └── examples/              # Sample inputs/outputs
    ├── 05-awaabs-law-hazard-triage/
    ├── 06-nhs-policy-qa/
    ├── 07-consultation-themes/
    ├── 08-uk-pii-redaction-gateway/
    ├── 09-casework-correspondence-draft/
    ├── 10-travel-rule-exception-triage/
    ├── 11-era-2025-hr-assistant/
    ├── 12-document-intake/
    ├── 13-council-contact-front-door/
    ├── 14-agent-architecture-advisor/
    ├── 15-vulnerability-urgency-scanner/
    ├── 16-kyc-evidence-intake/
    ├── 17-invoice-exception-triage/
    ├── 18-evidence-pack-builder/
    ├── 19-privacy-impact-assessment/
    ├── 20-complaints-root-cause-mi/
    ├── 21-it-service-desk/
    ├── 22-onchain-alert-sar-drafter/
    ├── 23-crypto-financial-promotions-prechecker/
    ├── 24-agent-use-case-intake/
    ├── 25-instruction-quality-reviewer/
    ├── 26-skill-selection-evaluator/
    ├── 27-tool-contract-review/
    ├── 28-prompt-injection-test/
    ├── 29-groundedness-evaluation/
    ├── 30-agent-regression-test-generator/
    ├── 31-agent-cost-capacity/
    ├── 32-employee-case-intake/
    ├── 33-case-bundle-summariser/
    └── 34-ehcp-draft-assembler/
```

## Agent Governance

Every experiment in this repository includes an **agent manifest** (`agent-manifest.yaml`) that defines:

- **Agent identity** and purpose
- **Autonomy level** (A0, A1, or A2 — A3 is not permitted in this catalogue)
- **Data access** — what the agent may read and must never access
- **Tools and actions** — with explicit controls on writes and sends
- **High-risk actions** — must be disabled or have named human approval
- **Human approval points** — who approves what
- **UK GDPR compliance** — lawful basis, special category data, retention
- **Risk assessment** — likelihood, impact, controls, residual risk
- **Kill switch** — how to disable the agent immediately

See the [Agent Manifest Schema](schemas/agent-manifest.schema.json) for the full specification.

## Contributing

Contributions, suggestions, and feedback are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Connect

- 🔗 [GitHub](https://github.com/rahul-bachina)
- 💬 Questions? Open an issue

---

*Built with ❤️ using Microsoft AI technologies*
