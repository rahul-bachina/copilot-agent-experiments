"""Freedom of Information Act 2000 section 40(1) and mixed requests.

Section 40(1) was opened on 27 November 2026. An FOI request for the
applicant's own personal data is not answered under FOI. A mixed request is
routed to a person. This module does not call Experiment 01, because that
triage path can call a model.
"""

from __future__ import annotations

if __package__ in {None, ""}:
    from negate import affirmed
else:
    from .negate import affirmed

_FOI = (
    "freedom of information",
    "foi request",
    "under the foi act",
    "environmental information regulations",
    "eir request",
)
_OWN = (
    "my personal data",
    "personal data about me",
    "information you hold about me",
    "information held about me",
    "data about me",
    "my information",
    "subject access",
    "subject access request",
)
_OTHER = (
    "information that is not about me",
    "not about me",
    "council policy",
    "the policy on",
    "the contract for",
    "all reports on",
    "minutes of the meeting",
)


def _any(text: str, phrases: tuple[str, ...]) -> list[str]:
    return [phrase for phrase in phrases if affirmed(text or "", phrase)]


def classify(text: str, channel: str) -> dict:
    foi = _any(text, _FOI)
    own = _any(text, _OWN)
    other = _any(text, _OTHER)
    channel_foi = channel == "foi"
    text_is_foi = bool(foi) or channel_foi
    text_is_own = bool(own)
    mixed = text_is_foi and text_is_own and bool(other)
    own_only = text_is_foi and text_is_own and not other
    foi_only = text_is_foi and not text_is_own
    if mixed:
        route = "mixed"
    elif own_only:
        route = "foi_section_40_1"
    elif foi_only:
        route = "foi_not_own_data"
    else:
        route = "subject_access"
    caller_tried_to_drop_sar = channel == "foi" and text_is_own
    return {
        "route": route,
        "foi_phrases_affirmed": foi,
        "own_data_phrases_affirmed": own,
        "other_information_phrases_affirmed": other,
        "section_40_1_candidate": route == "foi_section_40_1",
        "mixed": mixed,
        "foi_disclosure": False,
        "foi_answered": False,
        "caller_channel_did_not_drop_sar": caller_tried_to_drop_sar,
        "experiment_01_called": False,
    }
