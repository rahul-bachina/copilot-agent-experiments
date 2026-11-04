"""Pinned extracts. Opened 4 November 2026. The draft does not download them.

Quotations are the words on the page that day. A later amendment is not
applied here. The Acas draft code in consultation is not applied.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 4)
LAST_VERIFIED = "2026-11-04"
DEFAULT_STALE_AFTER_DAYS = 90

CATALOGUE_ID = "H009"
EXPERIMENT_ID = "exp-32-employee-case-intake"
GATEWAY_EXPERIMENT_ID = "exp-08-uk-pii-redaction-gateway"
GATEWAY_CATALOGUE_ID = "O005"
GATEWAY_CALLER = "exp-32-employee-case-intake"
INTAKE_EXPERIMENT_ID = "exp-12-document-intake"
INTAKE_CATALOGUE_ID = "O001"
SCANNER_EXPERIMENT_ID = "exp-15-vulnerability-urgency-scanner"
SCANNER_CATALOGUE_ID = "UK06"

# Part IVA headings on the contents page opened 4 November 2026.
# No section 43I appeared on that page. 43FA did.
PART_IVA_HEADINGS = (
    ("43A", "Meaning of “protected disclosure”."),
    ("43B", "Disclosures qualifying for protection."),
    ("43C", "Disclosure to employer or other responsible person."),
    ("43D", "Disclosure to legal adviser."),
    ("43E", "Disclosure to Minister of the Crown."),
    ("43F", "Disclosure to prescribed person."),
    ("43FA", "Prescribed persons: duty to report on disclosures of information."),
    ("43G", "Disclosure in other cases."),
    ("43H", "Disclosure of exceptionally serious failure."),
    ("43J", "Contractual duties of confidentiality."),
    ("43K", "Extension of meaning of “worker” etc. for Part IVA."),
    ("43KA", "Application of this Part and related provisions to police."),
    ("43L", "Other interpretative provisions."),
)

ACAS_HTML = (
    "https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures/html"
)
ACAS_ABOUT = (
    "https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures"
)

QUOTES = {
    "acas_foreword_scope": {
        "id": "acas_foreword_scope",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Foreword, published 11 March 2015",
        "text": (
            "The Acas statutory Code of Practice on discipline and grievance "
            "procedures is set out in paragraphs 1 to 47 below."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
    },
    "acas_foreword_liability": {
        "id": "acas_foreword_liability",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Foreword",
        "text": (
            "A failure to follow the Code does not, in itself, make a person "
            "or organisation liable to proceedings. However, employment tribunals "
            "will take the Code into account when considering relevant cases."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "The same foreword says tribunals will be able to adjust awards by "
            "up to 25 per cent for unreasonable failure to comply with any "
            "provision of the Code. Trade Union and Labour Relations "
            "(Consolidation) Act 1992 section 207A was not opened. This starter "
            "does not decide that a failure was unreasonable and does not adjust an award."
        ),
    },
    "acas_foreword_separate": {
        "id": "acas_foreword_separate",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Foreword",
        "text": (
            "Organisations may wish to consider dealing with issues involving "
            "bullying, harassment or whistleblowing under a separate procedure."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "This is the foreword, not a numbered paragraph. It is not a finding that a separate procedure applies.",
    },
    "acas_para_1": {
        "id": "acas_para_1",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Paragraph 1",
        "text": (
            "This Code is designed to help employers, employees and their "
            "representatives deal with disciplinary and grievance situations in the workplace."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
    },
    "acas_para_4": {
        "id": "acas_para_4",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Paragraph 4, first bullet",
        "text": (
            "Employers and employees should raise and deal with issues promptly "
            "and should not unreasonably delay meetings, decisions or confirmation of those decisions."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "The Code does not state a number of days in this bullet.",
    },
    "acas_para_32": {
        "id": "acas_para_32",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Paragraph 32",
        "text": (
            "If it is not possible to resolve a grievance informally employees "
            "should raise the matter formally and without unreasonable delay with "
            "a manager who is not the subject of the grievance. This should be "
            "done in writing and should set out the nature of the grievance."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
    },
    "acas_para_33": {
        "id": "acas_para_33",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Paragraph 33",
        "text": (
            "Employers should arrange for a formal meeting to be held without "
            "unreasonable delay after a grievance is received."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "No number of days is stated. The non-statutory Acas guide's "
            "'ideally within five working days' was seen in search and in the "
            "guide PDF index. It is not paragraph 33. This starter does not apply it. "
            "Paragraph 38's five working days is a postponement where a companion "
            "is unavailable, not a deadline for holding the meeting."
        ),
    },
    "acas_para_40": {
        "id": "acas_para_40",
        "instrument": "Acas Code of Practice on disciplinary and grievance procedures",
        "pin": "Paragraph 40",
        "text": (
            "Following the meeting decide on what action, if any, to take. "
            "Decisions should be communicated to the employee, in writing, "
            "without unreasonable delay and, where appropriate, should set out "
            "what action the employer intends to take to resolve the grievance."
        ),
        "url": ACAS_HTML,
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "The decision in this paragraph is the employer's. This agent does not take it.",
    },
    "era_43a": {
        "id": "era_43a",
        "instrument": "Employment Rights Act 1996",
        "pin": "Section 43A",
        "extent": "E+W+S",
        "text": (
            "In this Act a “protected disclosure” means a qualifying disclosure "
            "(as defined by section 43B) which is made by a worker in accordance "
            "with any of sections 43C to 43H."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/1996/18/section/43A",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "This starter does not decide that a narrative is a qualifying "
            "disclosure or that it was made in accordance with sections 43C to 43H. "
            "Those sections do not state an employer investigation period. "
            "A tribunal time limit is not calculated."
        ),
    },
    "era_43b_1": {
        "id": "era_43b_1",
        "instrument": "Employment Rights Act 1996",
        "pin": "Section 43B(1), including (da)",
        "extent": "E+W+S",
        "text": (
            "In this Part a “qualifying disclosure” means any disclosure of "
            "information which, in the reasonable belief of the worker making "
            "the disclosure, is made in the public interest and tends to show "
            "one or more of the following— (a) that a criminal offence has been "
            "committed, is being committed or is likely to be committed, "
            "(b) that a person has failed, is failing or is likely to fail to "
            "comply with any legal obligation to which he is subject, "
            "(c) that a miscarriage of justice has occurred, is occurring or is "
            "likely to occur, (d) that the health or safety of any individual "
            "has been, is being or is likely to be endangered, (da) that sexual "
            "harassment has occurred, is occurring or is likely to occur, "
            "(e) that the environment has been, is being or is likely to be "
            "damaged, or (f) that information tending to show any matter falling "
            "within any one of the preceding paragraphs has been, is being or is "
            "likely to be deliberately concealed."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/1996/18/section/43B",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "Paragraph (da) is marked inserted on 6 April 2026 by the Employment "
            "Rights Act 2025 section 23(2) and SI 2026/323. Section 43B(5) on "
            "the same page still says the relevant failure means the matter "
            "falling within paragraphs (a) to (f). This starter does not decide "
            "whether (da) is inside that cross-reference, and it does not decide "
            "that the worker's belief was reasonable or that the disclosure was "
            "in the public interest."
        ),
    },
    "era_43c": {
        "id": "era_43c",
        "instrument": "Employment Rights Act 1996",
        "pin": "Section 43C(1)",
        "extent": "E+W+S",
        "text": (
            "A qualifying disclosure is made in accordance with this section if "
            "the worker makes the disclosure (a) to his employer, or (b) where "
            "the worker reasonably believes that the relevant failure relates "
            "solely or mainly to (i) the conduct of a person other than his "
            "employer, or (ii) any other matter for which a person other than "
            "his employer has legal responsibility, to that other person."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/1996/18/section/43C",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "The numbered limbs are joined in this quotation. The words omitted "
            "by the F2 marker on the legislation.gov.uk page are not restored."
        ),
    },
    "era_43j": {
        "id": "era_43j",
        "instrument": "Employment Rights Act 1996",
        "pin": "Section 43J(1)",
        "extent": "E+W+S",
        "text": (
            "Any provision in an agreement to which this section applies is void "
            "in so far as it purports to preclude the worker from making a protected disclosure."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/1996/18/section/43J",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "Section 43J(2) applies the section to any agreement between a worker "
            "and his employer, including an agreement to refrain from instituting "
            "or continuing proceedings. This starter does not decide that a "
            "disclosure is protected, so it does not decide that a clause is void. "
            "It still keeps the narrative out of the routing summary."
        ),
    },
    "era_43l_sexual_harassment": {
        "id": "era_43l_sexual_harassment",
        "instrument": "Employment Rights Act 1996",
        "pin": "Section 43L(1)",
        "extent": "E+W+S",
        "text": (
            "“sexual harassment” means harassment of the kind described in "
            "section 26(2) of the Equality Act 2010 (unwanted conduct of a sexual nature)."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/1996/18/part/IVA",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "Inserted on 6 April 2026 by the Employment Rights Act 2025 section 23(3) and SI 2026/323.",
    },
    "eqa_26_1": {
        "id": "eqa_26_1",
        "instrument": "Equality Act 2010",
        "pin": "Section 26(1)",
        "extent": "E+W+S",
        "text": (
            "A person (A) harasses another (B) if A engages in unwanted conduct "
            "related to a relevant protected characteristic, and the conduct has "
            "the purpose or effect of violating B's dignity, or creating an "
            "intimidating, hostile, degrading, humiliating or offensive environment for B."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/26",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "This starter does not decide purpose or effect. Section 26(4) requires B's perception, the other circumstances, and whether it is reasonable for the conduct to have that effect. Those are not decided here.",
    },
    "eqa_26_2": {
        "id": "eqa_26_2",
        "instrument": "Equality Act 2010",
        "pin": "Section 26(2)",
        "extent": "E+W+S",
        "text": (
            "A also harasses B if A engages in unwanted conduct of a sexual nature, "
            "and the conduct has the purpose or effect referred to in subsection (1)(b)."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/26",
        "applied_as_deadline": False,
        "days_encoded": None,
    },
    "eqa_26_5": {
        "id": "eqa_26_5",
        "instrument": "Equality Act 2010",
        "pin": "Section 26(5)",
        "extent": "E+W+S",
        "text": (
            "The relevant protected characteristics are age, disability, gender "
            "reassignment, race, religion or belief, sex, and sexual orientation."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/26",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "Marriage and civil partnership, and pregnancy and maternity, are not in the list on the page.",
    },
    "era_80g_1b": {
        "id": "era_80g_1b",
        "instrument": "Employment Rights Act 1996",
        "pin": "Section 80G(1B)(a)",
        "extent": "E+W+S",
        "text": (
            "For the purposes of subsection (1)(aa) the decision period applicable "
            "to an employee's application under section 80F is the period of two "
            "months beginning with the date on which the application is made, or "
            "such longer period as may be agreed by the employer and the employee."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/1996/18/section/80G",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "The words 'two months' were substituted on 6 April 2024. This starter "
            "does not calculate the last day. It does not decide that a request "
            "is an application under section 80F, that the employer has dealt with "
            "it in a reasonable manner, or that a refusal ground applies. "
            "Section 80G(1)(b) and (1ZA) are marked substituted on 6 January 2026 "
            "for specified purposes by the Employment Rights Act 2025 section 9 "
            "and SI 2026/3. That commencement instrument was not opened. The "
            "refusal grounds are not applied."
        ),
    },
    "absence_no_period": {
        "id": "absence_no_period",
        "instrument": None,
        "pin": "No period encoded",
        "text": (
            "No statutory response period for sickness absence is encoded in "
            "this starter. The Acas Code paragraphs opened here, and Employment "
            "Rights Act 1996 sections 43A to 43L and 80G, do not set one."
        ),
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "Statutory sick pay and fit-note rules were not opened. They are not invented here.",
    },
    "uk_gdpr_art_5": {
        "id": "uk_gdpr_art_5",
        "instrument": "UK GDPR",
        "pin": "Article 5(1)(a), (c) and (f), and Article 5(2)",
        "text": (
            "Personal data shall be processed lawfully, fairly and in a transparent "
            "manner; adequate, relevant and limited to what is necessary in relation "
            "to the purposes for which they are processed; and processed in a manner "
            "that ensures appropriate security. The controller shall be responsible "
            "for, and be able to demonstrate compliance with, paragraph 1."
        ),
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "The page shows Article 5(1)(b) and (e) and Article 5(3) as amended "
            "by the Data (Use and Access) Act 2025, in force on 5 February 2026 "
            "so far as not already in force. This starter does not choose an "
            "Article 6 basis. The routing summary does not contain the narrative."
        ),
    },
    "uk_gdpr_art_9": {
        "id": "uk_gdpr_art_9",
        "instrument": "UK GDPR",
        "pin": "Article 9(1) and 9(2)(b)",
        "text": (
            "Processing of personal data revealing racial or ethnic origin, "
            "political opinions, religious or philosophical beliefs, or trade "
            "union membership, and the processing of genetic data, biometric data "
            "for the purpose of uniquely identifying a natural person, data "
            "concerning health or data concerning a natural person's sex life or "
            "sexual orientation shall be prohibited. Paragraph 1 shall not apply "
            "if the processing is based on Article 6(1) and one of the listed "
            "conditions applies, including point (b): processing necessary for "
            "employment, social security and social protection law in so far as "
            "it is authorised by domestic law or a collective agreement providing "
            "for appropriate safeguards."
        ),
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/9",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "No Article 9 condition is asserted. The words 'the processing is based on Article 6(1) and' are the Data (Use and Access) Act 2025 insertion, in force from 20 August 2025.",
    },
    "uk_gdpr_art_22a": {
        "id": "uk_gdpr_art_22a",
        "instrument": "UK GDPR",
        "pin": "Article 22A(1), substituted for Article 22",
        "text": (
            "A decision is based solely on automated processing if there is no "
            "meaningful human involvement in the taking of the decision, and a "
            "decision is a significant decision, in relation to a data subject, "
            "if it produces a legal effect for the data subject, or it has a "
            "similarly significant effect for the data subject."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/2025/18/section/80",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "The UK GDPR Article 22 page shows the article as substituted. "
            "Data (Use and Access) Act 2025 section 80(1) inserts Articles 22A "
            "to 22D. Section 80 is in force at 5 February 2026 in so far as not "
            "already in force, by SI 2026/82 regulation 2(j). Article 22B "
            "restricts a significant decision based entirely or partly on "
            "Article 9(1) data where it is taken based solely on automated "
            "processing. This draft is not that decision. The HR officer confirms "
            "classification and routing. No outcome is decided."
        ),
    },
    "dpa_s10": {
        "id": "dpa_s10",
        "instrument": "Data Protection Act 2018",
        "pin": "Section 10(2)",
        "text": (
            "The processing meets the requirement in point (b), (h), (i) or (j) "
            "of Article 9(2) of the UK GDPR for authorisation by, or a basis in, "
            "the law of the United Kingdom or a part of the United Kingdom only "
            "if it meets a condition in Part 1 of Schedule 1."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/2018/12/section/10",
        "applied_as_deadline": False,
        "days_encoded": None,
    },
    "dpa_sch1_para1": {
        "id": "dpa_sch1_para1",
        "instrument": "Data Protection Act 2018",
        "pin": "Schedule 1, paragraph 1(1)",
        "text": (
            "This condition is met if the processing is necessary for the purposes "
            "of performing or exercising obligations or rights which are imposed "
            "or conferred by law on the controller or the data subject in "
            "connection with employment, social security or social protection, "
            "and when the processing is carried out, the controller has an "
            "appropriate policy document in place."
        ),
        "url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/1/paragraph/1",
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": (
            "Paragraph 1(2) points to the additional safeguards in Part 4 of "
            "Schedule 1, including the policy document in paragraph 39. That "
            "paragraph was not opened. This starter does not decide that "
            "paragraph 1 is met and does not check a policy document."
        ),
    },
    "ni_not_applied": {
        "id": "ni_not_applied",
        "instrument": None,
        "pin": "Northern Ireland",
        "text": (
            "Equality Act 2010 section 26 and Employment Rights Act 1996 "
            "Part IVA and section 80G are marked E+W+S on the pages opened. "
            "This starter does not state Northern Ireland employment law."
        ),
        "applied_as_deadline": False,
        "days_encoded": None,
        "note": "The Acas Code HTML page that was opened does not state a Northern Ireland extent. The Code is not applied to a case marked northern_ireland.",
    },
}


DATA_PROTECTION_IDS = (
    "uk_gdpr_art_5",
    "uk_gdpr_art_9",
    "uk_gdpr_art_22a",
    "dpa_s10",
    "dpa_sch1_para1",
)

GB_JURISDICTIONS = frozenset(
    {"england", "wales", "scotland", "england_and_wales", "great_britain"}
)
