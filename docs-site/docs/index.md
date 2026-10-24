# Copilot agent experiments

This site explains the agent experiments in [rahul-bachina/copilot-agent-experiments](https://github.com/rahul-bachina/copilot-agent-experiments). Each experiment is a small, documented starting point on the Microsoft stack: Power Platform, Copilot Studio, Microsoft Foundry, and GitHub Copilot.

The repository is the source of truth. These pages are a briefing for people who have to decide whether a starter is fit to try. They are not a product, a procurement framework, or a completed compliance assessment.

The pages were written from the repository as it stood on 24 October 2026. If a page and an `agent-manifest.yaml` disagree, the manifest is the control.

## Who it is for

The briefings are written for people who own the service, the risk, or the design:

- heads of service
- FOI and complaints leads
- data protection officers
- chief information security officers and security architects
- solution architects who may rebuild a starter in their own tenant

Developers still work from the source folders. This site does not replace those READMEs. It states the problem, the limit of the agent, and the controls in plain English.

Experiment 01 is for UK public bodies handling information requests and complaints. Experiment 02 is for FCA-regulated firms handling complaints under DISP and the Consumer Duty. They are not interchangeable.

## Governance principles

Every experiment in the catalogue is held to the same rules. The [agent manifest schema](https://github.com/rahul-bachina/copilot-agent-experiments/blob/main/schemas/agent-manifest.schema.json) checks several of them in continuous integration. A manifest that fails the schema is not accepted.

| Principle | What it means here |
| --- | --- |
| Autonomy A0, A1 or A2 only | The agent may analyse, suggest, or take low-risk steps. Fully autonomous action (A3) is rejected by the schema. Definitions are in [docs/autonomy-levels.md](https://github.com/rahul-bachina/copilot-agent-experiments/blob/main/docs/autonomy-levels.md). |
| Human approval for any consequential action | Approving or rejecting, a regulated decision, a production record change, an external send, and spending must be switched off or named to a human approver. Both current experiments switch them off. |
| Least privilege | The manifest lists what the agent may read and what it must never access. Writes and sends are separate switches. |
| Synthetic data | Samples, fixtures and smoke tests use invented text. The repository is not a place for live cases. |
| A permissions manifest for each agent | `agent-manifest.yaml` sits in the experiment folder. It names the owner, the autonomy level, the tools, the approval points, the UK GDPR position, the risks and the kill switch. |
| UK GDPR | Lawful basis, special-category data, retention and residency are fields in the manifest. They are a prompt for the organisation's own assessment, not a finished DPIA. The public-body basis in experiment 01 is not the basis for the firm in experiment 02. |
| Algorithmic Transparency Recording Standard | A public-sector deployment may need an ATRS record. Experiment 01 maps manifest fields to ATRS fields. This repository does not submit a record. |

## Experiments

Two experiments are in the repository. The controls are set out on [Governance and security](governance.md). Names that are not started are on the [roadmap](roadmap.md). No date is attached to them.

Status labels used on this site:

| Label | Meaning |
| --- | --- |
| <span class="status status-available">Available</span> | The experiment is in the repository. You can run the parts the briefing marks as runnable. A build guide is not a tenant you can import. |
| <span class="status status-blueprint">Blueprint</span> | The design is written down. The runnable agent is not in the repository. |
| <span class="status status-planned">Planned</span> | Named as future work. No design and no code in the repository. No date is promised. |
| <span class="status status-archived">Archived</span> | Withdrawn from the catalogue and kept so the record is still there. |

Nothing in the repository is marked Blueprint or Archived today.

<div class="exp-grid" markdown="1">

<div class="exp-card" markdown="1">

<p class="exp-meta"><span class="status status-available">Available</span> · Autonomy A1 · Experiment 01</p>

### FOI and complaint triage

For UK public bodies. Takes a long FOI request, Environmental Information Regulations request, subject access request or complaint and returns a structured brief for a member of staff. Staff decide. The agent does not send, write to a case system, or reject a request.

The repository README marks this experiment complete. That means the starter is written. It does not mean a live model has been scored, and it does not mean a tenant has been configured.

[Read the briefing](experiments/01-foi-complaint-triage.md) · [Source folder](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/01-foi-complaint-triage)

</div>

<div class="exp-card" markdown="1">

<p class="exp-meta"><span class="status status-available">Available</span> · Autonomy A1 · Experiment 02 · C006</p>

### Consumer Duty complaint intake

For FCA-regulated firms. Helps a complaints handler turn one inbound complaint into a draft intake, and calculates DISP dates in Python rather than in a model. The handler validates every classification and every severity.

The repository README marks this as a starter. The clock and the mock intake run on a laptop. Nothing in the folder calls a model. Copilot Studio, Microsoft Foundry and Dynamics 365 Customer Service are build notes.

[Read the briefing](experiments/02-consumer-duty-complaint-intake.md) · [Source folder](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/02-consumer-duty-complaint-intake)

</div>

</div>

## What these pages will not claim

- No client names, testimonials, or measured savings. None are in the repository.
- A smoke test in mock mode is a check that the code runs on synthetic text. It is not a model score. Where a smoke-test count is quoted, it is labelled as one.
- No page here is legal advice, a data protection impact assessment, or an ATRS submission.
- Contact addresses on `example.gov.uk` and `example.com` in the manifests are placeholders.

## Licence

The repository is under the MIT Licence. Copyright 2026 Rahul Bachina. See [LICENSE](https://github.com/rahul-bachina/copilot-agent-experiments/blob/main/LICENSE).
