# Microsoft Copilot harness

This is the catalogue's GitHub Copilot harness for Experiment 80, implemented as the Microsoft Copilot harness described on the page opened on 26 November 2026. See [harness-comparison.md](harness-comparison.md). The page does not use the words "GitHub Copilot harness". That naming gap is unverified against the page.

The skills are:

- [review-translation](../skills/review-translation/SKILL.md)
- [record-route-seen](../skills/record-route-seen/SKILL.md)
- [record-high-risk-validated](../skills/record-high-risk-validated/SKILL.md)
- [record-translation-owned](../skills/record-translation-owned/SKILL.md)

Each skill calls the Python core. The core runs offline on the synthetic sample. It does not publish, send, or overwrite a document.

The harness page says this harness can create and edit files. Those capabilities are not tools in this starter. A skill must not turn a review into an overwritten translation.

No agent is published from this folder. A person can always stop and read the JSON themselves.
