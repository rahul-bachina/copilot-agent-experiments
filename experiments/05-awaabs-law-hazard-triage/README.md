# Experiment 05: Awaab's Law hazard triage and statutory clock

Catalogue ID **UK01**.

A starter for councils and other social landlords in England. It helps a housing officer turn one tenant report into a draft triage: a proposed hazard family and category, the statutory clock, vulnerability characteristics for the officer to review, a draft written summary, Housing Ombudsman escalation information, and a reasonable-endeavours record built only from steps the officer entered.

**Autonomy A1.** The officer approves the hazard category, the clock, and every tenant-facing summary. Nothing in this folder sends a message or writes a housing management system. The agent does not decide that a defence is made out, and it does not refer a complaint to the Housing Ombudsman.

This revision contains the permissions manifest, the deterministic clock, synthetic fixtures, a mock triage used only as a smoke test, and build notes for two Copilot Studio harnesses and for Microsoft Foundry. Nothing here calls a model.

Stack: Copilot Studio, Power Platform, and Microsoft Foundry. The clock itself is Python in the standard library, so an officer can run the dates without a tenant.

## The problem

Section 10A of the Landlord and Tenant Act 1985 implies a covenant, in a relevant social housing lease in England, that the lessor will comply with prescribed requirements. The requirements are in the [Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025](https://www.legislation.gov.uk/uksi/2025/1042) (SI 2025/1042). They came into force on 27 October 2025. They are often called Awaab's Law.

Missing a date, or letting a model invent one, leaves the landlord exposed to a breach of that covenant. The Housing Ombudsman is a separate route: a resident complains to the landlord first, and can then ask the Ombudsman to consider the complaint. Repairs and damp remain a large part of that caseload. This agent prepares the officer's reading. The officer decides.

## Non-goals

- Deciding the hazard category. The agent proposes one. The officer approves it.
- Deciding that a tenancy is a social home, or that the landlord is responsible for the deficiency.
- Sending the written summary, a safety note, an email, an SMS, or any other tenant-facing message.
- Writing a housing management system, a repairs system, or a Dataverse row.
- Deciding that the reasonable-endeavours defence in section 10A(5) is made out, or that consent endeavours are exhausted.
- Referring a complaint to the Housing Ombudsman, or deciding that the Ombudsman can consider it.
- Booking suitable alternative accommodation, or spending money.
- Labelling a tenant as vulnerable, or writing a marker onto a tenancy.
- Downgrading a proposal because the report text says to.
- Applying Phase 2 or Phase 3 as if they were in force.
- Applying the regulations to Wales, Scotland, Northern Ireland, or a private landlord.
- Giving legal advice, or deciding a claim.

## What is in force, and what is not

Read on 24 October 2026.

| Phase | What it covers | Status on 24 October 2026 |
| --- | --- | --- |
| Phase 1 | Emergency hazards other than overcrowding, and significant hazards associated with damp, mould or fungal growth | **In force** from 27 October 2025, SI 2025/1042 |
| Phase 2 | Significant hazards for a wider list (excess cold and heat, domestic hygiene, falls, electrical hazards, fire and explosions, structural collapse), plus a changed definition of significant risk | **Not in force.** The [draft amendment](https://www.legislation.gov.uk/ukdsi/2026/9780348285611) says it comes into force on 30 November 2026, and the legislation.gov.uk page still said it had not been made as a statutory instrument |
| Phase 3 | The remaining Housing Health and Safety Rating System hazards, except overcrowding | **Not in force.** MHCLG guidance describes it and does not give a commencement date. A GOV.UK news story says it will be introduced in 2027. No instrument was found |

The clock will not start an operative Phase 2 or Phase 3 significant-hazard timeframe. An emergency hazard is already in force for prescribed hazards other than a lack of adequate space for living and sleeping, including where the underlying matter is one that Phase 2 would later add as a *significant* hazard. The officer still has to approve that category.

The in-force definition of a significant risk is a risk that a reasonable lessor with the relevant knowledge would take steps to make safe as a matter of urgency, but not within 24 hours (regulation 3(1)(b)). The draft amendment would replace that with "make safe within 15 working days". That new test is not encoded. The ten-working-day investigation and the five-working-day safety work are action periods in the 2025 regulations. They are not the same thing as that draft definition.

## What the clock does

`src/statutory_clock.py` calculates the dates. It does not call a model and it does not read the network. The same inputs always produce the same JSON. A date is operative only when the officer has confirmed that the home is a social home in England, has approved the category, and has approved the clock, and the phase is in force.

| Clock | Rule | How it is counted |
| --- | --- | --- |
| Emergency investigation and relevant safety work | Regulation 5 | 24 hours from the awareness time the officer enters (Condition 1), or from the investigation completion time if the officer records Condition 2. Weekends are not skipped. |
| Standard investigation | Regulation 6 | 10 working days beginning on the day after the day of awareness. |
| Extended or renewed investigation | Regulations 6 and 7 | 10 working days beginning on the day after the day the tenant requests a physical inspection, when the officer records that request. |
| Written summary | Regulation 9 | 3 working days beginning on the day after the day the investigation is completed. The module does not decide that the regulation 9(1) exception applies. |
| Relevant safety work for a significant hazard | Regulation 11 | 5 working days beginning on the day after the day the investigation is completed. |
| Begin supplementary preventative work, or take steps to begin it | Regulation 13(2) | 5 working days beginning with the relevant day. The relevant day is the day after the investigation, or the day after a further investigation if the officer records one. |
| Long-stop to begin that work | Regulation 13(3) | 12 weeks beginning with the day after the investigation that determined the hazard, and only where the officer records that beginning within 5 working days is not reasonably practicable. |
| Finish supplementary preventative work | Regulation 13(4) | "Within a reasonable period." The clock does not invent a day. |

A working day is any day other than a Saturday, a Sunday, Christmas Day, Good Friday, or a bank holiday under the Banking and Financial Dealings Act 1971 in England and Wales (regulation 2). The day after the trigger is day 1 when that day is a working day. If it is not, day 1 is the next working day. That follows the regulations and the MHCLG guidance retrieved on 24 October 2026, which says day 1 is the day after the landlord becomes aware, except for the 24-hour emergency period.

Where the officer records that Part 6 (temporary rehousing) has been complied with, the fixed hard stop for completing relevant safety work is disapplied and the duty is to act as soon as reasonably practicable (regulation 5(5) and regulation 11(2)(b)). The module does not decide that Part 6 was complied with, and it does not book accommodation.

## Reasonable endeavours

Section 10A(5) makes it a defence, in proceedings for breach of the implied covenant, for the lessor to prove that they used all reasonable endeavours to avoid the breach. The regulations also stop particular duties once the lessor has exhausted all reasonable endeavours to obtain a consent without which the work cannot lawfully be done. MHCLG guidance treats access, approvals, and specialist contractors as questions for that defence, and says a court decides.

The record lists steps the officer typed. It does not invent a visit. `defence_made_out` is false. The agent cannot file the record.

## Housing Ombudsman

The draft includes published escalation information and nothing else. A landlord's complaint procedure has two stages under the Complaint Handling Code. Stage 1 is acknowledged within 5 working days of receipt and answered within 10 working days of acknowledgement. Stage 2 is acknowledged within 5 working days of the escalation request and answered within 20 working days of acknowledgement. Extensions are limited, and an extension must give the Ombudsman's contact details. The Ombudsman's resident pages, read on 24 October 2026, say the service can accept a complaint for investigation where the landlord's stage 2 response is dated within 12 months. The agent does not refer, and it does not decide that the Ombudsman can consider the complaint. The Code text that was read did not define "working day", so this module does not present a Code date as a statutory deadline.

## Vulnerability

The guidance says landlords should understand the household, including age and health, because the same defect can be a different risk for a different occupier. The agent may flag a characteristic and quote the words. It does not label the tenant vulnerable, and it does not write a marker. An officer reviews the flag before it is recorded anywhere.

## How to run

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/05-awaabs-law-hazard-triage
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
```

`eval/evaluate.py` prints a **mock smoke test**. The fixtures are synthetic and the classifier is a keyword stand-in tuned to them. `eval/smoke_report.json` is that same run. It is not a model score. A live Microsoft Foundry run has not been done.

Calculate one clock. Nothing is operative until the officer's flags are set:

```bash
python src/statutory_clock.py \
  --aware-at 2026-01-08T09:00:00+00:00 \
  --category significant \
  --hazard-family damp_mould_fungal_growth \
  --social-home-in-england \
  --approve-category \
  --approve-clock
```

Without `--approve-category` and `--approve-clock`, the same arithmetic is returned as a reference and `operative` is false.

Triage one synthetic report:

```bash
python src/triage.py \
  --aware-at 2026-10-24T09:30:00+00:00 \
  --input examples/sample_report.txt
```

## Sample

Awareness Thursday 8 January 2026 at 09:00, Europe/London. Officer confirms a social home in England, a significant damp and mould hazard, and the clock.

- The standard investigation period ends on Thursday 22 January 2026.
- The written summary, the five-working-day safety work, and the preventative-work dates are not calculated until the officer records that the investigation was completed.

Awareness Friday 2 January 2026 at 16:00. Officer confirms an emergency.

- The Condition 1 period of 24 hours ends at 16:00 on Saturday 3 January 2026. The weekend does not pause it.

## Limitations

- The standing bank-holiday pattern matches the GOV.UK England and Wales list's usual shape. It does not include one-off proclamations. A moved bank holiday has to be passed in with `--extra-closed` and `--cancel-bank-holiday`.
- "Ten working days beginning on the day after" is implemented as ten working days, with the day after as day 1 when it is a working day. A court decides a dispute about the count.
- "Twelve weeks beginning with" the day after the determination is implemented as 84 days beginning with that day, inclusive, so the last day is 83 days later. It is not moved for a weekend.
- The 24-hour period needs a time. A date with no time is refused rather than treated as midnight.
- The module records that, on 24 October 2026, the Phase 2 amendment was a draft and had not been made. A caller can assert that a made instrument is in force. The assertion does not make the draft law, the retrieval warning stays, and the date still cannot be operative before 30 November 2026.
- Phase 3 has no instrument and no verified commencement date. There is no flag that turns a Phase 3 significant-hazard clock on.
- The draft Phase 2 exclusions for some fire hazards in Fire Safety Order premises, and for residential evacuation plans, are not applied. They are not law yet. Under SI 2025/1042 an emergency hazard can still be a fire hazard.
- Amendments to section 10A by the Renters' Rights Act 2025 were, on the legislation.gov.uk page read that day, waiting for a commencement date. They are not encoded.
- Regulation 9(1) (no summary if the required work is finished inside the three-working-day period), regulation 14 (keeping the tenant updated, which has no fixed day count), and regulation 20 (entry at a reasonable time on 24 hours' notice) are described and not decided.
- `eval/smoke_report.json` is a mock smoke test of the keyword stand-in. It is not a model score. Dates in that run come from the clock.

This is not legal advice and it is not a statement of a landlord's compliance.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Copilot Studio standard harness, for tenant and officer intake: [copilot-studio/README.md](copilot-studio/README.md). Instructions to paste: [copilot-studio/system-prompt.md](copilot-studio/system-prompt.md).
- GitHub Copilot harness, for officer case review and the endeavours record: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Microsoft Foundry path: [docs/foundry.md](docs/foundry.md).
- Power Platform boundary: [docs/power-platform.md](docs/power-platform.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/05-awaabs-law-hazard-triage/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── src/
│   ├── statutory_clock.py
│   ├── triage.py
│   └── records.py
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
├── schema/
└── tests/
```

## References opened for this revision

Pages retrieved on 24 October 2026.

- [SI 2025/1042](https://www.legislation.gov.uk/uksi/2025/1042), made 23 September 2025, in force 27 October 2025
- [Draft amendment regulations 2026](https://www.legislation.gov.uk/ukdsi/2026/9780348285611), not yet made, stated commencement 30 November 2026
- [Landlord and Tenant Act 1985, section 10A](https://www.legislation.gov.uk/ukpga/1985/70/section/10A)
- [HHSRS Schedule 1](https://www.legislation.gov.uk/uksi/2005/3208/schedule/1), as amended by [SI 2026/571](https://www.legislation.gov.uk/uksi/2026/571) from 23 June 2026
- [Awaab's Law Phase 2 guidance for social landlords](https://www.gov.uk/government/publications/awaabs-law-phase-2-guidance-for-social-housing-landlords/awaabs-law-phase-2-guidance-for-social-landlords), MHCLG
- [Awaab's Law collection](https://www.gov.uk/government/collections/awaabs-law-in-the-social-rented-sector)
- [Awaab's Law: Regulations](https://www.gov.uk/government/publications/awaabs-law-regulations), the text as MHCLG says it would apply from 30 November 2026, subject to Parliamentary approval
- [GOV.UK news on the second phase](https://www.gov.uk/government/news/safer-homes-for-4m-tenants-with-quicker-action-on-dangerous-homes), including the statement that the third phase will be introduced in 2027
- [How to complain to your landlord](https://www.housing-ombudsman.org.uk/residents/how-to-complain-to-your-landlord/), Housing Ombudsman
- [When to get help from the Housing Ombudsman](https://www.housing-ombudsman.org.uk/residents/when-to-get-help-from-the-housing-ombudsman/)
- [Complaint Handling Code](https://www.housing-ombudsman.org.uk/app/uploads/2024/09/03.Complaint-Handling-Code-24.pdf)
- [Bank holidays](https://www.gov.uk/bank-holidays)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
