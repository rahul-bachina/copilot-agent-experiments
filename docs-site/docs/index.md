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

## Seventeen starters you can read today

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

</div>

<p class="note">Available means the starter is in the repository and the briefing says what you can run. It does not mean a tenant is configured, or that a live model has been scored.</p>

<div class="section-heading" markdown="1">

<div markdown="1">

<p class="eyebrow">Roadmap</p>

## Planned experiments

</div>

<p>Every name that was on this list now has a briefing. The roadmap keeps the cards.</p>

</div>

<p class="note"><a href="roadmap/">Open the roadmap</a>. B004, G010, UK01, UK02, UK03, UK05, UK06, M003, V006, V010, O001, O005, O008, and L004 now have briefings. Nothing on this list is still only a name.</p>

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

- These pages describe the repository as it stood on 24 October 2026, except the Experiment 08, Experiment 09, and Experiment 10 briefings, which were checked on 26 October 2026, the Experiment 11, Experiment 12, Experiment 13, Experiment 14, Experiment 15, and Experiment 16 briefings, which were checked on 27 October 2026, and the Experiment 18 briefing, which was checked on 28 October 2026. If a page and an `agent-manifest.yaml` disagree, the manifest is the control.
- There are no client names or testimonials. Experiment 06 records a design for measuring time with a stopwatch. The figures in its smoke report are synthetic fixture arithmetic, not a study of staff.
- A smoke test checks that code runs on synthetic text. It is not a model score.
- This site is not legal advice, a data protection impact assessment, or an ATRS submission.
- Contact addresses on `example.gov.uk` and `example.com` are placeholders.
- Experiment 01 is for public bodies. Experiments 02 and 04 are for FCA-regulated firms. Experiment 03 drafts assurance records and does not decide that a body is in the ATRS mandatory scope. Experiment 04 does not decide that a firm is ready for authorisation. Experiment 05 is for social landlords in England. Experiment 06 quotes approved corporate policies, refuses clinical questions, and does not decide entitlement. Experiment 07 drafts consultation themes for a public body or a charity. It does not decide the policy and it does not publish the analysis. Experiment 08 proposes redactions of UK identifiers for another experiment to call. A privacy reviewer approves the proposal before any release. The gateway does not release the text and does not describe it as anonymised. Experiment 09 drafts one correspondence reply for a department, an agency, or a council. It does not send, and it does not invent a line to take. Experiment 10 triages one synthetic cryptoasset transfer for an analyst at an FCA-regulated firm. It does not hold, return, release, file, or contact a counterparty. Experiment 11 drafts a commencement and evidence note for an HR lead at a UK employer. It does not decide that the employer took all reasonable steps, and it does not discipline, dismiss, publish, or send. Experiment 12 inventories one synthetic batch of text files. The user confirms the files and the purpose, and an intake reviewer decides the routing suggestion. It does not queue, release, or send, and it does not decide the underlying matter. Experiment 13 drafts a contact-centre reply for a local authority from a fixed catalogue, or a handover. It does not decide eligibility, send a message, or write a case. Experiment 14 drafts platform options for one proposed agent. The architect confirms every option. It does not select a platform, approve a manifest, or deploy. Experiment 15 flags possible safeguarding, self-harm, financial hardship, and deadline indicators in one synthetic letter. The duty officer reviews every flag. It does not close, deprioritise, send, or label a person as vulnerable. Text goes through Experiment 08 before any model call. Experiment 16 drafts a Money Laundering Regulations 2017 checklist for one synthetic customer file. The KYC reviewer confirms the documents and the purpose. It does not approve, reject, onboard, assign a risk rating, file a report, or send. Experiment 18 drafts an index for one synthetic evidence pack. The evidence pack approver records the exact item list and the redaction decisions. It does not apply an exemption, disclose, write a production record, or send. They are not interchangeable.

Nothing in the repository is marked Blueprint or Archived.

| Label | Meaning |
| --- | --- |
| <span class="status status-available">Available</span> | In the repository. The briefing says which parts you can run. A build guide is not a tenant you can import. |
| <span class="status status-blueprint">Blueprint</span> | The design is written down. The runnable agent is not in the repository. |
| <span class="status status-planned">Planned</span> | Named as future work. No date. |
| <span class="status status-archived">Archived</span> | Withdrawn, and kept so the record is still there. |
