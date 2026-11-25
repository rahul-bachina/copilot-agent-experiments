# Microsoft Copilot harness

This is the catalogue's GitHub Copilot harness for Experiment 79, implemented as the Microsoft Copilot harness described on the page opened on 25 November 2026. See [harness-comparison.md](harness-comparison.md). The page does not use the words "GitHub Copilot harness". That naming gap is unverified against the page.

The skills are:

- [compare-document-versions](../skills/compare-document-versions/SKILL.md)
- [record-route-seen](../skills/record-route-seen/SKILL.md)
- [confirm-version-pair](../skills/confirm-version-pair/SKILL.md)
- [record-interpretation-seen](../skills/record-interpretation-seen/SKILL.md)

Each skill calls the Python core. The core runs offline on the synthetic sample. It does not edit, approve, publish, or send a document.

The harness page says this harness can create and edit files. Those capabilities are not tools in this starter. A skill must not turn a comparison into an edited contract.

No agent is published from this folder. A person can always stop and read the JSON themselves.
