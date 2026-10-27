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
    └── 16-kyc-evidence-intake/
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
