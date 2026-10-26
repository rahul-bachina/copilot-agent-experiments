# GitHub Copilot harness

This is the reviewer follow-up variant for Experiment 08. It proposes redactions and can explain one finding. The fixed topic path stays on the standard harness. See [harness-comparison.md](harness-comparison.md).

The Python core, the manifest, and the tests are the same on both. This harness does not add an approval step and it does not remove one.

## What Microsoft says it is

Microsoft Learn, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 26 October 2026:

- The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service.
- The page says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. Existing Copilot Studio privacy, security, compliance, and data-residency commitments continue to apply.
- It is described as the harness for reasoning-heavy, multi-step work. It can take a goal, call tools, use skills and memory, create and edit Word, Excel, PowerPoint, and PDF files, and run each task in a sandbox governed by Copilot Studio.
- Agents and workflows on this harness use Copilot Credits.
- The overview text retrieved that day did not label the harness itself as preview. Confirm the release state in the tenant before relying on it.

The skills-upload article was not opened on 26 October 2026. This repository uses the same `SKILL.md` front matter as Experiments 01 and 02. The approval headings copy `agent-manifest.yaml`. They are not claimed as a Microsoft schema.

## Skills in this experiment

| Skill | Path | What the reviewer gets |
| --- | --- | --- |
| Propose a redaction | [../skills/propose-redaction/SKILL.md](../skills/propose-redaction/SKILL.md) | The JSON from `src/gateway.py` |
| Explain a finding | [../skills/explain-redaction-finding/SKILL.md](../skills/explain-redaction-finding/SKILL.md) | A reading of a finding the gateway already returned |

Neither skill releases, sends, or describes the output as anonymised. The explain skill does not recalculate a checksum.

## How to build it

1. Create an agent on the GitHub Copilot harness. Name it "UK identifier redaction (draft)". Language: English (United Kingdom).
2. Paste the instructions from [../copilot-studio/system-prompt.md](../copilot-studio/system-prompt.md). They are the same boundaries. Do not add a goal that says "release the redacted text".
3. Upload the two skills. Do not upload them onto a standard-harness agent.
4. Point the tool at `propose()` in `src/gateway.py`. A small internal API is enough. Do not reimplement modulus 11 in the model.
5. Do not add a mail connector, an HTTP action to a public model with the raw text logged, or a Key Vault write. If a tool is not in the manifest, it should not be on the agent.
6. Leave `apply_model_suggestions` false. A model span is the reviewer's decision, and the skill says so.

## What the reviewer sees

The proposal banner, the findings, the limitations, and the statement that nothing has been released. `output_is_anonymised` is false. `agent_may_release` is false.

A sandbox file of that JSON is a draft. It is not a release.

## What this harness must not do

- Invent an NHS check digit, a NINO prefix class, or an IBAN remainder.
- Hide a known miss. The limitations list is part of the answer.
- Store the text in memory. Whether memory can be switched off was not verified on 26 October 2026.
- Call `record_reviewer_decision`. That function is for the reviewer's own script. The agent does not approve itself.
- Call `release()` except to show that it raises. It always raises.
