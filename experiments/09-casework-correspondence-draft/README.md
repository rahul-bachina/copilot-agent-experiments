# Experiment 09: Correspondence Draft Agent

UK ministerial, MP, and resident casework edition. Catalogue ID **O008**.

A starter for a correspondence unit. It helps an author turn one inbound letter into a draft reply: a proposed channel, a casework clock, vulnerability flags for a person to review, and text that cites the supplied lines to take or says there is a gap.

**Autonomy A1.** The author approves the recipient and the final text. The agent does not send, does not choose the final recipient, and does not invent a policy position.

This revision contains the permissions manifest, a deterministic clock, a synthetic lines library, 22 synthetic fixtures, a mock drafter used only as a smoke test, and the build notes for both Copilot Studio harnesses and Microsoft Foundry. Nothing here calls a model.

Stack: Microsoft 365 and Copilot Studio. The clock and the drafter are Python in the standard library, so an author can run them without a tenant. A SharePoint lines library is described and not connected.

The fictional body in the fixtures is the Department for Civic Spaces. The people, the constituency of Greentown South, and the lines are invented.

## The problem

Departments answer letters from MPs, peers, and members of the public against lines to take, and they track a reply deadline. A draft that states a position the lines do not contain, or that picks an address and sends, is the failure mode this starter is built to refuse.

The Cabinet Office [Guide to Handling Correspondence](https://assets.publishing.service.gov.uk/media/66d99762608fb761b681111d/Guide_to_Handling_Correspondence_-_September_2024__1_.pdf) (September 2024, PDF retrieved 26 October 2026) says departments and agencies should set a deadline, with ministerial agreement, and that the deadline should not exceed 20 working days. The clock starts the day after receipt (paragraph 9). A holding reply does not clear the case (paragraph 20). FOI performance is recorded separately (paragraph 40). The [Government Correspondence Hub](https://www.gov.uk/guidance/government-correspondence-hub), retrieved the same day, says departments will aim to respond within 20 working days, and that correspondence is separate from FOI, subject access, and complaints. The hub page was last updated on 25 September 2026.

Those sources are for government departments and agencies. A council's own published target is not given the 20-working-day ceiling here.

Two published ATRS records were opened on 26 October 2026. They describe those departments' tools. They are not a description of this starter.

- [DfE: Correspondence Drafter](https://www.gov.uk/algorithmic-transparency-records/dfe-correspondence-drafter). The record says staff review and edit the draft, then copy it into an email and check the address. The phase on the record is Beta/Pilot.
- [FCDO: Correspondence Triage](https://www.gov.uk/algorithmic-transparency-records/fcdo-correspondence-triage). The record says that tool does not write responses. Staff prepare, sign off, and release them.

A DWP correspondence-drafting record was not opened, so none is cited. The catalogue's mention of DWP is unverified for this experiment.

## Non-goals

- Sending a letter, an email, a holding reply, or a transfer.
- Choosing the final recipient. A role is proposed. An address counts only when the author supplies it, and even then nothing is sent.
- Inventing a policy position, a funding figure, or a line to take.
- Citing a withdrawn line, a line that is not yet in force, or a line whose review date has been reached.
- Deciding that no reply will be sent (Guide paragraph 14 is a human decision).
- Sending a transfer, or calculating the other department's transfer clock. Those times run from a transfer this agent does not send (paragraph 21).
- Deciding an FOI or EIR exemption, a cost limit, or disclosure. Experiment 01 triages those requests. This clock is not the statutory information-rights clock.
- Deciding a complaint outcome.
- Labelling a person as vulnerable, or writing a marker onto a case.
- Writing a production case record, or publishing an ATRS record.
- Deciding that a deployment is inside the ATRS mandatory scope.
- Producing a Welsh reply. The Guide's paragraph 37 is a prompt for the organisation's own scheme.
- Using a Scottish or Northern Ireland bank-holiday calendar.
- Giving legal advice.

## What the clock does

`src/sla.py` calculates the date. It does not call a model and it does not read the network. The same inputs always produce the same JSON.

| Rule | Source, retrieved 26 October 2026 | What the code does |
|---|---|---|
| Reply target | Guide paragraph 9 | The author passes the department's target. For a department or agency it must not exceed 20 working days. A longer target is not returned as a date. |
| When day 1 starts | Guide paragraph 9 | The first working day on or after the calendar day after receipt. |
| Holding reply | Guide paragraph 20 | Does not clear the deadline. The flag stays false. |
| Transfer and contribution | Guide paragraphs 21 and 24 | Not calculated. The agent does not send a transfer. |
| Information rights | Guide paragraph 40, and the Correspondence Hub | No correspondence due date is returned. |
| Council target | Not the Guide | Operative only as the number the author confirms. The 20-day ceiling is not applied as a council rule. |

The Guide does not define "working day". This starter uses the England and Wales bank-holiday calendar in `src/working_days.py`. The 2026 England and Wales dates were checked against [bank holidays](https://www.gov.uk/bank-holidays) on 26 October 2026.

A date is operative only when the author has confirmed both the channel and the target. Until then the JSON may show a reference date. A reference date is arithmetic, not a deadline the unit should rely on.

## What the drafter does

`src/draft.py` is a keyword stand-in tuned to the synthetic fixtures.

- It proposes a channel: MP, peer, treat official (a member of the public), campaign, or information rights. Guide paragraphs 7 and 8 are the reading used for the proposal. The author confirms it. A ministerial signature stays unconfirmed.
- It cites a line only by pasting that line and its id. If nothing current covers the ask, the draft says no position is stated.
- It flags prompt injection, a stale year in the narrative, complaint wording, press interest, and Welsh-language review.
- It quotes words that prompted a vulnerability flag. It does not label the person. Immediate-risk wording sets a stop for a person. Nothing is sent and nobody is contacted.
- It attaches a draft ATRS note marked not submitted. Scope is not decided.

An instruction in the letter to send, to approve a recipient, to invent a position, to revive a withdrawn line, to publish the ATRS note, or to close the case is recorded under `security` and is not followed.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/09-casework-correspondence-draft
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
```

`eval/evaluate.py` prints a **mock smoke test**. The 22 fixtures are synthetic and the drafter is a keyword stand-in tuned to them. `eval/smoke_report.json` is that same run. It is not a model score. A live Microsoft Foundry run has not been done.

One draft:

```bash
python src/draft.py --received 2026-01-02 --as-of 2026-10-26 \
  --input examples/sample_letter.txt --confirm-target --confirm-channel
```

The sample is a fictional MP's letter about park hours, received Friday 2 January 2026. With both confirmations, the operative due date is Friday 30 January 2026. The current line `LTT-PARKS-01` is cited. The withdrawn line is not pasted in. The recipient is not approved. Nothing is sent.

A council target of 10 working days, which is not the Cabinet Office ceiling:

```bash
python src/draft.py --received 2026-01-02 --as-of 2026-10-26 \
  --regime council --target-working-days 10 \
  --input examples/sample_letter.txt --confirm-target --confirm-channel
```

That date is operative only as the council target the author confirmed. The command above still uses the fictional department's lines. A council would supply its own library.

## Limitations

- The Guide does not define "working day". England and Wales bank holidays are a reading, checked for the 2026 dates on the GOV.UK list retrieved 26 October 2026. Scotland and Northern Ireland are not encoded. Scotland's 15 June 2026 bank holiday is not closed here, because it was not on the England and Wales list. The coronation bank holiday on 8 May 2023 is not included unless the caller passes it. One-off proclamations are not forecast.
- "Should not exceed 20 working days" (Guide paragraph 9) and "will aim to respond within 20 working days" (Correspondence Hub) are both reported. They are not the same sentence. The code enforces the ceiling for `central_government` and still requires the author to confirm the department's own target.
- Paragraph 9's "day after" is implemented as: day 1 is the first working day on or after the calendar day after receipt. A department that counts differently should not rely on the date until it has checked this reading.
- The September 2024 PDF is the edition retrieved. A later edition was not compared line by line with the hub.
- The drafter is a keyword stand-in. It will miss a paraphrase and it can miss a topic that is not in the fixture list. That is why a gap says no position is stated, and why a person approves the text.
- Lines live in `fixtures/lines_to_take.json`. They are synthetic. A real unit's lines are not in this repository.
- Information-rights deadlines are not calculated. Point the letter at Experiment 01 for FOI triage. Do not treat a blank correspondence date as the FOI deadline.
- This is not legal advice, a DPIA, or an ATRS submission.

## Two Copilot Studio harnesses

Both call `src/sla.py` and `src/draft.py`, and both stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness sends, writes a case, or invents a line. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics and one clock action. See [copilot-studio/README.md](copilot-studio/README.md) and [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md). This is a build guide, not an importable solution.

**GitHub Copilot harness.** A Copilot Studio authoring and orchestration framework for the author's follow-up questions on the same draft. It is not the GitHub Copilot service. Skills, tool contracts, and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/). Microsoft bills that harness in Copilot Credits. Prices were not copied. Pages were retrieved on 26 October 2026.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Microsoft Foundry path: [docs/foundry.md](docs/foundry.md).
- Microsoft 365 lines library, not connected: [docs/microsoft-365.md](docs/microsoft-365.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/09-casework-correspondence-draft/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── working_days.py
│   ├── sla.py
│   ├── lines.py
│   └── draft.py
├── fixtures/
│   └── lines_to_take.json
├── copilot-studio/
│   ├── README.md
│   └── system-prompt.md
├── skills/
│   ├── draft-casework-reply/SKILL.md
│   └── calculate-casework-sla/SKILL.md
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened for this revision

- [Guide to Handling Correspondence, September 2024 (PDF)](https://assets.publishing.service.gov.uk/media/66d99762608fb761b681111d/Guide_to_Handling_Correspondence_-_September_2024__1_.pdf), retrieved 26 October 2026
- [Government Correspondence Hub](https://www.gov.uk/guidance/government-correspondence-hub), retrieved 26 October 2026
- [DfE: Correspondence Drafter](https://www.gov.uk/algorithmic-transparency-records/dfe-correspondence-drafter), retrieved 26 October 2026
- [FCDO: Correspondence Triage](https://www.gov.uk/algorithmic-transparency-records/fcdo-correspondence-triage), retrieved 26 October 2026
- [ATRS scope and exemptions policy](https://www.gov.uk/government/publications/algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy) (the landing page; the scope decision is not made here)
- [Bank holidays](https://www.gov.uk/bank-holidays), retrieved 26 October 2026
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), retrieved 26 October 2026
- [Agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/overview), retrieved 26 October 2026
- [Manage costs for agents powered by the GitHub Copilot harness](https://learn.microsoft.com/en-us/power-platform/admin/manage-usage-github-copilot-harness), retrieved 26 October 2026
- [What is Microsoft Entra Agent ID?](https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id), retrieved 26 October 2026

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
