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

## Six starters you can read today

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

</div>

<p class="note">Available means the starter is in the repository and the briefing says what you can run. It does not mean a tenant is configured, or that a live model has been scored.</p>

<div class="section-heading" markdown="1">

<div markdown="1">

<p class="eyebrow">Roadmap</p>

## Planned experiments

</div>

<p>Named only. No design, no code, and no date.</p>

</div>

<div class="plan-grid" markdown="1">

<article class="plan-card" markdown="1">

<p class="card-kicker"><span class="status status-planned">Planned</span> · V010</p>

### Consultation themes

Not started. It would group themes from a consultation. There is no consultation text and no method.

</article>

</div>

<p class="note"><a href="roadmap/">Open the roadmap</a>. G010, UK01, UK02, and M003 now have briefings. V010 is still only a name.</p>

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

- These pages describe the repository as it stood on 24 October 2026. If a page and an `agent-manifest.yaml` disagree, the manifest is the control.
- There are no client names or testimonials. Experiment 06 records a design for measuring time with a stopwatch. The figures in its smoke report are synthetic fixture arithmetic, not a study of staff.
- A smoke test checks that code runs on synthetic text. It is not a model score.
- This site is not legal advice, a data protection impact assessment, or an ATRS submission.
- Contact addresses on `example.gov.uk` and `example.com` are placeholders.
- Experiment 01 is for public bodies. Experiments 02 and 04 are for FCA-regulated firms. Experiment 03 drafts assurance records and does not decide that a body is in the ATRS mandatory scope. Experiment 04 does not decide that a firm is ready for authorisation. Experiment 05 is for social landlords in England. Experiment 06 quotes approved corporate policies, refuses clinical questions, and does not decide entitlement. They are not interchangeable.

Nothing in the repository is marked Blueprint or Archived.

| Label | Meaning |
| --- | --- |
| <span class="status status-available">Available</span> | In the repository. The briefing says which parts you can run. A build guide is not a tenant you can import. |
| <span class="status status-blueprint">Blueprint</span> | The design is written down. The runnable agent is not in the repository. |
| <span class="status status-planned">Planned</span> | Named as future work. No date. |
| <span class="status status-archived">Archived</span> | Withdrawn, and kept so the record is still there. |
