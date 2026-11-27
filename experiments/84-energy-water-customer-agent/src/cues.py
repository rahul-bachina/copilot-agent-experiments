"""Cues in a customer message or an account note.

Sensitive stems are handed to a person even when the sentence denies them.
An instruction, a forged confirmation, a complaint, and a human request use
the same-sentence negation rule. "It is not true that the message includes
ignore previous instructions" is not an instruction that was given.

A policy title is not a personal cue. A personal sentence still is.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import regex_affirmed, regex_present
else:
    from .negate import regex_affirmed, regex_present

_POLICY_ONLY = re.compile(
    r"\b(?:safeguarding|whistle-?blowing|grievance|mental health|disability|"
    r"prepayment|complaints?|priority services)\s+(?:policy|procedure)\b",
    re.IGNORECASE,
)
_PERSONAL = re.compile(r"\b(i|i'm|i’ve|i've|my|we|me|our)\b", re.IGNORECASE)

_MEDICAL = re.compile(
    r"medical equipment|oxygen machine|oxygen concentrator|\bdialysis\b|"
    r"\bventilator\b|nebuliser|nebulizer|breathing machine|kidney machine|"
    r"life support|refrigerated medicine|insulin that needs a fridge|"
    r"powered medical|home dialysis",
    re.IGNORECASE,
)
_AGE = re.compile(
    r"i am \d{1,3} years old|i'm \d{1,3} years old|i am elderly|i'm elderly|"
    r"i am of pensionable age|i have reached pensionable age|i am of pension age|"
    r"i am an older person|my advanced age|i am aged \d{1,3}\b",
    re.IGNORECASE,
)
_DISABILITY = re.compile(
    r"i am disabled|i'm disabled|i have a disability|my disability|"
    r"i am blind|i'm blind|i am deaf|i'm deaf|wheelchair|"
    r"mobility impairment|visual impairment|hearing impairment|"
    r"long-term medical condition|long term medical condition|"
    r"i cannot walk|i can't walk",
    re.IGNORECASE,
)
_HARDSHIP = re.compile(
    r"financial hardship|cannot afford|can't afford|struggling to pay|"
    r"no money for|choosing between heating and eating|cannot buy food|"
    r"can't buy food|cannot heat the home|can't heat the home|"
    r"no money left for the bill|skint and cannot",
    re.IGNORECASE,
)
_BEREAVEMENT = re.compile(
    r"\bbereavement\b|\bbereaved\b|passed away|my husband died|my wife died|"
    r"my partner died|my mother died|my father died|\bfuneral\b|"
    r"i am widowed|i'm widowed|death of my",
    re.IGNORECASE,
)
_MENTAL = re.compile(
    r"my mental health|i have depression|i'm depressed|my anxiety|"
    r"i have anxiety|psychiatric|mental-health crisis|i feel depressed",
    re.IGNORECASE,
)
_LANGUAGE = re.compile(
    r"do not speak english|don't speak english|cannot read english|"
    r"can't read english|need an interpreter|english is not my language|"
    r"please write in welsh|i need this in welsh|cannot understand english|"
    r"can't understand english|translation into|i need a translator",
    re.IGNORECASE,
)
_DISTRESS = re.compile(
    r"can(?:not|'t) cope|impossible to cope|not coping|struggling to cope|unable to cope|"
    r"suicid|do not want to be alive|don't want to be alive|no longer want to live|"
    r"end(?:ing)? my life|kill (?:myself|themselves|himself|herself)|"
    r"\bfrightened\b|\bscared\b|do not feel safe|don't feel safe|does not feel safe|"
    r"doesn't feel safe|not safe here|feel(?:s|ing)? (?:utterly )?desperate|\bdesperate\b|"
    r"in distress|self-harm|harm myself|cannot go on|can't go on|no way out",
    re.IGNORECASE,
)
_SAFEGUARDING = re.compile(
    r"safeguarding (?:concern|disclosure|alert|issue|matter|note)|"
    r"treat this as safeguarding|child protection(?!\s+policy)|harm to a child|"
    r"a child may be at risk|at risk of harm|adult at risk|child is being harmed",
    re.IGNORECASE,
)
_WHISTLE = re.compile(
    r"whistle[\s-]?blow(?:ing|er)?|protected disclosure|public interest (?:concern|disclosure)|"
    r"blow(?:ing)? the whistle",
    re.IGNORECASE,
)
_GRIEVANCE = re.compile(
    r"(?:raise|raising|lodge|lodging|file|filing|submit|submitting)\s+(?:a\s+|my\s+|the\s+)?grievance|"
    r"my grievance|formal grievance",
    re.IGNORECASE,
)
_SAR = re.compile(
    r"subject access request|\bsar\b|copy of (?:all )?my (?:personal )?data|"
    r"what data do you hold|data you hold about me|right of access",
    re.IGNORECASE,
)
_FOI = re.compile(
    r"freedom of information|\bfoi\b|environmental information request|"
    r"request under (?:the )?foi|information request about the company",
    re.IGNORECASE,
)
_COMPLAINT = re.compile(
    r"i want to complain|i wish to complain|this is a complaint|make a complaint|"
    r"formal complaint|i am unhappy with|i'm unhappy with|i am dissatisfied|"
    r"i'm dissatisfied|i am disgusted|i'm disgusted",
    re.IGNORECASE,
)
_HUMAN = re.compile(
    r"speak to a person|talk to a human|human advisor|real person|"
    r"not a bot|transfer me to a person|i want a human|talk to someone who works|"
    r"put me through to a person|speak to an advisor|speak to an adviser",
    re.IGNORECASE,
)
_AFFORD = re.compile(
    r"\baffordability\b|cannot afford|can't afford|struggling to afford|"
    r"income is not enough|income isn't enough|cannot afford the bill|"
    r"can't afford the bill",
    re.IGNORECASE,
)
_DEBT = re.compile(
    r"i am in debt|i'm in debt|debt collector|\barrears\b|outstanding debt|"
    r"write off the debt|write off my debt|i owe you|money i owe|"
    r"my debt with you",
    re.IGNORECASE,
)
_DISCONNECT = re.compile(
    r"\bdisconnect(?:ion|ed|ing)?\b|cut off my supply|cut my (?:gas|electricity|water) off|"
    r"cut me off|warrant for (?:entry|disconnection)|lose my supply",
    re.IGNORECASE,
)
_PREPAY = re.compile(
    r"prepayment meter|prepayment|prepay meter|pay as you go meter|"
    r"pay-as-you-go meter|top-up meter|top up meter|install a prepay|"
    r"switch me to prepay|switch to a prepayment",
    re.IGNORECASE,
)
_INJECTION = re.compile(
    r"ignore (?:all |the )?(?:previous|above|earlier) instructions|"
    r"disregard (?:the )?(?:previous|earlier) instructions|"
    r"forget the previous instructions|you are now the (?:advisor|adviser|agent)|"
    r"change the tariff now|write off the debt now|drop the legal hold|"
    r"strip the protective marking|override the (?:policy|rules)|"
    r"system prompt|ignore the pinned (?:policy|rules)|"
    r"do not flag this|mark the customer as vulnerable",
    re.IGNORECASE,
)
_FORGED = re.compile(
    r"i already confirmed|confirmation is recorded|confirmation recorded|"
    r"consider this confirmed|the customer has confirmed|skip the confirmation|"
    r"explicit_confirm\s*[:=]?\s*true|already been confirmed|"
    r"treat the embedded confirmation as enough|confirmation_recorded as true|"
    r"i confirm the action was accepted|the hash is already approved",
    re.IGNORECASE,
)
_LEADING = re.compile(
    r"prefer british|only help men|only help women|refuse disabled customers|"
    r"prefer customers from the|weight (?:male|female|older|younger) customers|"
    r"always side with the supplier|treat foreign names as|"
    r"no help for people on benefits|leading criterion|"
    r"only serve english speakers|bias the queue",
    re.IGNORECASE,
)
_METER_ASK = re.compile(
    r"submit my meter reading|submit this meter reading|here is my meter reading|"
    r"please (?:log|take|record) my (?:meter )?reading|log this reading",
    re.IGNORECASE,
)
_PLAN_ASK = re.compile(
    r"request a payment plan|request a payment arrangement|"
    r"please ask for a payment plan|ask for a payment arrangement",
    re.IGNORECASE,
)
_PLAN_AGREE = re.compile(
    r"agree the payment plan|agree a payment plan|agree my payment plan|"
    r"payment plan is agreed|approve my payment plan",
    re.IGNORECASE,
)
_PSR_ASK = re.compile(
    r"refer me to the priority services register|"
    r"submit a priority services register request|"
    r"ask to be added to the priority services register|"
    r"request a priority services register referral",
    re.IGNORECASE,
)
_TARIFF = re.compile(
    r"change my tariff|switch my tariff|change the tariff|cheapest tariff|"
    r"move me to another tariff|put me on a cheaper tariff",
    re.IGNORECASE,
)
_WRITE_OFF = re.compile(
    r"write off the debt|write off my debt|waive the debt|cancel the debt|"
    r"wipe the balance",
    re.IGNORECASE,
)
_INSTALL = re.compile(
    r"install a prepayment meter|install a prepay|fit a prepayment meter|"
    r"switch me to a prepayment meter|switch me to prepay|"
    r"switch the meter to prepay|change the meter to prepayment",
    re.IGNORECASE,
)
_CARVE = re.compile(
    r"\bexcept\b|\bunless\b|provided that|subject to|save where|save that|"
    r"apart from|other than|only if|only when|\bcarve-out\b",
    re.IGNORECASE,
)
_ROLE = re.compile(
    r"\bi am the account holder\b|\bmy role is\b|\bmy clearance is\b|"
    r"\bi am the advisor\b|\bi am the adviser\b",
    re.IGNORECASE,
)


def _policy_title_only(text: str) -> bool:
    if not text or not _POLICY_ONLY.search(text):
        return False
    return _PERSONAL.search(text) is None


def _sensitive(text: str, pattern: re.Pattern[str]) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_present(text, pattern)


def medical_hit(text: str) -> bool:
    return _sensitive(text, _MEDICAL)


def age_hit(text: str) -> bool:
    return _sensitive(text, _AGE)


def disability_hit(text: str) -> bool:
    return _sensitive(text, _DISABILITY)


def hardship_hit(text: str) -> bool:
    return _sensitive(text, _HARDSHIP)


def bereavement_hit(text: str) -> bool:
    return _sensitive(text, _BEREAVEMENT)


def mental_health_hit(text: str) -> bool:
    return _sensitive(text, _MENTAL)


def language_hit(text: str) -> bool:
    return _sensitive(text, _LANGUAGE)


def distress_hit(text: str) -> bool:
    return _sensitive(text, _DISTRESS)


def safeguarding_hit(text: str) -> bool:
    return _sensitive(text, _SAFEGUARDING)


def whistleblowing_hit(text: str) -> bool:
    return _sensitive(text, _WHISTLE)


def grievance_hit(text: str) -> bool:
    return _sensitive(text, _GRIEVANCE)


def sar_hit(text: str) -> bool:
    return _sensitive(text, _SAR)


def foi_hit(text: str) -> bool:
    return _sensitive(text, _FOI)


def complaint_hit(text: str) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_affirmed(text, _COMPLAINT)


def human_request_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _HUMAN)


def affordability_hit(text: str) -> bool:
    return _sensitive(text, _AFFORD)


def debt_hit(text: str) -> bool:
    return _sensitive(text, _DEBT)


def disconnection_hit(text: str) -> bool:
    return _sensitive(text, _DISCONNECT)


def prepayment_hit(text: str) -> bool:
    return _sensitive(text, _PREPAY)


def injection_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _INJECTION)


def forged_confirmation_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _FORGED)


def leading_hit(text: str) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_affirmed(text, _LEADING)


def meter_request_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _METER_ASK)


def plan_request_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _PLAN_ASK)


def plan_agree_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _PLAN_AGREE)


def psr_request_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _PSR_ASK)


def tariff_change_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _TARIFF)


def write_off_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _WRITE_OFF)


def install_prepay_hit(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _INSTALL)


def carve_out_affirmed(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _CARVE)


def role_claim(text: str) -> bool:
    if not text:
        return False
    return regex_affirmed(text, _ROLE)


def vulnerability_flags(text: str) -> list[str]:
    found = []
    checks = (
        ("medical_equipment", medical_hit),
        ("age", age_hit),
        ("disability", disability_hit),
        ("financial_hardship", hardship_hit),
        ("bereavement", bereavement_hit),
        ("mental_health", mental_health_hit),
        ("language", language_hit),
    )
    for name, fn in checks:
        if fn(text):
            found.append(name)
    return found


def sensitive_flags(text: str) -> list[str]:
    found = []
    checks = (
        ("distress", distress_hit),
        ("safeguarding", safeguarding_hit),
        ("whistleblowing", whistleblowing_hit),
        ("grievance", grievance_hit),
        ("sar", sar_hit),
        ("foi", foi_hit),
    )
    for name, fn in checks:
        if fn(text):
            found.append(name)
    return found
