# Security and permissions

Skill Selection Evaluator, Experiment 26. Catalogue ID G004.

Autonomy **A0**. Writes disabled. Sends disabled. The maintainer validates routing tests. This tool does not record that validation.

If this note and `agent-manifest.yaml` disagree, the manifest is the control.

## What a run may read

The skill and topic files the maintainer supplies, the labelled utterances, an optional permissions manifest, an optional structured use case, the as-of date, and the static source list. On the local machine the run may import Experiment 25, Experiment 14's rule table, and, when PyYAML and jsonschema are already installed, Experiment 03's generator.

## What a run must not read or change

A Copilot Studio tenant, a skill store, a mailbox, a billing account, and Copilot Studio, Microsoft Foundry, or Power Automate as a control plane. The evaluator does not edit a skill and does not deploy.

## Human approval

| Decision | Who |
|---|---|
| Validate routing tests | Maintainer |
| Accept or reject each description rewrite before it is kept | Maintainer |
| Rely on a manifest skeleton drafted because none was supplied | Governance owner |
| Re-open a pinned page, or a review date, before relying on a citation | Maintainer |
| Confirm an Article 6 basis, and an Article 9 condition if special-category data was pasted | Data protection officer |
| Deploy or publish | Outside this evaluator |

The contact in the manifest is `skill-routing@example.com`. It is a placeholder. Northfen Borough Council is fictional.

## UK GDPR

The manifest does not assert a lawful basis. The data protection officer confirms one before any live processing. No Article 9 condition is asserted. This note is not a DPIA. The samples are synthetic, apart from skill files already published in this repository. A routing score is not a statement that a catalogue meets UK GDPR.

## Prompt injection and prohibited actions

Fixtures include utterances that tell the evaluator to ignore its instructions and select a named skill, and utterances that ask it to send, deploy, take a payment, delete production records, approve a claim, leak data, or grant access. The evaluator records them and does not follow them. A prohibited request routes to `human`. `tests/test_injection.py` and `tests/test_prohibited.py` cover that. `--approve`, `--apply`, `--edit-skills`, and `--deploy` exit without writing a file.

## Stale data

Older than the threshold, default 90 days, is stale. The catalogue-boundary row is not a Microsoft page and is not stale-tested. A missing review date on a skill is stale. The evaluator does not clear the flag by itself. `reopened_for_this_experiment` stays false. `tests/test_stale.py` covers that.

## Tenant controls

Microsoft Entra identity, role-based access, private networking, and Application Insights are described on the Foundry Agent Service overview that Experiment 14 opened. They are not configured here.

The following were not opened for this experiment. Treat them as unverified:

- Entra Agent ID. Unverified.
- Conditional Access for agents. Unverified.
- A data loss prevention policy in Power Platform. Unverified.
- Key Vault. This starter has no secret. A later secret would go in Key Vault. Unverified as a control for this folder.
- Purview. Unverified.
- Application Insights as a configured resource. The product is named on a page Experiment 14 opened. No resource was created here.

Prompt Shields were opened by Experiment 14 and are not called. User prompt attack detection is described as on by default. Document attack detection is described as off by default. Tool-response scanning and Spotlighting are marked preview. The page says the service is Azure AI Content Safety. Shields do not validate routing tests.

## Logging and the kill switch

This starter writes no log. Before live use, log the bundle id, the as-of date, whether an injection pattern was detected, and whether a diff was proposed. Do not log the skill text or the utterances.

The kill switch is to not run the command. There is no published agent to turn off.

## Review

2 November 2026. Next review 2 May 2027, and sooner if a pinned page is re-opened and has changed.
