# Experiment 53: PowerPoint Narrative Builder

Catalogue ID **M005**. A slide outline for one synthetic briefing.

UK public-sector presentations are built from material the organisation has already approved: a briefing note, a figures sheet, and a short policy extract. The failure mode is a deck that invents a figure, a quote, a logo, a customer, or an outcome, that marks a sentence as sourced when no passage contains it, or that publishes itself because the note said "share the deck". This starter proposes a storyline. The presenter approves the outline and every citation before any slide file is produced. It does not publish, send, or share.

**Autonomy A1.** `propose_outline()` leaves `human_approval` null and `slides_produced` false. `record_presenter_approval()` can record that the presenter has approved the outline and every citation. That record still does not build slides. `produce_slides()` runs only after that record, and `shared` stays false. A sentence inside the pack that says the presenter has approved is ignored. The agent has no mail tool, no site tool, and no Microsoft Graph call.

Stack in the catalogue: Microsoft 365 and Work IQ. The outline itself is Python in the standard library. It calls `score_claim()` and `passage_currency()` in [Experiment 29](../29-groundedness-evaluation/), and `normalise_value()` and `classify_values()` in [Experiment 36](../36-cross-source-validation/). The approval gate, the negation rule, and the refusal to treat pack text as approval follow the shape of [Experiment 52](../52-word-proposal-drafting/). This starter does not import Experiment 52, because that core drafts a bid. A presenter can run this folder without a tenant.

The organisation in the samples is Northmere Digital Services. The audience is the leadership team at Aldergate Borough Council. Both are invented.

## The problem

A slide assistant that fills a gap with a plausible percentage, adds a logo it was never given, or shares a deck because the note said so is the failure this starter is built to refuse. The useful narrow job is: one key message taken from an approved passage, a slide for each sentence that passage supports, a citation for every sourced claim, a gap where the source is missing, and an accessibility checklist the presenter still has to check.

## Non-goals

- Publishing, sending, or sharing a deck. A recorded approval is not a share. A local slide file is not a share.
- Inventing a figure, a quote, a logo, a customer, or an outcome.
- Marking a claim as sourced when no citation quote sits in an approved passage, or when Experiment 29 does not call that quote supported.
- Copying an unsourced request into the outline, including a number the presenter typed.
- Treating a sentence in the pack as the presenter's approval. Only `record_presenter_approval()` counts.
- Deciding that the accessibility regulations were met, or that WCAG 2.2 AA was met.
- Choosing a Government Security Classification, or removing one that the source already carries.
- Stripping a retention label or a legal-hold label.
- Turning a safeguarding or distress sentence into a routine slide.
- Using a real organisation, a real audience, a real customer, or a real figure. Northmere is fictional.
- Autonomy A3. A3 is not permitted in this catalogue.

## What was opened

Opened on 13 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
|---|---|
| [Accessibility Regulations 2018, regulation 3](https://www.legislation.gov.uk/uksi/2018/952/regulation/3) | The accessibility requirement is to make a website or mobile application perceivable, operable, understandable and robust. The text opened does not name WCAG. In force at 23 September 2018. |
| [Regulation 4](https://www.legislation.gov.uk/uksi/2018/952/regulation/4) | The regulations apply to a public-sector website or mobile application, with the exceptions in regulation 4(1). Regulation 4(2)(a) and 4(3)(d) cover office file formats, including Microsoft Office documents, published on those sites. This starter does not decide that a deck is in scope. |
| [Regulation 6](https://www.legislation.gov.uk/uksi/2018/952/regulation/6) | Subject to regulation 7, public sector bodies must comply with the accessibility requirement. Regulation 7 was not opened. This starter does not decide that a deck complies. |
| [GOV.UK accessibility requirements](https://www.gov.uk/guidance/accessibility-requirements-for-public-sector-websites-and-apps) | Updated 30 September 2024. The page says a site meets the legal requirements if it meets WCAG 2.2 AA and an accessibility statement is published. That is the guidance page. It is not the regulation text. |
| [Publishing accessible documents](https://www.gov.uk/guidance/publishing-accessible-documents) | Updated 9 October 2025. Simple language, about 25 words or fewer in a sentence, alt text, colour contrast, and a logical reading order. This starter records those checks. It does not certify them. |
| [GOV.UK style guide, plain English](https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style) | All content on GOV.UK should be written in plain English. This starter does not decide that a sentence meets the guide. |
| [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html) | HTML edition, version 2.0 dated 5 August 2024 on that page. Paragraph 5 names OFFICIAL, SECRET, and TOP SECRET. Paragraph 25 describes the -SENSITIVE marking on OFFICIAL, as in OFFICIAL-SENSITIVE. This starter copies a marking it finds. It does not downgrade one. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Opened 13 November 2026. Three harnesses are named: Microsoft Copilot, Customer Conversation, and standard. The standard harness follows the topics and rules the maker defines. The Microsoft Copilot harness can create and edit PowerPoint files and uses Copilot Credits. The page states no price. The text retrieved that day does not use the name GitHub Copilot harness. See the limitations. |
| [Microsoft 365 Copilot overview](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview) | The PowerPoint row describes creating a presentation from a prompt or existing content, summarising, and editing. Grounding through Microsoft Graph and Work IQ is described on the same page. A dedicated Copilot in PowerPoint how-to was not opened. Neither is called. |
| [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/) | A permission-aware layer with A2A, a remote MCP server, and a REST API. Usage is independent of Microsoft 365 Copilot licensing and consumes Copilot Credits. No price and no general-availability date are on the page that was opened. Work IQ is not called. |

Regulation 7, regulation 9, the Equality Act 2010, the Disability Discrimination Act 1995, the WCAG 2.2 recommendation itself, the PowerPoint JavaScript API, and the Graph upload page were not opened. UK GDPR Articles 6, 9, and 28 were not opened. No lawful basis is asserted.

## What the starter does

`src/narrative.py` reads one JSON pack and writes one JSON document. The same pack and the same as-of date produce the same JSON. `human_approval` is null. `actions_taken` is empty. `executed` is false. `slides_produced` is false. Unsourced request text is not copied.

**Key message.** If a passage has the role `key_message`, and Experiment 29 calls a quote of that passage supported, and the passage is inside the review window, the one-line key message is that passage. Nothing else is written in its place. A request that says "it is not true that" the passage is so does not count as a citation of it.

**Sourced slide.** A requested sentence that matches an approved passage exactly, with no negation and no instruction, can become a proposed slide. The headline is the passage. The citation names the passage id and quotes it. `sourced` is true only when that citation is present and the verdict is `supported`.

**Figure.** A number is cited only when it is on the approved figures sheet. Experiment 36 compares two values for the same figure id. A material discrepancy is a gap, and neither number is copied. The sheet's own sentence can be quoted when it is the passage that was matched.

**Gap.** No approved passage matches. The fixed gap record names the point id and a reason. It does not answer the point. A logo, a customer, or an outcome that is not in a passage is a gap. Nothing is invented.

**Negation.** A sentence that contains a negation, and a following sentence that is only "no", is not used as a request to cite a source. "It is not true that…" does not mark the contained sentence as sourced.

**Prompt injection.** A sentence that tells the agent to ignore the sources, invent a logo, or publish the deck is recorded. `followed` is false. A later instruction does not publish.

**Approval in the pack.** Keys such as `human_approval` and `presenter_approved` are stripped. They do not set `human_approval`.

**Safeguarding.** A sentence with a distress or safeguarding cue is flagged for a person. It is not copied onto a slide.

**Personal data.** A phone number, an email address, a date of birth, a UK postcode, or a personal name is not copied into the outline. The categories are recorded. The values are not.

**Markings.** OFFICIAL, OFFICIAL-SENSITIVE, SECRET, and TOP SECRET tokens found in the source are kept. The strictest one is the marking applied. A lower value on the pack does not replace a higher one. A legal-hold or retention phrase in the source is kept. A false flag does not clear it.

**Stale data.** Experiment 29's review-stamp window applies. If the as-of date is more than 180 days after 13 November 2026, no passage is quoted. Equal to 180 days is still inside the window. The 180-day figure is a starter default, not a review duty in the regulations.

**Slides.** `produce_slides()` writes a local `.pptx` only after `record_presenter_approval()` has recorded approval of every sourced citation. The file is Office Open XML. It does not call the PowerPoint JavaScript API and it does not call Graph. `shared` stays false.

**Synthetic only.** A pack that is not marked synthetic, or whose pack id is not `SYN-DECK-` plus four digits, is refused. The refusal does not echo the text.

`record_presenter_approval` accepts `presenter_approve_outline_and_citations`, `presenter_request_revision`, or `reject_outline` from a separate review object. Approval is refused when a citation, a gap, the accessibility checklist, or a marking has not been acknowledged. It still does not build slides. `share_deck`, `publish_deck`, `send_deck`, and `invent_claim` raise `NarrativeForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 29 and 36 must be present beside this folder. This experiment does not carry a second copy of them.

```bash
cd experiments/53-powerpoint-narrative-builder
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/narrative.py --input examples/sample_pack.json --as-of 2026-11-13
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run: 26 passed, 0 failed, 0 errors, 26 cases. It is not a model score. Each case is counted once. A live Microsoft Foundry run has not been done.

The exit code is 0 when an outline or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The matcher is exact. A fair paraphrase of an approved sentence becomes a gap. That is deliberate. A gap is not a failed run.
- A sentence that contains a negation is dropped in full. "Use the catalogue, not the old line" does not cite the catalogue. Split the ask into its own sentence. A negation the list does not catch can still cite an approved line. The presenter still has to approve the outline, and nothing is shared.
- Experiment 29 treats a quote as unsupported when a content word is not in the source. The outline therefore quotes the passage itself.
- The 180-day window and Experiment 29's review-stamp window are starter defaults. They are not a duty in the accessibility regulations.
- The plain-English check counts words against the "around 25 words" line on the publishing-documents page. It is not a reading-age certificate and it is not a finding that the sentence was plain English.
- Colour contrast is not assessed, because this starter does not render colours. `wcag_22_aa_met` stays false.
- The local `.pptx` is a simple document. It is not a styled template and it is not a published file.
- A dedicated Copilot in PowerPoint how-to, the PowerPoint JavaScript API, the Graph upload page, and Microsoft 365 Copilot licensing prices were not opened.
- The harness overview retrieved on 13 November 2026 names a Microsoft Copilot harness. It does not, in that text, call it the GitHub Copilot harness or say that it is not the GitHub Copilot service. Experiment 52 recorded both from the same URL a day earlier. This folder still ships the skills layout the catalogue calls the GitHub Copilot harness. Treat the earlier sentence as not re-verified on this read.
- The Work IQ general-availability date is not on the page that was opened. It is not stated here.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. The overview says that. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Northmere Digital Services and Aldergate Borough Council are fictional.
- This is not legal advice, an accessibility certificate, a classification decision, or an ATRS submission.

## UK public-sector presentations

Regulation 6 is why a public-sector website has an accessibility duty. Regulation 4(3)(d) is why a Microsoft Office document published on that site can be in scope. This starter does not decide scope, and it does not set `accessibility_certified`.

The GOV.UK guidance page is why the checklist names WCAG 2.2 AA. The regulation text that was opened does not use those words. The checklist says the presenter must check contrast, alt text, reading order, and plain English. It does not say they were met.

Paragraph 5 and paragraph 25 of the classification policy are why OFFICIAL and OFFICIAL-SENSITIVE are copied rather than dropped. A deck in this starter is not marked FOR PUBLIC RELEASE unless those words are already in the source.

## Two Copilot Studio harnesses

Both call `src/narrative.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness publishes. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** One topic. The presenter pastes a pack, the flow returns JSON, the topic stops. Microsoft's harness overview, opened 13 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**GitHub Copilot harness, as this repository names it.** On the page opened 13 November 2026 the reasoning-heavy harness is titled Microsoft Copilot harness. It is a Copilot Studio authoring and orchestration framework for a follow-up on the same JSON: which passage was refused, which figure was withheld, and why an approval did not share the deck. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). The overview says this harness can create a PowerPoint file. This starter's slide file is still the local core, and only after approval. The skill does not tell the harness to share it.

## Microsoft Foundry

Optional. A short narrative may be written from the JSON. The quotes, the gaps, the checklist, and the approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same manifest.
- The groundedness check: [../29-groundedness-evaluation/](../29-groundedness-evaluation/).
- The figure comparison: [../36-cross-source-validation/](../36-cross-source-validation/).
- The bid-draft pattern this outline follows: [../52-word-proposal-drafting/](../52-word-proposal-drafting/).

## Project structure

```
experiments/53-powerpoint-narrative-builder/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 13 November 2026

- [Accessibility Regulations 2018, regulation 3](https://www.legislation.gov.uk/uksi/2018/952/regulation/3)
- [Regulation 4](https://www.legislation.gov.uk/uksi/2018/952/regulation/4)
- [Regulation 6](https://www.legislation.gov.uk/uksi/2018/952/regulation/6)
- [Understanding accessibility requirements for public sector bodies](https://www.gov.uk/guidance/accessibility-requirements-for-public-sector-websites-and-apps)
- [Publishing accessible documents](https://www.gov.uk/guidance/publishing-accessible-documents)
- [GOV.UK style guide](https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style)
- [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Microsoft 365 Copilot overview](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview)
- [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
