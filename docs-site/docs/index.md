---
hide:
  - navigation
  - toc
  - footer
---

<div class="hero" markdown="1">

<div markdown="1">

<p class="eyebrow">An open experiment library</p>

# Useful agents. Clear boundaries. Humans in control.

<p class="intro">Practical Microsoft agent starters for UK public bodies and FCA-regulated firms. See what each one does, where it stops, and which controls come first.</p>

<div class="actions" markdown="1">

[Explore the experiments](#experiments){ .button }
[Read the governance brief](governance.md){ .text-link }

</div>

<p class="hero-note">Open source. Synthetic data. A person approves any consequential action.</p>

</div>

<div class="workflow" markdown="1">

<p class="workflow-top"><span>How the starters work</span><span>1 to 3</span></p>

<ol>
<li>
<p class="step-kicker">1. Input</p>
<p><strong>A request comes in.</strong> Synthetic text in this repository. Defined permissions.</p>
</li>
<li>
<p class="step-kicker">2. Agent assistance</p>
<p><strong>Structure, classify, suggest.</strong> A draft to support a decision.</p>
</li>
<li class="human">
<p class="step-kicker">3. Human review</p>
<p><strong>The decision stays with a person.</strong> Staff check every output before anyone relies on it.</p>
</li>
</ol>

<p class="workflow-foot"><span>External sends are switched off.</span><span>Production writes are switched off.</span></p>

</div>

</div>

<div class="stack-strip" markdown="1">

<p class="stack-label">Built on the Microsoft stack</p>

- Power Platform
- Copilot Studio
- Microsoft Foundry
- GitHub Copilot

</div>

<div class="section-heading" id="experiments" markdown="1">

<div markdown="1">

<p class="eyebrow">The experiments</p>

## Seventy-four starters you can read today

</div>

<p>Different services. The same rule: a person decides.</p>

</div>

<div class="exp-grid" markdown="1">

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 01 · Public sector · Autonomy A1</p>

### FOI and complaint triage

Turn a long information request or complaint into a structured brief for a member of staff. The person decides.

<div class="boundary" markdown="1">

<span>The boundary</span>

No sending, no case-system writes, and no rejection of a request.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/01-foi-complaint-triage.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/01-foi-complaint-triage)
[Standalone repo](https://github.com/rahul-bachina/foi-complaint-triage-copilot-agent)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 02 · C006 · FCA firms · Autonomy A1</p>

### Consumer Duty complaint intake

Turn one complaint into a draft intake. DISP dates are calculated in Python. A handler checks every classification and the severity.

<div class="boundary" markdown="1">

<span>The boundary</span>

The clock and the mock intake run locally. Nothing in the folder calls a model.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/02-consumer-duty-complaint-intake.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/02-consumer-duty-complaint-intake)
[Standalone repo](https://github.com/rahul-bachina/consumer-duty-complaints-copilot-agent)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 03 · G010 · Autonomy A1</p>

### Agent inventory and ATRS assurance pack

Draft an ATRS record, a playbook mapping, a DPIA skeleton, a DUAA screen, and an FCA-style inventory row. The governance owner approves every lifecycle status change.

<div class="boundary" markdown="1">

<span>The boundary</span>

Drafts only. Nothing is approved, sent, or written to Dataverse.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/03-agent-inventory-atrs-assurance.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/03-agent-inventory-atrs-assurance)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 04 · UK02 · FCA firms · Autonomy A0</p>

### FCA cryptoasset authorisation readiness

Read a synthetic policy pack and draft an observation register against pinned FCA pages. The Compliance Officer or MLRO owns every gap conclusion.

<div class="boundary" markdown="1">

<span>The boundary</span>

No readiness finding, no regulatory advice, and no application is submitted. The checker runs locally.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/04-fca-cryptoasset-readiness.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/04-fca-cryptoasset-readiness)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 05 · UK01 · Social landlords · Autonomy A1</p>

### Awaab's Law hazard triage

Turn one tenant report into a draft triage and a statutory clock. The officer approves the category, the clock, and every summary.

<div class="boundary" markdown="1">

<span>The boundary</span>

The clock and the mock triage run locally. Nothing is sent, and nothing is written to a housing system.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/05-awaabs-law-hazard-triage.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/05-awaabs-law-hazard-triage)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 06 · M003 · NHS and public bodies · Autonomy A0</p>

### Policy questions for NHS corporate services

Quote an approved corporate policy, with its version and review date, or say "I don't know". Clinical questions are refused. The policy owner approves sources.

<div class="boundary" markdown="1">

<span>The boundary</span>

The register runs locally. Nothing is published, sent, or decided for a person.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/06-nhs-policy-qa.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/06-nhs-policy-qa)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 07 · V010 · Public bodies · Autonomy A1</p>

### Consultation themes

Code one consultation question. The analyst approves the framework and every sampled assignment. Minority views stay, with response IDs.

<div class="boundary" markdown="1">

<span>The boundary</span>

The codebook runs locally. Nothing is published, and a response cannot approve the framework.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/07-consultation-themes.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/07-consultation-themes)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 08 · O005 · Autonomy A1</p>

### UK identifier PII gateway

Propose redactions for UK identifiers before text goes to a model. A privacy reviewer approves the output. The gateway does not release it.

<div class="boundary" markdown="1">

<span>The boundary</span>

The detectors run locally. The proposal is not anonymised, and nothing is released.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/08-uk-pii-redaction-gateway.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/08-uk-pii-redaction-gateway)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 09 · O008 · Public bodies · Autonomy A1</p>

### Correspondence draft

Draft one reply for ministerial, MP, or resident casework. The author approves the recipient and the final text. A policy sentence is a supplied line, or the draft says there is a gap.

<div class="boundary" markdown="1">

<span>The boundary</span>

The clock runs locally. Nothing is sent, and the letter cannot choose its own recipient.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/09-casework-correspondence-draft.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/09-casework-correspondence-draft)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 10 · UK05 · FCA firms · Autonomy A1</p>

### Travel Rule exception triage

Read one synthetic cryptoasset transfer and draft the missing or mismatched fields. The analyst decides hold, return, or escalate. A follow-on to Experiment 04.

<div class="boundary" markdown="1">

<span>The boundary</span>

The checklist runs locally. Nothing is held, returned, released, filed, or sent to a counterparty.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/10-travel-rule-exception-triage.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/10-travel-rule-exception-triage)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 11 · UK03 · Employers · Autonomy A1</p>

### Employment Rights Act 2025 HR assistant

Read one synthetic employer pack and draft which pinned duties are in force. The HR lead decides. It does not find that the employer complied, and it does not discipline or send.

<div class="boundary" markdown="1">

<span>The boundary</span>

The checklist runs locally. Nothing is decided, published, written to a personnel record, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/11-era-2025-hr-assistant.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/11-era-2025-hr-assistant)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 12 · O001 · Autonomy A1</p>

### Document intake

Inventory one synthetic batch of text files. The user confirms the files and the purpose. An intake reviewer decides the routing suggestion. UK identifiers are proposed by Experiment 08.

<div class="boundary" markdown="1">

<span>The boundary</span>

The inventory runs locally. Nothing is confirmed, queued, released, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/12-document-intake.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/12-document-intake)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 13 · V006 · Local authorities · Autonomy A1</p>

### Council contact-centre front door

Quote one published page for an adviser, or hand the conversation to a person. Emergencies and eligibility questions stop at a handover.

<div class="boundary" markdown="1">

<span>The boundary</span>

The catalogue runs locally. Nothing is decided, sent, or written to a case.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/13-council-contact-front-door.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/13-council-contact-front-door)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 14 · G002 · Autonomy A0</p>

### Agent Architecture Advisor

Draft options for one proposed agent: a Copilot Studio harness, Microsoft Foundry Agent Service, Power Automate, or no agent. The architect confirms every option.

<div class="boundary" markdown="1">

<span>The boundary</span>

The advisor runs locally. Nothing is selected, approved, or deployed.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/14-agent-architecture-advisor.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/14-agent-architecture-advisor)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 15 · UK06 · Inbound post and email · Autonomy A1</p>

### Vulnerability and urgency scanner

Flag possible safeguarding, self-harm, financial hardship, and deadline indicators in one synthetic letter. The duty officer reviews every flag. UK identifiers go through Experiment 08 before any model call.

<div class="boundary" markdown="1">

<span>The boundary</span>

The scanner runs locally. Nothing is closed, deprioritised, or sent, and no one is labelled vulnerable.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/15-vulnerability-urgency-scanner.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/15-vulnerability-urgency-scanner)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 16 · B004 · FCA firms · Autonomy A1</p>

### KYC evidence intake

Draft a checklist for one synthetic customer file against the Money Laundering Regulations 2017. The KYC reviewer confirms the documents and the purpose. Experiment 12 inventories the files.

<div class="boundary" markdown="1">

<span>The boundary</span>

The checklist runs locally. Nothing is confirmed, approved, rated, filed, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/16-kyc-evidence-intake.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/16-kyc-evidence-intake)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 17 · F004 · UK public bodies and regulated firms · Autonomy A1</p>

### Invoice exception triage

Draft a resolution for one synthetic invoice that failed a 2-way or 3-way match. The AP reviewer approves the resolution. A bank-detail change goes to a separate verifier first. Experiment 12 inventories the file.

<div class="boundary" markdown="1">

<span>The boundary</span>

The triage runs locally. Nothing is posted, approved, held, paid, or changed on a supplier bank record.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/17-invoice-exception-triage.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/17-invoice-exception-triage)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 18 · L004 · Autonomy A1</p>

### Evidence pack builder

Draft an index for one synthetic evidence pack. The evidence pack approver records the exact item list and the redaction decisions. Experiment 12 inventories in-scope items.

<div class="boundary" markdown="1">

<span>The boundary</span>

The index runs locally. Nothing is approved, disclosed, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/18-evidence-pack-builder.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/18-evidence-pack-builder)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 19 · L006 · Privacy · Autonomy A1</p>

### Privacy impact assessment assistant

Draft a DPIA for one synthetic project brief against UK GDPR Article 35 and Articles 22A to 22D. The privacy officer approves the assessment. The project owner accepts residual risk. Experiment 08 proposes identifier redactions.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is approved, signed off, accepted, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/19-privacy-impact-assessment.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/19-privacy-impact-assessment)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 20 · UK04 · Complaints · Autonomy A0</p>

### Complaints root-cause and regulatory MI

Draft management information from one synthetic complaint batch. The complaints owner validates the clusters and the narrative. Every count lists the source record ids. Experiment 02 suggests a financial-services cause. Experiment 08 proposes identifier redactions.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is validated, submitted, published, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/20-complaints-root-cause-mi.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/20-complaints-root-cause-mi)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 21 · Q009 · IT service desk · Autonomy A1</p>

### IT service desk

Draft a reading of one synthetic IT ticket from a fixed knowledge base. The member of staff confirms a device change. Password resets, MFA changes, and access grants go to an analyst. Experiment 08 counts UK identifiers.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is reset, granted, executed, written, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/21-it-service-desk.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/21-it-service-desk)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 22 · UK07 · Financial crime · Autonomy A1</p>

### On-chain alert investigator and SAR narrative drafter

Draft an internal timeline and a SAR narrative from one synthetic on-chain alert. The nominated officer decides whether to file. Experiment 10, Experiment 16, and Experiment 08 can be called. Nothing is written for the customer.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is filed, requested as a defence, frozen, moved, or told to a customer.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/22-onchain-alert-sar-drafter.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/22-onchain-alert-sar-drafter)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 23 · UK08 · Financial promotions · Autonomy A0</p>

### Cryptoasset financial promotions pre-checker

Draft a checklist for one synthetic cryptoasset promotion. The section 21 approver signs off. Experiment 08 proposes identifier redactions. Nothing is approved, published, or rewritten.

<div class="boundary" markdown="1">

<span>The boundary</span>

The checklist runs locally. Nothing is approved, published, rewritten, or recorded as a compliance opinion.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/23-crypto-financial-promotions-prechecker.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/23-crypto-financial-promotions-prechecker)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 24 · G001 · Autonomy A1</p>

### Agent use-case intake

Take one proposed agent through a structured intake and draft a classification for the governance team. Suggested autonomy stays A0, A1, or A2. Experiments 14, 19, and 03 are called. A request for A3 is out of scope.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. The governance team approves or changes the classification. Nothing is approved or provisioned.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/24-agent-use-case-intake.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/24-agent-use-case-intake)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 25 · G003 · Governance · Autonomy A0</p>

### Instruction quality reviewer

Score one system prompt, SKILL.md, or topic prompt against a fixed checklist. The agent owner approves prompt changes. Experiment 03 can draft an unapproved manifest skeleton. Experiment 14 can cross-check a structured use case.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is edited, applied, approved, or deployed.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/25-instruction-quality-reviewer.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/25-instruction-quality-reviewer)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 26 · G004 · Governance · Autonomy A0</p>

### Skill selection evaluator

Score whether a labelled utterance would select the right skill or topic. The maintainer validates routing tests. Experiment 25 reads each skill file. Experiments 03 and 14 can be called.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is edited, applied, validated, or deployed.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/26-skill-selection-evaluator.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/26-skill-selection-evaluator)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 27 · G005 · Governance · Autonomy A0</p>

### Tool contract review

Score one tool or action contract against a fixed checklist. The security/API owner approves the contract. Experiment 03 can draft an unapproved manifest skeleton. Experiment 14 can cross-check a structured use case. Experiment 25 can score instruction text without changing the contract score.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. The contract is not modified, the policy is not published, and nothing is deployed.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/27-tool-contract-review.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/27-tool-contract-review)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 28 · G006 · Governance · Autonomy A0</p>

### Prompt injection test agent

Run a versioned suite of synthetic prompt-injection fixtures against a sandbox target and draft a findings report mapped to pinned OWASP titles. A security reviewer assesses the findings. Experiments 08, 25, and 03 can be called in the sandbox.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is assessed, remediated, published, or aimed at production.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/28-prompt-injection-test.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/28-prompt-injection-test)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 29 · G007 · Governance · Autonomy A0</p>

### Groundedness evaluation agent

Score each claim in a synthetic Q&A bundle against the passages the agent was shown. The evaluation owner approves thresholds and any pass or fail release. The Microsoft Foundry groundedness evaluator is described and not called.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Thresholds are not approved, a release is not recorded, and Foundry is not called.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/29-groundedness-evaluation.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/29-groundedness-evaluation)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 30 · G008 · Governance · Autonomy A1</p>

### Agent regression test generator

Draft regression cases from one synthetic manifest, skill files, a tool contract, and failure or change notes. The maintainer approves the tests and any pull request. Duplicates are skipped. Each drafted case keeps a trace. A Foundry-shaped queries file is not uploaded.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is merged, pushed, approved, or written into the agent under test.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/30-agent-regression-test-generator.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/30-agent-regression-test-generator)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 31 · G009 · FinOps · Autonomy A0</p>

### Agent cost and capacity

Draft per-agent cost, unit cost per case, a flat forecast, and quota headroom from synthetic usage and a rate card. The FinOps owner validates the rates and the forecast.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is validated, and no quota, budget, or subscription is changed.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/31-agent-cost-capacity.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/31-agent-cost-capacity)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 32 · H009 · HR · Autonomy A1</p>

### Employee case intake

Propose a category, an urgency flag, a statutory or Acas time reference, and a route for one synthetic HR case. An HR officer confirms the classification and the routing. The narrative is not stored.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is decided, no one is contacted, and the HR system is not written.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/32-employee-case-intake.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/32-employee-case-intake)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 33 · UK09 · Casework · Autonomy A0</p>

### Evidence and case-bundle summariser

Draft an extractive reading of one synthetic case bundle. Every sentence carries a pinpoint citation. The decision-maker reviews every cited sentence.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is decided, disclosed, or accepted as a case outcome.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/33-case-bundle-summariser.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/33-case-bundle-summariser)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 34 · UK10 · SEND · Autonomy A1</p>

### EHCP draft assembler

File synthetic SEND advice under the regulation 12 section headings. Each placed line cites the report it came from. Gaps, conflicts, and unsupported statements are flagged. The caseworker authors the final education, health and care plan.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is decided, section I stays blank, and nothing is sent. A local copy needs caseworker sign-off.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/34-ehcp-draft-assembler.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/34-ehcp-draft-assembler)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 35 · B007 · General insurance · Autonomy A1</p>

### Claims document triage

Draft a reading of one synthetic FNOL pack. Quoted lines, one policy pointer, and prompts for the handler to check. A scorecard covers faithfulness, completeness, and unsupported coverage statements. The claims handler approves the class.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is accepted, declined, or settled. Nothing is told to the customer. Nothing is written to a claims system.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/35-claims-document-triage.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/35-claims-document-triage)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 36 · B005 · Records · Autonomy A0</p>

### Cross-source validation

Compare the same fact across synthetic source documents. Dates, amounts, postcodes, company numbers, and names are normalised by a fixed rule. The reviewer resolves every material discrepancy.

<div class="boundary" markdown="1">

<span>The boundary</span>

The list runs locally. No source is chosen, no record is edited, and no one is contacted.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/36-cross-source-validation.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/36-cross-source-validation)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 37 · B006 · Insurance · Autonomy A0</p>

### Underwriting submission summary

Draft a cited summary of one synthetic broker submission. Every stated fact carries a pinpoint citation. A missing field is not stated. The underwriter owns coverage and price.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is accepted or declined, no price is suggested, the broker is not contacted, and the underwriting system is not written.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/37-underwriting-submission-summary.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/37-underwriting-submission-summary)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 38 · B008 · Insurance · Autonomy A0</p>

### Policy wording comparison

Compare two or more synthetic policy wordings. Every stated clause carries a pinpoint citation. A topic that one wording does not state is not stated. A wording specialist validates every interpretation.

<div class="boundary" markdown="1">

<span>The boundary</span>

The comparison runs locally. Nothing is ranked as more favourable, nothing is recommended, no endorsement is drafted, the broker is not contacted, and a policy administration system is not written.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/38-policy-wording-comparison.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/38-policy-wording-comparison)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 39 · B009 · Credit · Autonomy A1</p>

### Credit memo drafting

Draft a cited credit memo from one synthetic pack. Every stated figure carries a pinpoint citation. A missing section is not stated. The credit officer owns the recommendation and every approval.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is approved or declined, no limit is set, the customer and the bureau are not contacted, no core system is posted, and no SAR is filed.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/39-credit-memo-drafting.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/39-credit-memo-drafting)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 40 · C001 · Customer service · Autonomy A1</p>

### Customer self-service

Answer one synthetic enquiry from a fixed knowledge base, explain the next step, and prepare an address or appointment draft for confirmation. A person is always offered.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is written to an account, no payment is taken, no complaint is closed, and no message is sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/40-customer-self-service.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/40-customer-self-service)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 41 · C002 · Customer service · Autonomy A0</p>

### Case summary

Draft a cited reading of one synthetic contact-centre case. Every sentence names its event, paragraph, and line. The service representative checks accuracy.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. The customer is not contacted, the case record is not changed, and no complaint is closed.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/41-case-summary.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/41-case-summary)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 42 · C003 · Customer service · Autonomy A1</p>

### Case routing assistant

Propose a queue, a priority, and a reason for one synthetic case. Vulnerability and statutory-clock cases stay with a person. The adviser confirms before any reroute.

<div class="boundary" markdown="1">

<span>The boundary</span>

The proposal runs locally. Nothing is rerouted, closed, or escalated, and a routing rule is not edited.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/42-case-routing-assistant.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/42-case-routing-assistant)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 43 · C004 · Customer service · Autonomy A1</p>

### Response drafting

Draft a customer response from one synthetic case and approved snippets. The representative reviews the text and sends it.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is sent, no case is written, and no redress is offered.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/43-response-drafting.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/43-response-drafting)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 44 · C005 · Customer service · Autonomy A0</p>

### Knowledge gap detector

Flag likely gaps, stale articles, and conflicts in one synthetic pack. The knowledge manager confirms the gaps.

<div class="boundary" markdown="1">

<span>The boundary</span>

The review runs locally. Nothing is published or edited, and no article is chosen as the winner.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/44-knowledge-gap-detector.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/44-knowledge-gap-detector)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 45 · C007 · Customer service · Autonomy A0</p>

### Service entitlement explainer

Explain what an approved table says about one synthetic service plan. Quote the clause. Show uncertainty. A person decides a disputed entitlement.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is granted, refused, or changed, and no message is sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/45-service-entitlement-explainer.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/45-service-entitlement-explainer)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 46 · C008 · Customer service · Autonomy A0</p>

### Field visit preparation

Assemble a pre-visit brief from one synthetic work order, asset history, site access notes, and safety records. The technician confirms the asset and the safety context.

<div class="boundary" markdown="1">

<span>The boundary</span>

The brief runs locally. Nothing is scheduled, dispatched, or closed, and a safety hold is not cleared.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/46-field-visit-preparation.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/46-field-visit-preparation)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 47 · C009 · Customer service · Autonomy A1</p>

### Work order completion

Turn visit notes, photo descriptions, and parts used into a draft completion record. The technician approves every field before the stub write.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. The stub is the returned JSON. Nothing is closed, charged, ordered, or sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/47-work-order-completion.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/47-work-order-completion)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 48 · C010 · Customer service · Autonomy A0</p>

### Customer sentiment evidence

Produce an evidence pack from one synthetic batch of complaints, survey free text, contact notes, and reviews. The analyst confirms the sample frame and the limitations.

<div class="boundary" markdown="1">

<span>The boundary</span>

The pack runs locally. Nothing is published, no customer is contacted, and no conclusion is made about an individual.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/48-customer-sentiment-evidence.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/48-customer-sentiment-evidence)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 49 · M009 · Microsoft 365 · Autonomy A1</p>

### Records classification

Propose a file-plan category, a retention entry, a disposal action, a security marking, and personal-data indicators for one synthetic document. The records manager confirms every field.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is deleted, disposed of, moved, or downgraded, and a label is not applied in a tenant.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/49-records-classification.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/49-records-classification)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 50 · M001 · Microsoft 365 · Autonomy A1</p>

### SharePoint knowledge curator

Propose curation actions for one synthetic SharePoint snapshot: missing or inconsistent metadata, duplicates, stale or orphaned pages, and broken links. The site owner approves every metadata change and every publishing action.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is deleted, unpublished, moved, or given new permissions, and SharePoint is not called.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/50-sharepoint-knowledge-curator.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/50-sharepoint-knowledge-curator)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 51 · M002 · Microsoft 365 · Autonomy A0</p>

### Teams channel digest

Produce a read-only digest of synthetic Teams channel messages once the user confirms the channels and the period. Every point quotes the message it came from.

<div class="boundary" markdown="1">

<span>The boundary</span>

The digest runs locally. Nothing is posted, replied to, or forwarded, and no judgement is made about a named person.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/51-teams-channel-digest.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/51-teams-channel-digest)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 52 · M004 · Microsoft 365 · Autonomy A1</p>

### Word proposal drafting

Draft a cited bid response from one synthetic invitation and an approved library. The author accepts the complete draft before it is used anywhere.

<div class="boundary" markdown="1">

<span>The boundary</span>

The draft runs locally. Nothing is submitted, sent, or uploaded, and a price or a certificate is not invented.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/52-word-proposal-drafting.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/52-word-proposal-drafting)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 53 · M005 · Microsoft 365 · Autonomy A1</p>

### PowerPoint narrative builder

Propose a cited slide outline from one synthetic briefing, an approved figures sheet, and a short policy extract. The presenter approves the outline and every citation before any slide file is produced.

<div class="boundary" markdown="1">

<span>The boundary</span>

The outline runs locally. Nothing is published, sent, or shared, and a figure, a logo, a customer, or an outcome is not invented.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/53-powerpoint-narrative-builder.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/53-powerpoint-narrative-builder)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 54 · M006 · Microsoft 365 · Autonomy A0</p>

### Excel assumption review

Review one synthetic workbook after the model owner confirms the ranges and the formulas. The report names literals, broken references, and a computed sensitivity.

<div class="boundary" markdown="1">

<span>The boundary</span>

The review runs locally. The workbook is not edited, no assumption is judged, and no benchmark is invented.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/54-excel-assumption-review.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/54-excel-assumption-review)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 55 · M007 · Microsoft 365 · Autonomy A0</p>

### OneDrive document finder

Rank files inside locations the requesting user has confirmed. Each hit carries the reason, the location, the last modified date, and the sensitivity label.

<div class="boundary" markdown="1">

<span>The boundary</span>

The list runs locally. Nothing outside the confirmed locations is listed, and nothing is moved, deleted, shared, or given new permissions.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/55-onedrive-document-finder.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/55-onedrive-document-finder)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 56 · M008 · Microsoft 365 · Autonomy A1</p>

### Intranet content freshness

Review one synthetic intranet inventory. The report names overdue pages, withdrawn or superseded guidance, broken or stale links and contacts, pages with no current owner, and likely duplicates.

<div class="boundary" markdown="1">

<span>The boundary</span>

The named content owner approves each task. The agent does not edit, publish, unpublish, delete, reassign an owner, or message staff.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/56-intranet-content-freshness.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/56-intranet-content-freshness)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 57 · M010 · Microsoft 365 · Autonomy A1</p>

### Collaboration space onboarding

Explain one synthetic Teams and SharePoint space and draft who should join, as a member or an owner, internal or guest.

<div class="boundary" markdown="1">

<span>The boundary</span>

The workspace owner approves membership on a separate object. Owner rights and guest access each need their own boolean. The sample does not call Microsoft Graph or share a file or a link externally.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/57-collaboration-space-onboarding.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/57-collaboration-space-onboarding)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 58 · H001 · HR · Autonomy A0</p>

### Employee handbook

Answer one question from the handbook version HR has approved and that is in force on the date asked about. The section and the effective date are cited. A gap is stated. A personal case goes to a named person.

<div class="boundary" markdown="1">

<span>The boundary</span>

The answer runs locally. It does not decide an individual's entitlement, and it does not treat a word in the question as HR's approval of a source.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/58-employee-handbook.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/58-employee-handbook)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 59 · H002 · HR · Autonomy A1</p>

### New starter guide

Draft a checklist for the role on the synthetic directory, and answer a how-do-I question with the section and the effective date. Equipment, accounts, access, and training stay proposals.

<div class="boundary" markdown="1">

<span>The boundary</span>

The line manager approves that exact checklist before it is shared. The agent does not request equipment, create an account, grant access, enrol training, or collect special-category data.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/59-new-starter-guide.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/59-new-starter-guide)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 60 · H003 · HR · Autonomy A0</p>

### Manager one-to-one preparation

Draft a short prep note from the previous notes, objectives, shared updates, and calendar items a line manager has already selected. Each line is cited. Open questions sit beside those lines.

<div class="boundary" markdown="1">

<span>The boundary</span>

The note runs locally. It does not rate performance, compare employees, or read a mailbox or a chat. A distress sign is flagged for the manager, with an HR and employee-assistance route, and is not a routine agenda item.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/60-manager-one-to-one-prep.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/60-manager-one-to-one-prep)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 61 · H004 · HR · Autonomy A1</p>

### Learning path planner

Draft a sequenced learning plan from a synthetic course catalogue and the goals the employee states. Each step cites a catalogue entry, or the result says no suitable course is in the catalogue.

<div class="boundary" markdown="1">

<span>The boundary</span>

The employee and their manager both approve that plan id. The agent does not enrol, book, or spend, and it does not infer ability from a protected characteristic.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/61-learning-path-planner.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/61-learning-path-planner)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 62 · H005 · HR · Autonomy A0</p>

### Internal mobility explorer

Explain which open vacancies look relevant to the experience an employee states. Each row cites the vacancy and the HR eligibility rule, or the result says eligibility is unclear.

<div class="boundary" markdown="1">

<span>The boundary</span>

HR validates eligibility. The agent does not apply, nominate, shortlist, or contact anyone, and it does not share the employee's interest with their manager or with recruiters.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/62-internal-mobility-explorer.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/62-internal-mobility-explorer)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 63 · H006 · HR · Autonomy A0</p>

### Leave policy explainer

Explain a synthetic leave policy beside the UK statutory baseline. The answer quotes the section, its effective date, and the statutory source.

<div class="boundary" markdown="1">

<span>The boundary</span>

The explanation is not an entitlement. HR or the line manager decides. The agent does not book leave, record leave, or calculate pay.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/63-leave-policy-explainer.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/63-leave-policy-explainer)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 64 · H007 · HR · Autonomy A0</p>

### Job description quality checker

Flag potentially exclusionary wording, a missing salary or location, and an essential criterion that is not linked to a duty. Each prompt has a reason and a suggested alternative.

<div class="boundary" markdown="1">

<span>The boundary</span>

The recruiter accepts or rejects each suggestion and writes the final wording. An occupational requirement or positive action is routed to HR. The agent does not publish, post, or send, and it does not score candidates.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/64-job-description-quality.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/64-job-description-quality)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 65 · H008 · HR · Autonomy A1</p>

### Interview pack builder

Draft questions tied to each essential criterion, a behaviourally anchored rubric, adjustment prompts for the invitation, and the guide's note-taking rules.

<div class="boundary" markdown="1">

<span>The boundary</span>

The recruiter approves the questions and the rubric before the pack is for use. A health question or an occupational requirement is routed to HR. The agent does not contact candidates, schedule interviews, score or rank anyone, or make a hiring decision.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/65-interview-pack-builder.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/65-interview-pack-builder)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 66 · H010 · HR · Autonomy A0</p>

### Workforce skills inventory

Propose skills from evidence an employee supplied, each with a cited snippet, a confidence band, and a state that needs employee confirmation.

<div class="boundary" markdown="1">

<span>The boundary</span>

The employee confirms, rejects, or corrects each skill. HR validates only after that step. The agent does not write to an HR system, rate performance, or feed pay, promotion, redundancy, or disciplinary decisions.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/66-workforce-skills-inventory.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/66-workforce-skills-inventory)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 67 · L001 · Legal · Autonomy A0</p>

### Contract clause review

Quote limitation of liability, indemnities, processor terms, termination, governing law, intellectual property, confidentiality, and auto-renewal against a clause playbook.

<div class="boundary" markdown="1">

<span>The boundary</span>

The lawyer owns the interpretation. The agent quotes deviations and says not found. It does not give legal advice, redline, accept terms, sign, or send.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/67-contract-clause-review.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/67-contract-clause-review)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 68 · L002 · Legal · Autonomy A0</p>

### Regulatory change briefing

Draft a briefing from one pinned synthetic regulator notice: the quoted change, the dates, and the registered policies that might be affected.

<div class="boundary" markdown="1">

<span>The boundary</span>

The compliance owner validates applicability. The agent quotes the change and says not stated or not found. It does not decide that a change applies, change a policy, or send.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/68-regulatory-change-briefing.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/68-regulatory-change-briefing)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 69 · L003 · Assurance · Autonomy A0</p>

### Policy control mapping

Propose which policy sentence supports which internal control, with the verbatim quote, the clause reference, the control id, a rationale, and a confidence band.

<div class="boundary" markdown="1">

<span>The boundary</span>

The control owner approves each mapping. The agent says no evidence found when a control has no sentence. It does not mark a control as met, close a gap, edit a policy, or write to a GRC system.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/69-policy-control-mapping.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/69-policy-control-mapping)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 70 · L005 · Procurement · Autonomy A1</p>

### Conflict-of-interest intake

Draft a structured declaration from a staff member's note, a synthetic supplier list, a synthetic procurement register, and a synthetic directory. Missing detail is asked for. A live procurement link is highlighted for the ethics team.

<div class="boundary" markdown="1">

<span>The boundary</span>

The declarant confirms the exact draft before it is written to a synthetic staging store. The ethics or procurement team decides disposition and mitigation. The agent does not decide that a conflict exists, clear, exclude, or approve anyone, or send.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/70-conflict-of-interest-intake.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/70-conflict-of-interest-intake)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 71 · L007 · Records · Autonomy A0</p>

### Data retention decision support

Explain which pinned retention line appears to apply, the indicative date from the trigger, and the questions the records owner still has to answer.

<div class="boundary" markdown="1">

<span>The boundary</span>

The records or legal owner decides retention, disposal, transfer, and hold. The agent does not delete, move, relabel, archive, or send, and it does not suggest disposal for a legal hold or an open FOI, SAR, litigation, or inquiry.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/71-data-retention-decision-support.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/71-data-retention-decision-support)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 72 · L008 · Legal · Autonomy A1</p>

### Compliance obligation register

Draft obligation records from pinned synthetic extracts and a synthetic register. Each record quotes the provision, shows a diff, and names a proposed owner from the directory.

<div class="boundary" markdown="1">

<span>The boundary</span>

The named compliance owner approves the exact change before a synthetic staging row is written. The agent does not treat the law as final advice, assign accountability, or send.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/72-compliance-obligation-register.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/72-compliance-obligation-register)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 73 · L009 · Assurance · Autonomy A1</p>

### Control testing assistant

Propose a seeded sample and a draft working paper from a synthetic control library, a synthetic evidence population, and a synthetic directory. Exceptions cite the evidence id. The tester decides the result.

<div class="boundary" markdown="1">

<span>The boundary</span>

The named tester approves the exact draft before a synthetic staging write. The tester validates the evidence and decides the result. The agent does not pass or fail a control, close a finding, or send.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/73-control-testing-assistant.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/73-control-testing-assistant)

</div>

</article>

<article class="exp-card" markdown="1">

<p class="card-kicker"><span class="status status-available">Available</span> · Experiment 75 · V009 · Public services · Autonomy A0</p>

### Benefits information assistant

Answer a general question about what a benefit is, how to apply, what evidence is usually needed, and where to get independent advice. Every answer cites the pinned page and its review date.

<div class="boundary" markdown="1">

<span>The boundary</span>

The assistant does not decide eligibility, estimate an entitlement, or calculate an award. A human adviser route is always offered. The resident approves the exact summary before it is staged. Nothing is sent.

</div>

<div class="card-links" markdown="1">

[Read the briefing](experiments/75-benefits-information-assistant.md)
[Source](https://github.com/rahul-bachina/copilot-agent-experiments/tree/main/experiments/75-benefits-information-assistant)

</div>

</article>

</div>

<p class="note">Available means the starter is in the repository and the briefing says what you can run. It does not mean a tenant is configured, or that a live model has been scored.</p>

<div class="section-heading" markdown="1">

<div markdown="1">

<p class="eyebrow">Roadmap</p>

## Planned experiments

</div>

<p>Every name that was on this list now has a briefing. The roadmap keeps the cards.</p>

</div>

<p class="note"><a href="roadmap/">Open the roadmap</a>. B004, B005, B006, B007, B008, B009, F004, G001, G003, G004, G005, G006, G007, G008, G009, G010, H009, L004, L006, Q009, UK01, UK02, UK03, UK04, UK05, UK06, UK07, UK08, M003, V006, V010, O001, O005, O008, UK09, UK10, C001, C002, C003, C004, C005, C007, C008, C009, C010, M009, M001, M002, M004, M005, M006, M007, M008, M010, H001, H002, H003, H004, H005, H006, H007, H008, H010, L001, L002, L003, L005, L007, L008, and L009 now have briefings. V009 is Experiment 75. Nothing on this list is still only a name.</p>

<section class="principles" markdown="1">

<div class="section-heading" markdown="1">

<div markdown="1">

<p class="eyebrow">Governance</p>

## The limit is part of the design

</div>

<p>Every starter has a permissions manifest, named approval points, and a way to switch it off.</p>

</div>

<div class="principle-grid" markdown="1">

<article class="principle-card" markdown="1">

### Human approval

Consequential actions need a named person, or they are switched off. These starters switch them off.

</article>

<article class="principle-card" markdown="1">

### Least privilege

The manifest lists what may be read, and what must never be read. Writes and sends are separate switches. Autonomy is A0, A1, or A2.

</article>

<article class="principle-card" markdown="1">

### Synthetic data

Samples and smoke tests use invented text. Live cases do not belong in this repository.

</article>

<article class="principle-card" markdown="1">

### UK GDPR and ATRS

The manifest is a prompt for the organisation's own assessment. It is not a finished DPIA, and this site does not submit an ATRS record.

</article>

</div>

<p class="note"><a href="governance.md">Read the governance brief</a>.</p>

</section>

## Before you rely on a page

- These pages describe the repository as it stood on 24 October 2026, except the Experiment 08, Experiment 09, and Experiment 10 briefings, which were checked on 26 October 2026, and the Experiment 11, Experiment 12, Experiment 13, Experiment 14, Experiment 15, and Experiment 16 briefings, which were checked on 27 October 2026, and the Experiment 17, Experiment 18, and Experiment 19 briefings, which were checked on 28 October 2026, and the Experiment 20, Experiment 21, and Experiment 22 briefings, which were checked on 29 October 2026, and the Experiment 23, Experiment 24, and Experiment 25 briefings, which were checked on 30 October 2026, and the Experiment 26, Experiment 27, and Experiment 28 briefings, which were checked on 2 November 2026, and the Experiment 29, Experiment 30, and Experiment 31 briefings, which were checked on 3 November 2026, and the Experiment 32 briefing, which was checked on 4 November 2026, and the Experiment 33 briefing, which was checked on 4 November 2026,, and the Experiment 34 briefing, which was checked on 4 November 2026, and the Experiment 35 briefing, which was checked on 5 November 2026, and the Experiment 36 briefing, which was checked on 5 November 2026, and the Experiment 37 briefing, which was checked on 5 November 2026, and the Experiment 38 briefing, which was checked on 6 November 2026. If a page and an `agent-manifest.yaml` disagree, the manifest is the control.
- There are no client names or testimonials. Experiment 06 records a design for measuring time with a stopwatch. The figures in its smoke report are synthetic fixture arithmetic, not a study of staff.
- A smoke test checks that code runs on synthetic text. It is not a model score.
- This site is not legal advice, a data protection impact assessment, or an ATRS submission.
- Contact addresses on `example.gov.uk` and `example.com` are placeholders.
- Experiment 01 is for public bodies. Experiments 02 and 04 are for FCA-regulated firms. Experiment 03 drafts assurance records and does not decide that a body is in the ATRS mandatory scope. Experiment 04 does not decide that a firm is ready for authorisation. Experiment 05 is for social landlords in England. Experiment 06 quotes approved corporate policies, refuses clinical questions, and does not decide entitlement. Experiment 07 drafts consultation themes for a public body or a charity. It does not decide the policy and it does not publish the analysis. Experiment 08 proposes redactions of UK identifiers for another experiment to call. A privacy reviewer approves the proposal before any release. The gateway does not release the text and does not describe it as anonymised. Experiment 09 drafts one correspondence reply for a department, an agency, or a council. It does not send, and it does not invent a line to take. Experiment 10 triages one synthetic cryptoasset transfer for an analyst at an FCA-regulated firm. It does not hold, return, release, file, or contact a counterparty. Experiment 11 drafts a commencement and evidence note for an HR lead at a UK employer. It does not decide that the employer took all reasonable steps, and it does not discipline, dismiss, publish, or send. Experiment 12 inventories one synthetic batch of text files. The user confirms the files and the purpose, and an intake reviewer decides the routing suggestion. It does not queue, release, or send, and it does not decide the underlying matter. Experiment 13 drafts a contact-centre reply for a local authority from a fixed catalogue, or a handover. It does not decide eligibility, send a message, or write a case. Experiment 14 drafts platform options for one proposed agent. The architect confirms every option. It does not select a platform, approve a manifest, or deploy. Experiment 15 flags possible safeguarding, self-harm, financial hardship, and deadline indicators in one synthetic letter. The duty officer reviews every flag. It does not close, deprioritise, send, or label a person as vulnerable. Text goes through Experiment 08 before any model call. Experiment 16 drafts a Money Laundering Regulations 2017 checklist for one synthetic customer file. The KYC reviewer confirms the documents and the purpose. It does not approve, reject, onboard, assign a risk rating, file a report, or send. Experiment 17 drafts a resolution for one synthetic invoice that failed a 2-way or 3-way match. The AP reviewer approves the resolution. A bank-detail change is routed to a separate verifier. It does not post, approve, hold, or pay the invoice, and it does not change supplier bank details. Experiment 18 drafts an index for one synthetic evidence pack. The evidence pack approver records the exact item list and the redaction decisions. It does not apply an exemption, disclose, write a production record, or send. Experiment 19 drafts a data protection impact assessment for one synthetic project brief. The privacy officer approves the assessment and the project owner accepts residual risk. It does not approve, reject, sign off, accept residual risk, or send a consultation. Experiment 20 drafts management information from one synthetic complaint batch for a Consumer Duty board report, a Housing Ombudsman Code self-assessment, or Ofgem complaints reporting. The complaints owner validates the clusters and the narrative. It does not present the draft as a regulatory return, confirm compliance, submit, publish, or send. Experiment 21 drafts a reading of one synthetic IT ticket. The member of staff confirms a device change. An analyst takes a password reset, an MFA change, or an access grant. It does not reset, grant, execute, write a ticket, or send. Experiment 22 drafts an internal timeline and a SAR narrative for one synthetic on-chain alert. The nominated officer decides whether section 330 or section 331 is met and whether to file. It does not file, request a defence, freeze or move a cryptoasset, or draft customer-facing content. Experiment 23 drafts a checklist for one synthetic cryptoasset promotion. The section 21 approver signs off. It does not approve, publish, rewrite, or give a compliance opinion. Experiment 24 drafts a classification of one proposed agent. The governance team approves or changes the classification. It does not approve the use case, provision an agent, decide that a DPIA is required, or decide ATRS mandatory scope. Experiment 25 scores one system prompt, SKILL.md, or topic prompt against a fixed checklist. The agent owner approves prompt changes. It does not edit the file, apply the diff, approve a manifest, or deploy. Experiment 26 scores whether a labelled utterance would select the right skill or topic, and proposes a description diff. The maintainer validates routing tests. It does not edit, apply, validate, or deploy. Experiment 27 scores one tool or action contract against a fixed checklist. The security/API owner approves the contract. It does not modify the contract, publish an API Management policy, or deploy. Experiment 28 runs a versioned suite of synthetic prompt-injection fixtures against a sandbox target and drafts findings mapped to pinned OWASP titles. A security reviewer assesses the findings. It does not target production, assess, remediate, publish, or call Microsoft Foundry. Experiment 29 scores each claim in a synthetic Q&A bundle against the passages the agent was shown. The evaluation owner approves thresholds and any pass or fail release. It does not approve a threshold, record a release, or call the Microsoft Foundry groundedness evaluator. Experiment 30 drafts regression cases from a synthetic manifest, skill files, a tool contract, and failure or change notes. The maintainer approves the tests and any pull request. It does not merge, push, or edit the agent under test. Experiment 31 drafts cost, unit cost, a flat forecast, and quota headroom from one synthetic usage file and a rate card. The FinOps owner validates the rates and the forecast. It does not change a quota, a budget, or a subscription, and it does not store a Microsoft price. Experiment 32 proposes a category, an urgency flag, a statutory or Acas time reference, and a route for one synthetic HR case. An HR officer confirms the classification and the routing. It does not decide an outcome, contact the employee or a manager, or write to an HR system. Experiment 33 drafts an extractive reading of one synthetic case bundle. Every sentence carries a pinpoint citation. The decision-maker reviews every cited sentence. It does not recommend an outcome, make a disclosure decision, make a credibility finding, or call Microsoft Foundry. Experiment 34 files synthetic SEND advice under the regulation 12 section headings. Each placed line cites the report it came from. The caseworker authors the final education, health and care plan. It does not decide needs, provision, placement, or outcomes, and it does not send the draft. Experiment 35 drafts a reading of one synthetic FNOL pack, with coverage pointers, inconsistency prompts, and a scorecard. The claims handler approves the class. It does not accept, decline, settle, tell the customer, or write a claims system. Experiment 36 compares the same fact across synthetic source documents and classifies each difference with a fixed rule. The reviewer resolves every material discrepancy. It does not choose which source is right, edit a record, contact anyone, or query a live register. Experiment 37 drafts a cited summary of one synthetic broker submission. A missing field is not stated. The underwriter owns coverage and price. It does not accept or decline, suggest a price or terms, contact the broker, or write to an underwriting system. Experiment 38 compares two or more synthetic policy wordings. Every stated clause carries a pinpoint citation. A topic that one wording does not state is not stated. A wording specialist validates every interpretation. It does not rank favourability, recommend buy, sell, or renew, draft an endorsement, contact a broker, or write to a policy administration system. They are not interchangeable. Experiment 43 drafts a customer response for a representative from one synthetic case and approved snippets. The representative reviews the text and sends it on their own channel. It does not send, write a case, offer redress, or decide that a firm met PRIN 2A.5. The Experiment 43 briefing was checked on 9 November 2026. Experiment 44 flags likely knowledge gaps, stale articles, and conflicts in one synthetic pack for a knowledge manager. The manager confirms the gaps. It does not publish or edit an article, and it does not decide that a firm met PRIN 2A.5. The Experiment 44 briefing was checked on 10 November 2026. Experiment 45 explains one synthetic service plan from an approved entitlement table. It quotes the clause and routes a disputed entitlement to a person. It does not grant, refuse, or change the entitlement, and it does not decide that a firm met PRIN 2A.5. The Experiment 45 briefing was checked on 10 November 2026. Experiment 49 proposes a file-plan category, a retention entry, a disposal action, a security marking, and personal-data indicators for one synthetic document. The records manager confirms every field. It does not delete, dispose of, move, or downgrade a record, and it does not call Microsoft Purview. The Experiment 49 briefing was checked on 11 November 2026. Experiment 50 proposes curation actions for one synthetic SharePoint snapshot. The site owner approves every metadata change and every publishing action. It does not delete, unpublish, move, or change permissions, and it does not call SharePoint or Microsoft Graph. The Experiment 50 briefing was checked on 12 November 2026. Experiment 58 answers one question from a synthetic employee handbook. HR approves which documents and versions are in scope. It quotes the version in force on the date asked about, or says the handbook does not cover the question, and it routes a personal or sensitive case to a named person. It does not decide an individual's entitlement. The Experiment 58 briefing was checked on 16 November 2026. Experiment 60 drafts a one-to-one prep note from the notes, objectives, shared updates, and calendar items a line manager has selected. It quotes follow-ups with a citation, or flags distress for the manager with an HR and employee-assistance route. It does not rate performance, compare employees, or read a mailbox or a chat. The Experiment 60 briefing was checked on 17 November 2026. Experiment 61 drafts a learning plan from a synthetic course catalogue and the goals an employee states. The employee and their manager both approve the plan id before an enrolment request is recorded. It does not enrol, book, or spend, and it does not infer ability from a protected characteristic. The Experiment 61 briefing was checked on 17 November 2026. Experiment 64 returns prompts on one synthetic job description. The recruiter accepts or rejects each suggestion and writes the final wording. An occupational requirement, positive action, or a health question is routed to HR and is not decided. It does not publish, post, or send, and it does not score candidates. The Experiment 64 briefing was checked on 18 November 2026. Experiment 66 proposes skills from evidence an employee supplied for a skills inventory. The employee confirms, rejects, or corrects each skill, and HR validates only after that step. A small team count is suppressed. It does not write to an HR system, rate performance, or feed pay, promotion, redundancy, or disciplinary decisions. The Experiment 66 briefing was checked on 19 November 2026. Experiment 70 drafts a conflict-of-interest declaration from one synthetic note. The declarant confirms that declaration hash before a synthetic staging row is written. The ethics or procurement team records disposition and mitigation. It does not decide that a conflict exists, clear, exclude, or approve anyone, or send. The Experiment 70 briefing was checked on 20 November 2026. Experiment 75 answers a general benefits question from pinned synthetic pages and cites the page and the review date. It does not decide eligibility, estimate an entitlement, calculate an award, complete or submit a claim, or send. The resident approves the exact summary before a synthetic staging write. The Experiment 75 briefing was checked on 24 November 2026.

Nothing in the repository is marked Blueprint or Archived.

| Label | Meaning |
| --- | --- |
| <span class="status status-available">Available</span> | In the repository. The briefing says which parts you can run. A build guide is not a tenant you can import. |
| <span class="status status-blueprint">Blueprint</span> | The design is written down. The runnable agent is not in the repository. |
| <span class="status status-planned">Planned</span> | Named as future work. No date. |
| <span class="status status-archived">Archived</span> | Withdrawn, and kept so the record is still there. |
