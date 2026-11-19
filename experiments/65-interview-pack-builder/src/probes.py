"""Questions that probe a protected characteristic, including paraphrases.

A match needs an enquiry (or a stated requirement) and a concept, and the
concept must sit outside a negation. A right-to-work question that does not
ask nationality is not a nationality probe. An adjustment sentence that says
the person need not disclose health is not a health probe.

The patterns are an example list the organisation must review. They are not
a finding that a question is unlawful, and they are not a statistic.
"""

from __future__ import annotations

import re

from negate import denied_at, sentences

EXAMPLE_NOTE = (
    "Probe patterns are an example list. They are not a measure of how often "
    "a question is unlawful, and they are not legal advice. A sentence that "
    "uses none of the concept words is not matched."
)

_ENQUIRY = re.compile(
    r"\?|\b(?:how|what|when|why|where|who|which|are you|is the candidate|"
    r"do you|does the|did you|have you|will you|would you|could you|can you|"
    r"tell me|tell us|please (?:state|confirm|give|provide|disclose|complete)|"
    r"we need(?: to know| your)?|describe your|"
        r"ask (?:them|the candidate|the applicant|about)|"
    r"enquire|inquire)\b",
    re.I,
)
_PERSON = re.compile(
    r"\b(?:you|your|yours|candidate|applicant|interviewee|them|they|their)\b",
    re.I,
)
_REQUIREMENT = re.compile(r"\b(?:must|required|requirement|need you to|needs to be)\b", re.I)
_ADJUSTMENT = re.compile(
    r"\b(?:reasonable adjustment|adjustment|change to the interview|interview arrangements)\b",
    re.I,
)
_NO_DISCLOSE = re.compile(
    r"\b(?:do not need to|need not|don't need to|do not have to|don't have to|"
    r"without telling us|without disclosing|need not disclose|you do not need)\b",
    re.I,
)
_RTW = re.compile(
    r"\b(?:right to work|permission to work|allowed to work in the (?:uk|united kingdom)|"
    r"may work in the (?:uk|united kingdom))\b",
    re.I,
)

# Each pattern is matched inside one sentence. person_near is required unless
# the pattern itself names the person.
_PATTERNS: dict[str, tuple[str, ...]] = {
    "age": (
        r"\bhow old\b",
        r"\byour age\b",
        r"\b(?:the )?(?:candidate|applicant)'?s age\b",
        r"\bage bracket\b",
        r"\byears old\b",
        r"\bdate of birth\b",
        r"\bwhen (?:were|was) (?:you|the candidate|the applicant|they) born\b",
        r"\bwhen they were born\b",
        r"\b(?:you|they|the candidate) were born\b",
        r"\b(?:where|were) (?:you|they|the candidate) born\b",
        r"\byear of (?:your |their )?birth\b",
        r"\bretire(?:ment|d)?\b",
        r"\bpension age\b",
        r"\bstate pension\b",
        r"\btoo (?:young|old)\b",
        r"\b(?:under|over) (?:twenty-five|25|fifty|50)\b",
        r"\bleft school\b",
        r"\bleave school\b",
        r"\bschool leaver\b",
        r"\bleave the workforce\b",
        r"\bwhat generation\b",
        r"\byoung (?:applicant|candidate)\b",
    ),
    "marriage": (
        r"\bmarital status\b",
        r"\b(?:are|is) (?:you|the candidate|the applicant|they) married\b",
        r"\b(?:you|they|the candidate) (?:are|is) married\b",
        r"\byour (?:husband|wife|spouse|partner)\b",
        r"\bhave a (?:husband|wife|spouse)\b",
        r"\byour civil partner\b",
        r"\bhave a civil partner\b",
        r"\bin a civil partnership\b",
        r"\bentered a civil partnership\b",
        r"\bcivil partnership we should\b",
        r"\b(?:planning|plan|intend) to (?:get )?marr(?:y|ied)\b",
        r"\bget married\b",
        r"\brelationship status\b",
        r"\bsingle or married\b",
        r"\bto marry\b",
    ),
    "pregnancy_childcare": (
        r"\b(?:are|is) (?:you|the candidate|the applicant|they) pregnant\b",
        r"\b(?:you|they|the candidate) (?:are|is) pregnant\b",
        r"\bplanning (?:to have )?(?:a family|children|a baby)\b",
        r"\bhave a baby\b",
        r"\bchildcare plans\b",
        r"\bwhat childcare\b",
        r"\byour childcare\b",
        r"\b(?:do|does) (?:you|the candidate|the applicant|they) have (?:any )?(?:children|kids|childcare)\b",
        r"\bhow many children\b",
        r"\bwho (?:looks|will look) after (?:your|the) (?:children|child|kids)\b",
        r"\bmaternity (?:plans|leave)\b",
        r"\bexpecting a baby\b",
        r"\bfamily plans\b",
        r"\bwhen (?:are|is) (?:you|they) due\b",
    ),
    "religion": (
        r"\byour (?:religion|faith|beliefs)\b",
        r"\breligious beliefs\b",
        r"\bwhat religion\b",
        r"\b(?:the )?(?:candidate|applicant)'?s faith\b",
        r"\bwhich religion\b",
        r"\bwhat faith\b",
        r"\bdo you (?:pray|worship)\b",
        r"\b(?:attend|keep) (?:a |the )?(?:church|mosque|temple|synagogue|sabbath)\b",
        r"\btheir faith\b",
        r"\breligious belief\b",
        r"\bwhat do you believe\b",
        r"\bwhat they believe\b",
        r"\bplace of worship\b",
        r"\bmember of a (?:church|mosque|temple|synagogue)\b",
        r"\b(?:which|what) (?:church|mosque|temple|synagogue)\b",
        r"\bsabbath\b",
    ),
    "nationality": (
        r"\byour nationality\b",
        r"\b(?:the )?(?:candidate|applicant)'?s nationality\b",
        r"\btheir nationality\b",
        r"\bwhere (?:are|were) you from\b",
        r"\bwhere the candidate is from\b",
        r"\bcountry of (?:birth|origin)\b",
        r"\bwhere (?:were|was) (?:you|they|the candidate) born\b",
        r"\b(?:were|was) (?:you|they|the candidate) born\b",
        r"\b(?:you|they|the candidate) were born\b",
        r"\bwhat passport\b",
        r"\bwhich passport\b",
        r"\bare you british\b",
        r"\bbritish citizen\b",
        r"\bethnic origin\b",
        r"\bwhere were your parents born\b",
        r"\bparents born\b",
        r"\bcitizenship\b",
        r"\bwhich country\b",
    ),
    "disability_health": (
        r"\bhow many (?:sick|sickness) days\b",
        r"\bmedical history\b",
        r"\b(?:are|is) (?:you|the candidate|the applicant|they) disabled\b",
        r"\bdo you have a disability\b",
        r"\b(?:your|their) (?:health|disability|condition|diagnosis|illness)\b",
        r"\b(?:the )?(?:candidate|applicant)'?s medical\b",
        r"\bhealth questionnaire\b",
        r"\bsickness absence\b",
        r"\bmental health\b",
        r"\bmedication\b",
        r"\bfit (?:enough )?to work\b",
        r"\bany medical conditions\b",
        r"\bmedical condition\b",
        r"\bhealth condition\b",
        r"\byour medical\b",
        r"\bgood health required\b",
        r"\bin good health\b",
        r"\bdisclose your disability\b",
        r"\bno disability\b",
        r"\bmust be physically fit\b",
        r"\bable-bodied\b",
    ),
    "sex": (
        r"\bare you (?:a )?(?:man|woman|male|female)\b",
        r"\byour sex\b",
        r"\byour gender\b",
        r"\bman or a woman\b",
        r"\bidentify as a (?:man|woman)\b",
    ),
    "sexual_orientation": (
        r"\bsexual orientation\b",
        r"\bare you (?:gay|lesbian|bisexual|heterosexual|straight)\b",
        r"\b(?:gay|lesbian|bisexual|heterosexual)\b",
        r"\bsame-sex partner\b",
    ),
    "gender_reassignment": (
        r"\bgender reassignment\b",
        r"\bgender identity\b",
        r"\btransgender\b",
        r"\bare you trans\b",
        r"\btrans (?:man|woman)\b",
    ),
    "race": (
        r"\byour race\b",
        r"\bwhat is your race\b",
        r"\bskin colou?r\b",
        r"\bare you white\b",
        r"\bare you black\b",
        r"\bethnic group\b",
        r"\bethnic origin\b",
    ),
}

_COMPILED = {
    category: tuple(re.compile(pattern, re.I) for pattern in patterns)
    for category, patterns in _PATTERNS.items()
}

_OCCUPATIONAL = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"\boccupational requirement\b",
        r"\bgenuine occupational qualification\b",
        r"\bonly women should\b",
        r"\bonly men should\b",
        r"\bonly a woman should\b",
        r"\bonly a man should\b",
        r"\bapplicants must be women\b",
        r"\bapplicants must be men\b",
        r"\bcandidates must be (?:male|female|men|women)\b",
        r"\bthis post is reserved\b",
        r"\bthe post is reserved\b",
        r"\breserved for women\b",
        r"\breserved for people\b",
        r"\bpostholder must be a (?:woman|man)\b",
        r"\bwe require a (?:female|male)\b",
        r"\bwomen only\b",
        r"\bmen only\b",
        r"\bparticular faith\b",
        r"\bmust be a woman\b",
        r"\bmust be a man\b",
    )
)
_POSITIVE = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"\bpositive action\b",
        r"\btie-?break in favour\b",
        r"\bparticularly welcome applications from\b",
        r"\bprefer a candidate who shares\b",
    )
)


def _person_near(sentence: str, start: int, end: int) -> bool:
    window = sentence[max(0, start - 48): end + 48]
    return _PERSON.search(window) is not None


def _adjustment_without_disclosure(sentence: str) -> bool:
    return bool(_ADJUSTMENT.search(sentence) and _NO_DISCLOSE.search(sentence))


def _affirmed_pattern(sentence: str, pattern: re.Pattern[str], *, need_person: bool) -> bool:
    for match in pattern.finditer(sentence):
        if denied_at(sentence, match.group(0), match.start()):
            continue
        if need_person and not _person_near(sentence, match.start(), match.end()):
            if not re.search(r"\b(?:you|your|who|candidate|applicant)\b", match.group(0), re.I):
                continue
        return True
    return False


def _categories_in_sentence(sentence: str) -> list[str]:
    if not sentence or not _ENQUIRY.search(sentence) and not _REQUIREMENT.search(sentence):
        return []
    found: list[str] = []
    skip_health = _adjustment_without_disclosure(sentence)
    for category, patterns in _COMPILED.items():
        if category == "disability_health" and skip_health:
            continue
        implied = re.search(r"\b(?:please|tell us|tell me|ask them|ask the)\b", sentence, re.I)
        need_person = _REQUIREMENT.search(sentence) is None and implied is None
        for pattern in patterns:
            if _affirmed_pattern(sentence, pattern, need_person=need_person):
                if category == "nationality" and _RTW.search(sentence):
                    # Still a probe: nationality was affirmed as well as right to work.
                    pass
                if category not in found:
                    found.append(category)
                break
    if "nationality" in found and _rtw_only(sentence):
        found = [item for item in found if item != "nationality"]
    return found


def _rtw_only(sentence: str) -> bool:
    """True when the sentence is a right-to-work check and no nationality concept is affirmed."""

    if not _RTW.search(sentence):
        return False
    for pattern in _COMPILED["nationality"]:
        if _affirmed_pattern(sentence, pattern, need_person=True):
            return False
    return True


def probes_in(text: str) -> list[dict]:
    """One row per sentence and category. The row does not store the sentence."""

    rows: list[dict] = []
    for index, sentence in enumerate(sentences(text or "")):
        for category in _categories_in_sentence(sentence):
            rows.append(
                {
                    "category": category,
                    "sentence_index": index,
                    "excerpt_stored": False,
                    "decided": False,
                }
            )
    return rows


def categories_in(text: str) -> list[str]:
    found: list[str] = []
    for row in probes_in(text):
        if row["category"] not in found:
            found.append(row["category"])
    return found


def category_affirmed(text: str, category: str) -> bool:
    return category in categories_in(text)


def _route_patterns(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    for sentence in sentences(text or ""):
        for pattern in patterns:
            if _affirmed_pattern(sentence, pattern, need_person=False):
                return True
    return False


def occupational_requirement(text: str) -> bool:
    return _route_patterns(text, _OCCUPATIONAL)


def positive_action(text: str) -> bool:
    return _route_patterns(text, _POSITIVE)


def positive_action_recruitment(text: str) -> bool:
    """Section 159 is about more favourable treatment in recruitment or promotion."""

    narrowed = tuple(
        pattern
        for pattern in _POSITIVE
        if pattern.pattern in {r"\btie-?break in favour\b", r"\bprefer a candidate who shares\b"}
    )
    return _route_patterns(text, narrowed)


def positive_action_general(text: str) -> bool:
    narrowed = tuple(
        pattern
        for pattern in _POSITIVE
        if pattern.pattern
        in {r"\bpositive action\b", r"\bparticularly welcome applications from\b"}
    )
    return _route_patterns(text, narrowed)


def right_to_work_only(text: str) -> bool:
    """True when every right-to-work sentence stays inside that check."""

    saw = False
    for sentence in sentences(text or ""):
        if not _RTW.search(sentence):
            continue
        saw = True
        if not _rtw_only(sentence):
            return False
    return saw
