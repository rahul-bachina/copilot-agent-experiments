"""Content risk and sensitive cues.

High-risk categories use the same-sentence negation rule. "It is not true
that the letter includes a deadline" does not count as a deadline.
Distress, safeguarding, whistleblowing, and grievance stems are routed
even when the sentence denies them. A policy title is not a personal cue.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from siblings import neighbours
else:
    from .siblings import neighbours

# Each list is a set of reworded stems. A sentence matches when one stem
# is affirmed. The eval reports recall on these authored paraphrases.
RISK_STEMS: dict[str, tuple[str, ...]] = {
    "legal_rights": (
        "you have a legal right to a written decision",
        "your legal rights are set out here",
        "the law gives you a right to challenge this",
        "you are entitled to appeal this decision",
        "you are entitled to a review of the decision",
        "a statutory right applies to this decision",
        "you have the right to a written decision",
        "a right of appeal is available",
        "you are entitled to written reasons",
        "you may challenge this decision in law",
        "this letter concerns your legal rights",
        "you can request a statutory review",
        "your right to reasons is part of this notice",
        "the statute gives you a right to be heard",
        "you are entitled to see the evidence",
        "a legal right to a hearing applies",
        "you have a right to a reasoned decision",
        "your appeal rights are explained below",
        "you may seek a review under the rules",
        "this notice affects your legal rights",
    ),
    "health": (
        "your medical treatment",
        "speak to your gp",
        "this affects your health",
        "mental health support",
        "your prescription",
        "a health condition",
        "your clinical care",
        "talk to a doctor about this",
        "this relates to your illness",
        "medicine you have been given",
        "a diagnosis is mentioned here",
        "your hospital appointment",
        "treatment for your condition",
        "a nurse will contact you about your health",
        "this page describes a health service",
        "your wellbeing and medical needs",
        "a referral to a clinic",
        "symptoms you should tell a clinician",
        "this is about your healthcare",
        "a health warning for patients",
    ),
    "safety": (
        "safety warning",
        "do not use this equipment",
        "risk of harm",
        "unsafe to enter",
        "a hazard is present",
        "emergency evacuation",
        "keep clear of the danger",
        "this is a safety notice",
        "danger of injury",
        "do not enter the unsafe area",
        "a fire safety instruction",
        "protective equipment is required",
        "the premises are unsafe",
        "an urgent safety alert",
        "risk to physical safety",
        "evacuate if you smell gas",
        "this product is unsafe",
        "a warning about injury",
        "stay away from the hazard",
        "safety of the public is affected",
    ),
    "benefits": (
        "housing benefit",
        "universal credit",
        "you may be paid a benefit",
        "benefit entitlement",
        "this payment is a benefit",
        "council tax reduction",
        "a benefit claim",
        "your benefit award",
        "apply for the benefit",
        "the benefit office",
        "pension credit",
        "this support is a benefit",
        "how the benefit is paid",
        "a change in your benefit",
        "benefit evidence you must send",
        "the amount of the benefit",
        "you are claiming a benefit",
        "local welfare benefit",
        "this letter is about your benefits",
        "a benefit decision",
    ),
    "deadlines": (
        "the deadline is",
        "the last day to apply",
        "no later than the date",
        "time limit for this application",
        "you must apply by the date",
        "the closing date",
        "within the time limit",
        "the deadline for a reply",
        "your deadline to respond",
        "the final day for this form",
        "a deadline applies to this notice",
        "send it before the deadline",
        "the time limit runs from this letter",
        "missing the deadline",
        "the cut-off date for applications",
        "you have until the deadline",
        "the application deadline",
        "a statutory time limit",
        "reply by the deadline given",
        "the deadline cannot be ignored",
    ),
    "complaints": (
        "make a complaint",
        "your complaint",
        "a formal complaint",
        "contact the ombudsman",
        "if you are dissatisfied",
        "how to complain",
        "the complaint procedure",
        "we will look at your complaint",
        "a complaint about this service",
        "you can complain to the ombudsman",
        "the complaints process",
        "raise a complaint",
        "your complaint will be recorded",
        "a stage two complaint",
        "complain if you disagree",
        "the complaint response",
        "this is a complaint letter",
        "refer the complaint",
        "unhappy with the complaint outcome",
        "the ombudsman can consider the complaint",
    ),
}

# Personal cues. Presence is enough, including a denial. A title is not.
SENSITIVE_STEMS: dict[str, tuple[str, ...]] = {
    "distress": (
        "i cannot go on like this",
        "i want to end my life",
        "i am thinking of suicide",
        "there is no point in carrying on",
        "i might hurt myself",
        "i do not want to be here any more",
        "i feel like ending it",
        "i have been thinking about killing myself",
        "i cannot cope any longer",
        "i am in despair and cannot continue",
        "i want to die",
        "ending my life feels like the only way",
        "i have made a plan to harm myself",
        "i am not safe from my own thoughts",
        "i keep thinking about suicide",
        "i cannot face another day",
        "i feel hopeless and want it to stop",
        "i am going to hurt myself",
        "there is nothing left for me and i want to die",
        "i have been self-harming",
    ),
    "safeguarding": (
        "my child is not safe",
        "i am worried about the child's safety",
        "someone is hurting my child",
        "this is a safeguarding concern for a child",
        "afraid for my child",
        "my child is being harmed",
        "a child in my care is at risk",
        "please protect my child",
        "someone at home is hurting the child",
        "the child told me about abuse",
        "i think a child is being abused",
        "my son is not safe at home",
        "my daughter is not safe at home",
        "a child is in immediate danger",
        "this needs a safeguarding referral",
        "i fear for the child's welfare",
        "the child is being neglected",
        "someone is a risk to my child",
        "please treat this as a child protection matter",
        "i need help because my child is unsafe",
    ),
    "whistleblowing": (
        "i need to blow the whistle",
        "this is a protected disclosure",
        "i am reporting serious wrongdoing",
        "please treat this as whistleblowing",
        "i am making a whistleblowing report",
        "this disclosure is about wrongdoing at work",
        "i want whistleblower protection",
        "i am disclosing malpractice",
        "please record this as a protected disclosure",
        "i am blowing the whistle on this practice",
        "this is a public interest disclosure",
        "i need to report wrongdoing in confidence",
        "treat me as a whistleblower",
        "i am raising whistleblowing concerns",
        "the wrongdoing i am disclosing",
        "a protected whistleblowing concern",
        "i want this disclosure kept as whistleblowing",
        "i am reporting a cover-up at work",
        "please log this whistleblowing disclosure",
        "this message is a protected disclosure of wrongdoing",
    ),
    "grievance": (
        "i want to raise a grievance",
        "this is a formal grievance",
        "i am raising a workplace grievance",
        "please open a grievance",
        "my grievance about my manager",
        "i am submitting a grievance",
        "treat this as my grievance",
        "a grievance against the way i was treated",
        "i need the grievance procedure",
        "this letter is my grievance",
        "i want a grievance hearing",
        "please register my grievance",
        "i am grieving the treatment at work",
        "this is my written grievance",
        "start the grievance process",
        "i have a grievance to lodge",
        "my formal grievance follows",
        "i am complaining through the grievance procedure",
        "please acknowledge my grievance",
        "this workplace grievance needs a person",
    ),
}

_TITLE = re.compile(
    r"\b(?:safeguarding|whistleblowing|grievance|distress) policy\b",
    re.IGNORECASE,
)
_INJECTION = (
    r"ignore previous instructions",
    r"ignore all previous instructions",
    r"report no issues",
    r"say there are no issues",
    r"say no issues",
    r"publish this translation",
    r"send the translation",
    r"overwrite the document",
    r"overwrite this document",
    r"treat the caller glossary as authoritative",
    r"drop the protective marking",
    r"strip the legal hold",
    r"ignore the retention",
    r"you are now the reviewer",
    r"the translation is already approved",
    r"high risk is already validated",
    r"mark translation_owned",
    r"the reviewer has already signed",
    r"do not flag the error",
    r"skip the bilingual reviewer",
)


def _patterns(stems: tuple[str, ...]) -> re.Pattern[str]:
    body = "|".join(re.escape(stem) for stem in stems)
    return re.compile(rf"\b(?:{body})\b", re.IGNORECASE)


_RISK = {name: _patterns(stems) for name, stems in RISK_STEMS.items()}
_SENSITIVE = {name: _patterns(stems) for name, stems in SENSITIVE_STEMS.items()}
_INJECTION_RE = _patterns(_INJECTION)


def risk_categories(text: str) -> list[str]:
    """Affirmed risk only. A denial in the same sentence is not a match."""

    affirmed = neighbours()["regex_affirmed"]
    found = []
    for name, pattern in _RISK.items():
        if affirmed(text or "", pattern):
            found.append(name)
    return found


def sensitive_categories(text: str) -> list[str]:
    """Personal cues, including a paraphrase and including a denial.

    A policy title such as "safeguarding policy" is not a personal cue.
    """

    present = neighbours()["regex_present"]
    sentences = neighbours()["sentences"]
    found = []
    for sentence in sentences(text or ""):
        if _TITLE.search(sentence) and not present(sentence, _SENSITIVE["distress"]):
            # A title alone is not a cue. A distress stem in the same sentence still is.
            remainder = _TITLE.sub(" ", sentence)
            for name, pattern in _SENSITIVE.items():
                if name == "distress":
                    continue
                if present(remainder, pattern) and name not in found:
                    # The title words were removed. A real stem can still match.
                    found.append(name)
            if present(sentence, _SENSITIVE["distress"]) and "distress" not in found:
                found.append("distress")
            continue
        for name, pattern in _SENSITIVE.items():
            if present(sentence, pattern) and name not in found:
                found.append(name)
    return found


def distress_sentences(text: str) -> list[str]:
    present = neighbours()["regex_present"]
    sentences = neighbours()["sentences"]
    hit = []
    for sentence in sentences(text or ""):
        if any(present(sentence, pattern) for pattern in _SENSITIVE.values()):
            if _TITLE.fullmatch(sentence.strip()):
                continue
            hit.append(sentence)
    return hit


def injection_signals(text: str) -> list[str]:
    """An instruction that was affirmed. A denial is not an instruction."""

    affirmed = neighbours()["regex_affirmed"]
    if not affirmed(text or "", _INJECTION_RE):
        return []
    signals = []
    for stem in _INJECTION:
        if affirmed(text or "", re.compile(rf"\b{re.escape(stem)}\b", re.IGNORECASE)):
            signals.append(stem)
    return signals
