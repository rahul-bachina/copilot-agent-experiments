# Governance and security

Every experiment carries an `agent-manifest.yaml`. The file is the permissions record: what the agent is, what it may read, what it must never touch, which tools it has, and which actions a person must approve. A human-readable note sits beside it at `docs/security-and-permissions.md`. If the note and the manifest disagree, the manifest is the control.

The schema is [`schemas/agent-manifest.schema.json`](https://github.com/rahul-bachina/copilot-agent-experiments/blob/main/schemas/agent-manifest.schema.json). Continuous integration validates every manifest in `experiments/` against it. Fixtures that claim autonomy A3, or that enable a high-risk action with no approver, are required to fail.

This page is the catalogue rule. It is not a DPIA, a security accreditation, or a configured tenant. Nothing here creates an Entra directory, a DLP policy, a Key Vault, or a Foundry project.

## The permissions manifest

The schema requires these sections:

| Section | What a buyer should look for |
| --- | --- |
| Agent | Id, name, version, purpose, and an owner. Contact addresses in the current manifests are placeholders on `example.gov.uk` or `example.com`. |
| Autonomy | A0, A1, or A2 only. Whether any action can run without a person. |
| Data access | Each read, with why, and an explicit never-access list. |
| Tools | Allowed tools, and separate switches for writes and sends. |
| High-risk actions | Approve or reject, regulated decision, production record change, external send, and spending. Each one is disabled or has a named human approver. |
| Human approval | The decisions a person must take, and who that person is. |
| UK GDPR | Lawful basis, special-category data, minimisation, retention, residency. A starting point for the organisation's own assessment. |
| Risk assessment | Likelihood, impact, controls, residual risk, and an owner. |
| Logging and audit | What is logged, and where. Experiment 02's starter logs nothing yet. The manifest says so. |
| Kill switch | How to stop the agent, how fast, and who can do it. |
| Review | Last review, next review, and what forces an earlier one. |

Experiment 01 also maps some of those sections to ATRS fields. Experiment 02 does not. ATRS is a public-sector standard.

## Autonomy levels

The definitions below are the ones in [`docs/autonomy-levels.md`](https://github.com/rahul-bachina/copilot-agent-experiments/blob/main/docs/autonomy-levels.md). That file is the source. Both experiments in the repository are A1.

| Level | Name | What the agent may do |
| --- | --- | --- |
| A0 | Read-only analysis | Analyse and return a result. No capability to act, even with approval. |
| A1 | Human approves all | Suggest actions. A person approves every action before it runs. |
| A2 | Human approves high-risk | Take low-risk actions, such as logging or an internal query. High-risk actions need a person. |
| A3 | Fully autonomous | Acts without human approval. **Not permitted in this catalogue.** The schema rejects it. |

High-risk actions, for an A2 agent and for the schema, are:

1. Approve or reject a request, application, or claim.
2. A regulated decision, such as a Consumer Duty outcome, an FOI response, or a benefits determination.
3. Creating, updating, or deleting a production record.
4. An external send: email, message, letter, or any other communication.
5. Spending money, authorising a payment, or any other transaction.

Each high-risk action that is enabled needs a named approver. Both current manifests leave them disabled. A handler or officer still approves the draft before anyone relies on it. That approval is not the agent executing the action. The person does the consequential step in their own system.

## How the controls map to Microsoft products

The manifests and the security notes name the products below. They are the controls an adopting organisation would turn on. This repository does not turn them on, and it does not prove they are configured in anyone's tenant.

| Control | What it is for in this catalogue | Where it is named |
| --- | --- | --- |
| Microsoft Entra Agent ID | An identity for the agent, so access and audit can be tied to it rather than to a shared key. | Experiment 01's security guide, as the identity control. Experiment 02 does not claim an Agent ID has been created. |
| Conditional Access | Restrict which people and devices can invoke the agent, and block it as a kill switch. | Experiment 01, including risk R7 and the kill switch. |
| Power Platform DLP | Stop connectors the manifest does not allow, including mail and case-write connectors. | Both experiments. Experiment 02's default is no connector. DLP is the backstop if one is added later. |
| Microsoft Foundry prompt shields | Filter prompt injection and unsafe content on a model call. | Experiment 01. Experiment 02's Foundry note says to turn them on, and says the filter is not what stops a send. The missing tool is. |
| Key Vault | Hold an API key if a managed identity cannot be used, and revoke it to stop the agent. | Both. Experiment 02 prefers a managed identity for any orchestration. |
| Microsoft Purview | Classification, governance, and compliance reporting around the data the agent sees. | Experiment 01's security guide. Not configured by this repository. |
| Application Insights | Telemetry of invocations and failures. Experiment 01 says to log the size of the input, not the text. | Experiment 01, marked as an assumption. Experiment 02 writes no log in the starter and says not to put the complaint text in an application trace. |

Experiment 01's security guide also lists three announced capabilities whose general availability it marks as unverified: Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access. Do not treat those as controls you can rely on until availability is confirmed. The guide says it will be updated when that changes.

## UK GDPR

The two experiments do not share a lawful basis. Copying one into the other would be a mistake.

| | Experiment 01, public body | Experiment 02, FCA-regulated firm |
| --- | --- | --- |
| Lead basis in the manifest | Article 6(1)(e), public task | Article 6(1)(c), legal obligation under DISP, for the DPO to confirm |
| Secondary | Article 6(1)(c), legal obligation to respond to FOI, EIR, and SAR requests | Not fixed. Article 6(1)(b) may be relevant for a contract. Do not copy the public-task basis. |
| Special-category data | May appear. Manifest cites Article 9(2)(g) and DPA 2018 Schedule 1, Part 2, paragraph 6. | May appear. **No Article 9 condition is asserted.** The firm chooses one before live processing. |
| Retention by the agent | None. Transient. | None in the starter. The firm's complaints file applies to what the handler then saves. |
| Residency | UK South or UK West, as an assumption to confirm | Same assumption, if Foundry is used |

Neither page is a data protection impact assessment. Experiment 02 says so in its security note.

## Algorithmic Transparency Recording Standard

Public-sector bodies use the [Algorithmic Transparency Recording Standard](https://www.gov.uk/government/collections/algorithmic-transparency-recording-standard-hub) to record how an algorithmic tool is used. Experiment 01's manifest maps name, description, scope, human oversight, risk, and the UK GDPR section onto ATRS fields. The experiment says a public-facing deployment would likely need an entry, and that this starter is for staff decision support rather than a tool the public uses directly.

This repository does not submit an ATRS record. The deploying organisation does. Experiment 02 has no ATRS mapping. A firm does not become ATRS-compliant by adopting that starter.

A future experiment, G010, is named on the roadmap as an inventory and assurance pack. It is not in the repository.

## Synthetic data

Samples, evaluation fixtures, and smoke tests use invented text. Experiment 01 says no real personal data and no real requests are in its set. Experiment 02 uses invented people and a fictional firm, Northbridge Mutual, and says not to replace the fixtures with live complaints.

Smoke tests check that code runs. They are not model scores. The counts are on the experiment pages, labelled as smoke tests.

## Kill switch

| Experiment | Ways to stop it, as written |
| --- | --- |
| 01 | Turn the Copilot Studio agent off. Revoke the key in Key Vault. Block access with Conditional Access. Block the connector with a Power Platform DLP policy. |
| 02 | Turn the Copilot Studio agent off. Remove the Foundry access. If a connector was added despite the default, block it with DLP. |

Times in the manifests are the platform's, not a measured drill. Escalation contacts are placeholders. Replace them before anyone relies on the page.

## What continuous integration checks

- [`validate-agent-manifests.yml`](https://github.com/rahul-bachina/copilot-agent-experiments/blob/main/.github/workflows/validate-agent-manifests.yml) checks the schema, validates each manifest, and checks that the invalid fixtures are rejected.
- Experiment 01's workflow runs unit tests, schema validation, and a mock-mode smoke test.
- Experiment 02's workflow runs the unit tests, including the intake safety tests, and the mock evaluation.
- This site's workflow runs `mkdocs build --strict` on every pull request.
