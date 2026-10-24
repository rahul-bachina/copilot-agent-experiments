# Contributing to Copilot Agent Experiments

Thank you for your interest in contributing! This is a learning-focused repository, and contributions that help others learn are especially welcome.

## Ways to Contribute

### 🐛 Report Issues
- Found a bug? Open an issue with steps to reproduce
- Include your Python version and environment details

### 💡 Suggest Improvements
- Ideas for better explanations or documentation
- Alternative approaches or architectures
- Additional evaluation cases

### 🔧 Submit Changes
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Make your changes
4. Run tests (`pytest` for Python code)
5. Commit with clear messages
6. Open a Pull Request

## Guidelines

### Code Style
- Python: Follow PEP 8, use type hints
- Include docstrings for functions
- Keep code readable and well-commented for learning purposes

### Documentation
- Update READMEs when changing functionality
- Include examples where helpful
- Be clear about what is a guide vs runnable code

### Agent Manifests (Required)

Every experiment must include an `agent-manifest.yaml` that defines the agent's permissions, data access, and governance controls. The manifest must:

1. **Validate against the schema** at `schemas/agent-manifest.schema.json`
2. **Use autonomy level A0, A1, or A2** — A3 (fully autonomous) is not permitted in this catalogue
3. **Declare all high-risk actions** (approve/reject, regulated decisions, production writes, external sends, spending) as either disabled or with explicit human approval
4. **Document UK GDPR compliance** including lawful basis and special category data handling
5. **Include a risk assessment** with likelihood, impact, controls, and residual risk
6. **Define kill switch mechanisms** for immediate agent disablement

Run `python -m pytest tests/test_agent_manifest_schema.py` to validate your manifest locally before submitting.

### Responsible AI
- Never include real personal data
- Clearly mark synthetic/test data
- Consider fairness and accessibility implications
- Document human-in-the-loop requirements

## Questions?

Open an issue or reach out on [LinkedIn](https://www.linkedin.com/in/rahulbachina/).

---

*Thank you for helping make AI more accessible and responsible!*
