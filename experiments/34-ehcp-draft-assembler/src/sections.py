"""Statutory EHCP section letters. The assembler does not invent headings.

Regulation 12 of the Special Educational Needs and Disability Regulations
2014 (SI 2014/1530) is the statutory list. Paragraph 9.62 of the SEND Code
of Practice (January 2015) restates the letters and says the format is
agreed locally. Paragraph 9.69 is about shorter-term targets. It is not
the section list.
"""

from __future__ import annotations

SECTION_ORDER = ("A", "B", "C", "D", "E", "F", "G", "H1", "H2", "I", "J", "K")

# Headings follow regulation 12. code_note records where paragraph 9.62
# uses different words. The caseworker checks both against the local template.
SECTIONS: dict[str, dict[str, str]] = {
    "A": {
        "heading": "The views, interests and aspirations of the child and his parents or the young person.",
        "regulation": "SI 2014/1530 reg. 12(1)(a)",
        "code_note": "SEND Code of Practice, paragraph 9.62, section A.",
    },
    "B": {
        "heading": "The child or young person's special educational needs.",
        "regulation": "SI 2014/1530 reg. 12(1)(b)",
        "code_note": "SEND Code of Practice, paragraph 9.62, section B. Children and Families Act 2014 s.37(2)(a).",
    },
    "C": {
        "heading": "The child or young person's health care needs which relate to their special educational needs.",
        "regulation": "SI 2014/1530 reg. 12(1)(c)",
        "code_note": "Paragraph 9.62 says 'health needs which are related to their SEN'. The regulation says 'health care needs'.",
    },
    "D": {
        "heading": "The child or young person's social care needs which relate to their special educational needs or to a disability.",
        "regulation": "SI 2014/1530 reg. 12(1)(d)",
        "code_note": "SEND Code of Practice, paragraph 9.62, section D.",
    },
    "E": {
        "heading": "The outcomes sought for the child or young person.",
        "regulation": "SI 2014/1530 reg. 12(1)(e)",
        "code_note": "Paragraph 9.62 adds outcomes for adult life and shorter-term target arrangements. Paragraph 9.64 says outcomes are specified in section E. This assembler does not write an outcome.",
    },
    "F": {
        "heading": "The special educational provision required by the child or young person.",
        "regulation": "SI 2014/1530 reg. 12(1)(f)",
        "code_note": "Children and Families Act 2014 s.37(2)(c) and s.42. Section 42 applies where a plan is maintained. This draft is not a maintained plan.",
    },
    "G": {
        "heading": "Any health care provision reasonably required by the learning difficulties or disabilities which result in the child or young person having special educational needs.",
        "regulation": "SI 2014/1530 reg. 12(1)(g)",
        "code_note": "Regulation 12(2) says this provision must be agreed by the responsible commissioning body. This assembler does not record that agreement.",
    },
    "H1": {
        "heading": "Any social care provision which must be made for the child or young person as a result of section 2 of the Chronically Sick and Disabled Persons Act 1970.",
        "regulation": "SI 2014/1530 reg. 12(1)(h)(i)",
        "code_note": "Children and Families Act 2014 s.37(2)(e). Paragraph 9.62, section H1.",
    },
    "H2": {
        "heading": "Any other social care provision reasonably required by the learning difficulties or disabilities which result in the child or young person having special educational needs.",
        "regulation": "SI 2014/1530 reg. 12(1)(h)(ii)",
        "code_note": "Paragraph 9.62, section H2, also mentions adult social care under the Care Act 2014. This assembler does not decide eligibility.",
    },
    "I": {
        "heading": "The name of the school or other institution to be attended, and the type of that institution, or the type alone where no name is specified.",
        "regulation": "SI 2014/1530 reg. 12(1)(i)",
        "code_note": "Paragraph 9.62, section I. Children and Families Act 2014 s.38(5) says the draft plan must not name a school or other institution, or specify a type.",
    },
    "J": {
        "heading": "Where any special educational provision is to be secured by a direct payment, the special educational needs and outcomes to be met by the direct payment.",
        "regulation": "SI 2014/1530 reg. 12(1)(j)",
        "code_note": "Paragraph 9.62, section J, is wider and covers a Personal Budget. Children and Families Act 2014 s.49. This assembler does not set a budget or a direct payment.",
    },
    "K": {
        "heading": "The advice and information obtained under regulation 6(1), in appendices, with a list of that advice and information.",
        "regulation": "SI 2014/1530 reg. 12(4)",
        "code_note": "Paragraph 9.62, section K. This draft lists advice. It does not attach the reports.",
    },
}

# Regulation 6(1). (f) is discretionary. (g) applies in or beyond year 9.
# (h) is a request the bundle records. This starter does not decide that
# the request was reasonable.
ADVICE_TYPES: dict[str, dict[str, str | bool]] = {
    "parent_or_young_person": {"regulation": "6(1)(a)", "required": True},
    "educational": {"regulation": "6(1)(b)", "required": True},
    "medical": {"regulation": "6(1)(c)", "required": True},
    "psychological": {"regulation": "6(1)(d)", "required": True},
    "social_care": {"regulation": "6(1)(e)", "required": True},
    "other": {"regulation": "6(1)(f)", "required": False},
    "preparation_for_adulthood": {"regulation": "6(1)(g)", "required": False},
}

# Sections that are a gap when no tagged quote was placed.
# I is left blank on a draft under s.38(5). K is the advice list.
EMPTY_IS_GAP = ("A", "B", "C", "D", "E", "F", "G", "H1", "H2", "J")

PLACEMENT_SECTION = "I"
ADVICE_LIST_SECTION = "K"
