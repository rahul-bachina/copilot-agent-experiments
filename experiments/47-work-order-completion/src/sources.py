"""Pages opened on 11 November 2026. The core does not download them."""

from __future__ import annotations

from datetime import date

RETRIEVED_ON = date(2026, 11, 11)
STALE_AFTER_DAYS = 180

NOT_OPENED = (
    "Not opened on 11 November 2026: UK GDPR Article 9, Article 22A, "
    "the Renters' Rights Act 2025 commencement for the listed section 10A amendments, "
    "Phase 2 of the hazards regulations, regulation 5 and regulation 20 of SI 2025/1042, "
    "the Copilot Studio billing and licensing articles, and any FCA Handbook provision. "
    "Nothing in those pages is quoted. Whether a Phase 2 instrument has been made is unverified. "
    "No FCA Handbook provision is applied. This starter is not an FCA process."
)

SOURCES: dict[str, dict[str, str]] = {
    "hswa_s2": {
        "id": "hswa_s2",
        "title": "Health and Safety at Work etc. Act 1974, section 2",
        "url": "https://www.legislation.gov.uk/ukpga/1974/37/section/2",
        "retrieved": "2026-11-11",
        "banner": (
            "The page said section 2 is up to date with all changes known to be in force "
            "on or before 11 November 2026. It also said revised legislation on the site "
            "may not be fully up to date. A change yet to be applied is listed for section 51B."
        ),
        "taken": (
            "Section 2(1): it shall be the duty of every employer to ensure, so far as is "
            "reasonably practicable, the health, safety and welfare at work of all his employees. "
            "Section 2(2)(a) covers plant and systems of work. Section 2(2)(c) covers information, "
            "instruction, training and supervision. Section 2(2)(d) covers a place of work under "
            "the employer's control, including access and egress. The provision is marked U.K. "
            "This record does not decide that the duty was met."
        ),
    },
    "hswa_s3": {
        "id": "hswa_s3",
        "title": "Health and Safety at Work etc. Act 1974, section 3",
        "url": "https://www.legislation.gov.uk/ukpga/1974/37/section/3",
        "retrieved": "2026-11-11",
        "banner": (
            "The page said section 3 is up to date with all changes known to be in force "
            "on or before 11 November 2026."
        ),
        "taken": (
            "Section 3(1): it shall be the duty of every employer to conduct his undertaking in "
            "such a way as to ensure, so far as is reasonably practicable, that persons not in his "
            "employment who may be affected thereby are not thereby exposed to risks to their health "
            "or safety. The provision is marked U.K. This record does not decide that the duty was met."
        ),
    },
    "hswa_s7": {
        "id": "hswa_s7",
        "title": "Health and Safety at Work etc. Act 1974, section 7",
        "url": "https://www.legislation.gov.uk/ukpga/1974/37/section/7",
        "retrieved": "2026-11-11",
        "banner": (
            "The page said section 7 is up to date with all changes known to be in force "
            "on or before 11 November 2026."
        ),
        "taken": (
            "Section 7: it shall be the duty of every employee while at work to take reasonable "
            "care for the health and safety of himself and of other persons who may be affected "
            "by his acts or omissions at work, and, as regards any duty or requirement imposed on "
            "his employer or any other person by or under the relevant statutory provisions, to "
            "co-operate with him so far as is necessary to enable that duty or requirement to be "
            "performed or complied with. The provision is marked U.K. Approving a field is not "
            "that duty being performed by the agent."
        ),
    },
    "mhsvr_r3": {
        "id": "mhsvr_r3",
        "title": "Management of Health and Safety at Work Regulations 1999, regulation 3",
        "url": "https://www.legislation.gov.uk/uksi/1999/3242/regulation/3",
        "retrieved": "2026-11-11",
        "banner": (
            "The regulation heading is marked E+W+S. The page said there are currently no known "
            "outstanding effects for regulation 3."
        ),
        "taken": (
            "Regulation 3(1) requires every employer to make a suitable and sufficient assessment "
            "of the risks to employees and to persons not in his employment arising out of or in "
            "connection with the conduct by him of his undertaking. This completion record is not "
            "that assessment."
        ),
    },
    "lta_s10a": {
        "id": "lta_s10a",
        "title": "Landlord and Tenant Act 1985, section 10A",
        "url": "https://www.legislation.gov.uk/ukpga/1985/70/section/10A",
        "retrieved": "2026-11-11",
        "banner": (
            "The page lists changes yet to be applied, including substitution of section 10A(1) "
            "by the Renters' Rights Act 2025, section 60. Those amendments were not in the text "
            "that was read. Their commencement was not opened. The provision is marked E+W. "
            "The textual amendment note says sections 10A and 10B were inserted by the Social "
            "Housing (Regulation) Act 2023, section 42, with S.I. 2023/1001 regulation 2(t)."
        ),
        "taken": (
            "Section 10A(1) applies to a lease of a dwelling in England that is a relevant social "
            "housing lease, where section 9A applies or would apply but for section 9B(3). "
            "Section 10A(2) implies a covenant by the lessor to comply with all prescribed "
            "requirements applicable to that lease. Section 10A(3) requires regulations for action "
            "on prescribed hazards within the periods the regulations specify. Section 10A(5) is a "
            "defence if the lessor proves all reasonable endeavours to avoid the breach. "
            "This record does not decide that the covenant applies or that the defence is made out."
        ),
    },
    "hazards_reg_1": {
        "id": "hazards_reg_1",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 1",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/1",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects for regulation 1.",
        "taken": (
            "Regulation 1(1) cites the regulations by that name. Regulation 1(2): they come into "
            "force on 27 October 2025. Regulation 1(3): they extend to England and Wales. "
            "Regulation 1(4): they apply to lessors of social homes in England (whenever the lease "
            "was granted)."
        ),
    },
    "hazards_reg_3": {
        "id": "hazards_reg_3",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 3",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/3",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects for regulation 3.",
        "taken": (
            "Regulation 3(1) defines a significant hazard and an emergency hazard. A significant "
            "risk of harm is one a reasonable lessor with the relevant knowledge would take steps "
            "to make safe as a matter of urgency, but not within 24 hours. An imminent and "
            "significant risk is one they would take steps to make safe within 24 hours. For a "
            "significant hazard, regulation 3(2) limits a relevant hazard to a prescribed hazard "
            "where the risk is associated with exposure to damp, mould or fungal growth. This "
            "record does not apply that test."
        ),
    },
    "hazards_reg_8": {
        "id": "hazards_reg_8",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 8",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/8",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects for regulation 8.",
        "taken": (
            "Regulation 8(1) applies where an investigation concludes that a social home is affected "
            "by a significant hazard or an emergency hazard but that a further investigation is "
            "necessary to determine what work is required work, or any other matter relevant to "
            "required work. Regulation 8(2): the lessor must secure that the further investigation "
            "is completed by a competent investigator as soon as reasonably practicable. This "
            "record can flag further investigation for a person. It does not decide that regulation 8 applies."
        ),
    },
    "hazards_reg_9": {
        "id": "hazards_reg_9",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 9",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/9",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects for regulation 9.",
        "taken": (
            "Regulation 9(2) requires the lessor to give the lessee a document setting out the "
            "information in regulation 9(3), before the end of the relevant period, unless required "
            "work is identified and completed before that period ends. Regulation 9(4): the relevant "
            "period is 3 working days beginning the day after the day the relevant investigation is "
            "completed. This record does not give that document and does not start that period."
        ),
    },
    "hazards_reg_11": {
        "id": "hazards_reg_11",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 11",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/11",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects for regulation 11.",
        "taken": (
            "Regulation 11(2) requires the lessor to secure that relevant safety work for a "
            "significant hazard is completed within 5 working days beginning the day after the "
            "relevant investigation is completed, or, where Part 6 is complied with, as soon as "
            "reasonably practicable thereafter. This record does not decide that the work is "
            "relevant safety work and does not complete it."
        ),
    },
    "hazards_reg_12": {
        "id": "hazards_reg_12",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 12",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/12",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects for regulation 12.",
        "taken": (
            "Regulation 12 applies where relevant safety work has been completed. The lessor must "
            "secure that the social home is kept safe until a further investigation, or relevant "
            "supplementary preventative work, is completed, subject to regulation 12(4). "
            "Regulation 12(5) defines keep safe and relevant supplementary preventative work. "
            "This record does not decide that the home is safe."
        ),
    },
    "hazards_reg_13": {
        "id": "hazards_reg_13",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 13",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/13",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects for regulation 13.",
        "taken": (
            "Regulation 13(2) requires the lessor, before the end of 5 working days beginning with "
            "the relevant day, to begin relevant supplementary preventative work or to take steps "
            "to secure that it begins as soon as reasonably practicable and before the end of 12 "
            "weeks beginning the day after the investigation that determined the home is affected. "
            "Regulation 13(4): the work must be completed within a reasonable period. This record "
            "does not begin that work and does not decide that the period has started."
        ),
    },
    "uk_gdpr_art_5": {
        "id": "uk_gdpr_art_5",
        "title": "UK GDPR, Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "retrieved": "2026-11-11",
        "banner": (
            "Opened on 11 November 2026. Article 5(1)(b), Article 5(1)(e), and Article 5(3) show "
            "amendments from the Data (Use and Access) Act 2025. Article 5(1)(c) and Article 5(1)(d) "
            "were read in the text on the page."
        ),
        "taken": (
            "Article 5(1)(c): personal data shall be adequate, relevant and limited to what is "
            "necessary in relation to the purposes for which they are processed (data minimisation). "
            "Article 5(1)(d): personal data shall be accurate and, where necessary, kept up to date; "
            "every reasonable step must be taken to ensure that personal data that are inaccurate, "
            "having regard to the purposes for which they are processed, are erased or rectified "
            "without delay (accuracy). Article 5(2) is accountability. This record does not decide "
            "that a controller met Article 5. It lists clashes between the notes, the photo text, "
            "the parts, and the original job, and it leaves the clash on the record."
        ),
    },
    "uk_gdpr_art_6": {
        "id": "uk_gdpr_art_6",
        "title": "UK GDPR, Article 6",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/6",
        "retrieved": "2026-11-11",
        "banner": "The page said there are currently no known outstanding effects by UK legislation for Article 6.",
        "taken": (
            "Article 6(1) lists the bases on which processing shall be lawful. The closing words "
            "of Article 6(1) say points (ea) and (f) shall not apply to processing carried out by "
            "public authorities in the performance of their tasks. No basis is asserted."
        ),
    },
    "harness_overview": {
        "id": "harness_overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "retrieved": "2026-11-11",
        "banner": (
            "The page did not use the word preview for the three harnesses. That is not a "
            "general-availability claim for a click-path that was not exercised in a tenant. "
            "The billing and licensing articles linked from the page were not opened."
        ),
        "taken": (
            "The standard harness follows the topics and rules the maker defines. Skills and memory "
            "are described as not a focus for that harness. The GitHub Copilot harness is a "
            "Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot "
            "service. The page says customer data is not sent to or processed by the GitHub Copilot "
            "service when agents run in Copilot Studio. Agents on that harness use Copilot Credits. "
            "The page states no price."
        ),
    },
}


def source_view(as_of: date) -> tuple[list[dict], dict]:
    age = (as_of - RETRIEVED_ON).days
    current = age <= STALE_AFTER_DAYS
    rows = []
    for source in SOURCES.values():
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "retrieved": source["retrieved"],
                "banner": source["banner"] if current else None,
                "taken": source["taken"] if current else None,
                "current": current,
            }
        )
    stale = {
        "rules_current": current,
        "age_days": age,
        "stale_after_days": STALE_AFTER_DAYS,
        "retrieved_on": RETRIEVED_ON.isoformat(),
        "quotes_withheld": not current,
    }
    return rows, stale
