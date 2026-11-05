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

## Thirty-six starters you can read today

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

<p class="note"><a href="roadmap/">Open the roadmap</a>. B004, B006, B007, F004, G001, G003, G004, G005, G006, G007, G008, G009, G010, H009, L004, L006, Q009, UK01, UK02, UK03, UK04, UK05, UK06, UK07, UK08, M003, V006, V010, O001, O005, O008, UK09, and UK10 now have briefings. Nothing on this list is still only a name.</p>

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

- These pages describe the repository as it stood on 24 October 2026, except the Experiment 08, Experiment 09, and Experiment 10 briefings, which were checked on 26 October 2026, and the Experiment 11, Experiment 12, Experiment 13, Experiment 14, Experiment 15, and Experiment 16 briefings, which were checked on 27 October 2026, and the Experiment 17, Experiment 18, and Experiment 19 briefings, which were checked on 28 October 2026, and the Experiment 20, Experiment 21, and Experiment 22 briefings, which were checked on 29 October 2026, and the Experiment 23, Experiment 24, and Experiment 25 briefings, which were checked on 30 October 2026, and the Experiment 26, Experiment 27, and Experiment 28 briefings, which were checked on 2 November 2026, and the Experiment 29, Experiment 30, and Experiment 31 briefings, which were checked on 3 November 2026, and the Experiment 32 briefing, which was checked on 4 November 2026, and the Experiment 33 briefing, which was checked on 4 November 2026,, and the Experiment 34 briefing, which was checked on 4 November 2026, and the Experiment 35 briefing, which was checked on 5 November 2026, and the Experiment 37 briefing, which was checked on 5 November 2026. If a page and an `agent-manifest.yaml` disagree, the manifest is the control.
- There are no client names or testimonials. Experiment 06 records a design for measuring time with a stopwatch. The figures in its smoke report are synthetic fixture arithmetic, not a study of staff.
- A smoke test checks that code runs on synthetic text. It is not a model score.
- This site is not legal advice, a data protection impact assessment, or an ATRS submission.
- Contact addresses on `example.gov.uk` and `example.com` are placeholders.
- Experiment 01 is for public bodies. Experiments 02 and 04 are for FCA-regulated firms. Experiment 03 drafts assurance records and does not decide that a body is in the ATRS mandatory scope. Experiment 04 does not decide that a firm is ready for authorisation. Experiment 05 is for social landlords in England. Experiment 06 quotes approved corporate policies, refuses clinical questions, and does not decide entitlement. Experiment 07 drafts consultation themes for a public body or a charity. It does not decide the policy and it does not publish the analysis. Experiment 08 proposes redactions of UK identifiers for another experiment to call. A privacy reviewer approves the proposal before any release. The gateway does not release the text and does not describe it as anonymised. Experiment 09 drafts one correspondence reply for a department, an agency, or a council. It does not send, and it does not invent a line to take. Experiment 10 triages one synthetic cryptoasset transfer for an analyst at an FCA-regulated firm. It does not hold, return, release, file, or contact a counterparty. Experiment 11 drafts a commencement and evidence note for an HR lead at a UK employer. It does not decide that the employer took all reasonable steps, and it does not discipline, dismiss, publish, or send. Experiment 12 inventories one synthetic batch of text files. The user confirms the files and the purpose, and an intake reviewer decides the routing suggestion. It does not queue, release, or send, and it does not decide the underlying matter. Experiment 13 drafts a contact-centre reply for a local authority from a fixed catalogue, or a handover. It does not decide eligibility, send a message, or write a case. Experiment 14 drafts platform options for one proposed agent. The architect confirms every option. It does not select a platform, approve a manifest, or deploy. Experiment 15 flags possible safeguarding, self-harm, financial hardship, and deadline indicators in one synthetic letter. The duty officer reviews every flag. It does not close, deprioritise, send, or label a person as vulnerable. Text goes through Experiment 08 before any model call. Experiment 16 drafts a Money Laundering Regulations 2017 checklist for one synthetic customer file. The KYC reviewer confirms the documents and the purpose. It does not approve, reject, onboard, assign a risk rating, file a report, or send. Experiment 17 drafts a resolution for one synthetic invoice that failed a 2-way or 3-way match. The AP reviewer approves the resolution. A bank-detail change is routed to a separate verifier. It does not post, approve, hold, or pay the invoice, and it does not change supplier bank details. Experiment 18 drafts an index for one synthetic evidence pack. The evidence pack approver records the exact item list and the redaction decisions. It does not apply an exemption, disclose, write a production record, or send. Experiment 19 drafts a data protection impact assessment for one synthetic project brief. The privacy officer approves the assessment and the project owner accepts residual risk. It does not approve, reject, sign off, accept residual risk, or send a consultation. Experiment 20 drafts management information from one synthetic complaint batch for a Consumer Duty board report, a Housing Ombudsman Code self-assessment, or Ofgem complaints reporting. The complaints owner validates the clusters and the narrative. It does not present the draft as a regulatory return, confirm compliance, submit, publish, or send. Experiment 21 drafts a reading of one synthetic IT ticket. The member of staff confirms a device change. An analyst takes a password reset, an MFA change, or an access grant. It does not reset, grant, execute, write a ticket, or send. Experiment 22 drafts an internal timeline and a SAR narrative for one synthetic on-chain alert. The nominated officer decides whether section 330 or section 331 is met and whether to file. It does not file, request a defence, freeze or move a cryptoasset, or draft customer-facing content. Experiment 23 drafts a checklist for one synthetic cryptoasset promotion. The section 21 approver signs off. It does not approve, publish, rewrite, or give a compliance opinion. Experiment 24 drafts a classification of one proposed agent. The governance team approves or changes the classification. It does not approve the use case, provision an agent, decide that a DPIA is required, or decide ATRS mandatory scope. Experiment 25 scores one system prompt, SKILL.md, or topic prompt against a fixed checklist. The agent owner approves prompt changes. It does not edit the file, apply the diff, approve a manifest, or deploy. Experiment 26 scores whether a labelled utterance would select the right skill or topic, and proposes a description diff. The maintainer validates routing tests. It does not edit, apply, validate, or deploy. Experiment 27 scores one tool or action contract against a fixed checklist. The security/API owner approves the contract. It does not modify the contract, publish an API Management policy, or deploy. Experiment 28 runs a versioned suite of synthetic prompt-injection fixtures against a sandbox target and drafts findings mapped to pinned OWASP titles. A security reviewer assesses the findings. It does not target production, assess, remediate, publish, or call Microsoft Foundry. Experiment 29 scores each claim in a synthetic Q&A bundle against the passages the agent was shown. The evaluation owner approves thresholds and any pass or fail release. It does not approve a threshold, record a release, or call the Microsoft Foundry groundedness evaluator. Experiment 30 drafts regression cases from a synthetic manifest, skill files, a tool contract, and failure or change notes. The maintainer approves the tests and any pull request. It does not merge, push, or edit the agent under test. Experiment 31 drafts cost, unit cost, a flat forecast, and quota headroom from one synthetic usage file and a rate card. The FinOps owner validates the rates and the forecast. It does not change a quota, a budget, or a subscription, and it does not store a Microsoft price. Experiment 32 proposes a category, an urgency flag, a statutory or Acas time reference, and a route for one synthetic HR case. An HR officer confirms the classification and the routing. It does not decide an outcome, contact the employee or a manager, or write to an HR system. Experiment 33 drafts an extractive reading of one synthetic case bundle. Every sentence carries a pinpoint citation. The decision-maker reviews every cited sentence. It does not recommend an outcome, make a disclosure decision, make a credibility finding, or call Microsoft Foundry. Experiment 34 files synthetic SEND advice under the regulation 12 section headings. Each placed line cites the report it came from. The caseworker authors the final education, health and care plan. It does not decide needs, provision, placement, or outcomes, and it does not send the draft. Experiment 35 drafts a reading of one synthetic FNOL pack, with coverage pointers, inconsistency prompts, and a scorecard. The claims handler approves the class. It does not accept, decline, settle, tell the customer, or write a claims system. Experiment 37 drafts a cited summary of one synthetic broker submission. A missing field is not stated. The underwriter owns coverage and price. It does not accept or decline, suggest a price or terms, contact the broker, or write to an underwriting system. They are not interchangeable.

Nothing in the repository is marked Blueprint or Archived.

| Label | Meaning |
| --- | --- |
| <span class="status status-available">Available</span> | In the repository. The briefing says which parts you can run. A build guide is not a tenant you can import. |
| <span class="status status-blueprint">Blueprint</span> | The design is written down. The runnable agent is not in the repository. |
| <span class="status status-planned">Planned</span> | Named as future work. No date. |
| <span class="status status-archived">Archived</span> | Withdrawn, and kept so the record is still there. |
