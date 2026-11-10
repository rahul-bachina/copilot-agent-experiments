"""Pages opened on 10 November 2026. The core does not download them."""

from __future__ import annotations

from datetime import date

RETRIEVED_ON = date(2026, 11, 10)
STALE_AFTER_DAYS = 180

NOT_OPENED = (
    "Not opened on 10 November 2026: UK GDPR Article 9, Article 22A, "
    "the Data (Use and Access) Act 2025 commencement instrument S.I. 2026/82, "
    "the Renters' Rights Act 2025 commencement for the listed section 10A amendments, "
    "Phase 2 of the hazards regulations, regulation 5 and regulation 20 of SI 2025/1042, "
    "and any FCA Handbook provision. Nothing in those pages is quoted. "
    "Whether a Phase 2 instrument has been made since Experiment 05's reading on "
    "24 October 2026 is unverified here."
)

SOURCES: dict[str, dict[str, str]] = {
    "hswa_s2": {
        "id": "hswa_s2",
        "title": "Health and Safety at Work etc. Act 1974, section 2",
        "url": "https://www.legislation.gov.uk/ukpga/1974/37/section/2",
        "retrieved": "2026-11-10",
        "banner": (
            "The page said section 2 is up to date with all changes known to be in force "
            "on or before 7 November 2026. It also said revised legislation on the site "
            "may not be fully up to date."
        ),
        "taken": (
            "Section 2(1): it shall be the duty of every employer to ensure, so far as is "
            "reasonably practicable, the health, safety and welfare at work of all his employees. "
            "Section 2(2)(a) includes plant and systems of work that are, so far as is reasonably "
            "practicable, safe and without risks to health. Section 2(2)(c) includes information, "
            "instruction, training and supervision. Section 2(2)(d) includes, so far as is reasonably "
            "practicable, a place of work under the employer's control and safe access and egress. "
            "The provision is marked U.K. on the page. This brief does not decide that the duty was met."
        ),
    },
    "hswa_s3": {
        "id": "hswa_s3",
        "title": "Health and Safety at Work etc. Act 1974, section 3",
        "url": "https://www.legislation.gov.uk/ukpga/1974/37/section/3",
        "retrieved": "2026-11-10",
        "banner": (
            "The page said section 3 is up to date with all changes known to be in force "
            "on or before 7 November 2026."
        ),
        "taken": (
            "Section 3(1): it shall be the duty of every employer to conduct his undertaking in "
            "such a way as to ensure, so far as is reasonably practicable, that persons not in his "
            "employment who may be affected thereby are not thereby exposed to risks to their health "
            "or safety. The provision is marked U.K. on the page. This brief does not decide that "
            "the duty was met."
        ),
    },
    "hswa_s7": {
        "id": "hswa_s7",
        "title": "Health and Safety at Work etc. Act 1974, section 7",
        "url": "https://www.legislation.gov.uk/ukpga/1974/37/section/7",
        "retrieved": "2026-11-10",
        "banner": (
            "The page said section 7 is up to date with all changes known to be in force "
            "on or before 9 November 2026."
        ),
        "taken": (
            "Section 7: it shall be the duty of every employee while at work to take reasonable "
            "care for the health and safety of himself and of other persons who may be affected "
            "by his acts or omissions at work, and to co-operate with his employer so far as is "
            "necessary to enable a duty under the relevant statutory provisions to be performed. "
            "The provision is marked U.K. on the page. Confirming this brief is not that co-operation "
            "being performed by the agent."
        ),
    },
    "mhsvr_r3": {
        "id": "mhsvr_r3",
        "title": "Management of Health and Safety at Work Regulations 1999, regulation 3",
        "url": "https://www.legislation.gov.uk/uksi/1999/3242/regulation/3",
        "retrieved": "2026-11-10",
        "banner": (
            "The regulation heading on the page is marked E+W+S. The page said there are "
            "currently no known outstanding effects for regulation 3."
        ),
        "taken": (
            "Regulation 3(1): every employer shall make a suitable and sufficient assessment of "
            "the risks to the health and safety of his employees to which they are exposed whilst "
            "they are at work, and the risks to persons not in his employment arising out of or in "
            "connection with the conduct by him of his undertaking. This brief is not that assessment."
        ),
    },
    "lta_s10a": {
        "id": "lta_s10a",
        "title": "Landlord and Tenant Act 1985, section 10A",
        "url": "https://www.legislation.gov.uk/ukpga/1985/70/section/10A",
        "retrieved": "2026-11-10",
        "banner": (
            "The page listed changes yet to be applied, including substitution of section 10A(1) "
            "by the Renters' Rights Act 2025, section 60. Those amendments were not in the text "
            "that was read. Their commencement was not opened. The provision is marked E+W."
        ),
        "taken": (
            "Section 10A(1) applies to a lease of a dwelling in England that is a relevant social "
            "housing lease, where section 9A applies or would apply but for section 9B(3). "
            "Section 10A(2) implies a covenant by the lessor to comply with all prescribed "
            "requirements applicable to that lease. Section 10A(3) requires regulations for action "
            "on prescribed hazards within the periods the regulations specify. Section 10A(5) is a "
            "defence if the lessor proves all reasonable endeavours to avoid the breach. "
            "This brief does not decide that the covenant applies or that the defence is made out."
        ),
    },
    "hazards_reg_1": {
        "id": "hazards_reg_1",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 1",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/1",
        "retrieved": "2026-11-10",
        "banner": "The page said there are currently no known outstanding effects for regulation 1.",
        "taken": (
            "Regulation 1(2): these Regulations come into force on 27 October 2025. "
            "Regulation 1(3): they extend to England and Wales. Regulation 1(4): they apply to "
            "lessors of social homes in England (whenever the lease was granted)."
        ),
    },
    "hazards_reg_3": {
        "id": "hazards_reg_3",
        "title": "Hazards in Social Housing (Prescribed Requirements) (England) Regulations 2025, regulation 3",
        "url": "https://www.legislation.gov.uk/uksi/2025/1042/regulation/3",
        "retrieved": "2026-11-10",
        "banner": (
            "The page said there are currently no known outstanding effects for regulation 3. "
            "Commencement information on the page says regulation 3 is in force at 27 October 2025."
        ),
        "taken": (
            "Regulation 3(1)(b): a significant risk of harm is a risk that a reasonable lessor "
            "with the relevant knowledge would take steps to make safe as a matter of urgency "
            "(but not within 24 hours). Regulation 3(1)(d): an imminent and significant risk is "
            "one that a reasonable lessor would take steps to make safe within 24 hours. "
            "For a significant hazard, regulation 3(2) limits a relevant hazard to a prescribed "
            "hazard where the risk is associated with exposure to damp, mould or fungal growth. "
            "For an emergency hazard, the risk is not associated with a lack of adequate space "
            "for living and sleeping. This brief does not apply that test. Experiment 05 may "
            "illustrate a clock. Officer approval is not passed, so the illustration is not operative."
        ),
    },
    "uk_gdpr_art_5": {
        "id": "uk_gdpr_art_5",
        "title": "UK GDPR, Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "retrieved": "2026-11-10",
        "banner": "Opened on 10 November 2026. Article 5(3) and the Article 5(1) amendments are on the page.",
        "taken": (
            "Article 5(1)(c) is data minimisation: adequate, relevant and limited to what is "
            "necessary. Article 5(1)(d) is accuracy. Article 5(2) is accountability. "
            "This brief does not decide that a controller met Article 5."
        ),
    },
    "uk_gdpr_art_6": {
        "id": "uk_gdpr_art_6",
        "title": "UK GDPR, Article 6",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/6",
        "retrieved": "2026-11-10",
        "banner": "The page said there are currently no known outstanding effects by UK legislation for Article 6.",
        "taken": (
            "Article 6(1) lists the bases on which processing shall be lawful. The closing words "
            "of Article 6(1) say points (ea) and (f) shall not apply to processing carried out by "
            "public authorities in the performance of their tasks. No basis is asserted. "
            "A utility or a facilities contractor confirms its own basis. Do not copy a basis from another experiment."
        ),
    },
    "harness_overview": {
        "id": "harness_overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "retrieved": "2026-11-10",
        "banner": (
            "The page did not use the word preview for the three harnesses. That is not a "
            "general-availability claim for a click-path that was not exercised in a tenant."
        ),
        "taken": (
            "The standard harness follows the topics and rules the maker defines. The GitHub "
            "Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, "
            "not the GitHub Copilot service. The page says customer data is not sent to the GitHub "
            "Copilot service when agents run in Copilot Studio. Agents on that harness use Copilot "
            "Credits. The page states no price. The billing articles were not opened."
        ),
    },
}
