# Copilot Agent Experiments

A series of small, well-documented AI agent experiments exploring practical applications of Microsoft Copilot, Azure AI Foundry, and Power Platform technologies.

**By [Rahul Bachina](https://github.com/rahul-bachina)** — UK-based Microsoft-stack AI builder specialising in Power Platform, Azure AI Foundry, Copilot Studio, and GitHub Copilot.

## About This Series

Each experiment in this repository tackles a real-world problem with AI agents, providing:

- 🎯 Clear problem statement and context
- 🏗️ Architecture diagrams and design rationale
- 💻 Working code (Python + Azure AI Foundry)
- 🤖 Copilot Studio implementation guides
- 📊 Evaluation datasets and metrics
- 📝 Responsible AI considerations
- 💡 Lessons learned

The goal is to share practical, reproducible experiments that demonstrate how AI agents can augment human work — always with humans in the loop.

## Experiments

| # | Name | Description | Status |
|---|------|-------------|--------|
| 01 | [FOI Complaint Triage](experiments/01-foi-complaint-triage/) | Triage long FOI requests and complaints into structured data for public sector staff | ✅ Complete |

## Getting Started

Each experiment is self-contained in its own folder under `experiments/`. Navigate to any experiment and follow its README for setup instructions.

### Prerequisites

- Python 3.10+
- Azure subscription (for Azure AI Foundry) — or use `--mock` mode for demos
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
```

## Repository Structure

```
copilot-agent-experiments/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contribution guidelines
├── .gitignore
└── experiments/
    └── 01-foi-complaint-triage/
        ├── README.md         # Experiment documentation
        ├── requirements.txt
        ├── src/              # Python implementation
        ├── copilot-studio/   # Copilot Studio guides
        ├── eval/             # Evaluation data and scripts
        ├── docs/             # Architecture diagrams
        └── examples/         # Sample inputs/outputs
```

## Contributing

Contributions, suggestions, and feedback are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Connect

- 🔗 [GitHub](https://github.com/rahul-bachina)
- 💬 Questions? Open an issue

---

*Built with ❤️ using Microsoft AI technologies*
