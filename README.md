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
| 04 | [FCA cryptoasset authorisation readiness](experiments/04-fca-cryptoasset-readiness/) | Draft a gap register against pinned FCA cryptoasset pages. The Compliance Officer or MLRO owns every gap conclusion. Autonomy A0. | ✅ Starter |
| 05 | [Awaab's Law hazard triage](experiments/05-awaabs-law-hazard-triage/) | Draft a hazard triage and statutory clock for a social landlord in England. The officer approves the category, the clock, and every summary. Dates are computed in code. The agent does not send or write a housing system. | ✅ Starter |

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
    ├── 04-fca-cryptoasset-readiness/
    │   ├── README.md              # Experiment documentation
    │   ├── agent-manifest.yaml    # Permissions and governance manifest
    │   ├── requirements.txt
    │   ├── src/                   # Python implementation
    │   ├── copilot-studio/        # Copilot Studio guides
    │   ├── eval/                  # Evaluation data and scripts
    │   ├── docs/                  # Architecture and security docs
    │   └── examples/              # Sample inputs/outputs
    └── 05-awaabs-law-hazard-triage/
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
