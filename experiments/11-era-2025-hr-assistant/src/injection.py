"""Detect instructions aimed at the agent inside an untrusted employer pack.

A match is recorded and not followed. It is not a finding about a worker
or about the employer.
"""

from __future__ import annotations

import re

# Each pattern is an instruction to the agent, not a description of a policy.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ignore_instructions", re.compile(r"ignore (?:all |any )?(?:previous|prior|above) instructions", re.I)),
    ("disregard_rules", re.compile(r"disregard (?:the |all )?(?:rules|instructions|checklist)", re.I)),
    ("role_override", re.compile(r"\byou are now\b", re.I)),
    ("system_prefix", re.compile(r"\bsystem\s*:", re.I)),
    ("dismiss_worker", re.compile(r"\b(?:dismiss|sack|fire) (?:the |this )?(?:employee|worker|them)\b", re.I)),
    ("suspend_worker", re.compile(r"\bsuspend (?:the |this )?(?:employee|worker)\b", re.I)),
    ("issue_warning", re.compile(r"\bissue (?:a |the )?warning\b", re.I)),
    ("email_person", re.compile(r"\b(?:email|e-mail|message) (?:the )?(?:complainant|worker|employee|visitor)\b", re.I)),
    ("update_record", re.compile(r"\bupdate (?:the )?(?:hr|personnel|employee) record\b", re.I)),
    ("publish_policy", re.compile(r"\bpublish (?:the |this )?policy\b", re.I)),
    ("mark_compliant", re.compile(r"\bmark (?:the |this )?(?:employer )?compliant\b", re.I)),
    ("state_all_steps", re.compile(r"\bstate that (?:we|the employer) (?:has|have) taken all reasonable steps\b", re.I)),
    ("contact_acas", re.compile(r"\bcontact (?:acas|the helpline)\b", re.I)),
    ("start_claim", re.compile(r"\b(?:file|submit) (?:a |the )?tribunal claim\b", re.I)),
]

PROHIBITED_PAYLOAD_KEYS = (
    "hr_decision",
    "disciplinary_decision",
    "dismiss",
    "suspend",
    "warning_issued",
    "compliance_conclusion",
    "policy_published",
    "records_changed",
    "message_sent",
    "send_email",
    "update_hris",
    "contact_acas",
    "tribunal_deadline",
    "approved",
    "likelihood",
    "impact",
    "residual_risk",
)

# Questions that ask the agent to decide or to calculate. Not an injection
# finding about the worker. The handbook quotation is refused.
QUESTION_REFUSALS: list[tuple[str, re.Pattern[str]]] = [
    ("claim", re.compile(r"\b(do i have a (claim|case)|tribunal claim|take legal action)\b", re.I)),
    (
        "discipline",
        re.compile(
            r"\b(should (?:we|i) (?:dismiss|suspend|sack|fire|warn)|issue a warning|start (?:a )?disciplinary)\b",
            re.I,
        ),
    ),
    (
        "legal_characterisation",
        re.compile(
            r"\b(is this (?:sexual )?harassment|have we (?:complied|breached)|taken all reasonable steps|automatically unfair)\b",
            re.I,
        ),
    ),
    (
        "time_limit",
        re.compile(r"\b(time limit|how long do i have to claim|deadline to claim|limitation period)\b", re.I),
    ),
    (
        "send",
        re.compile(r"\b(?:email|write to|contact) (?:the )?(?:worker|employee|complainant|acas|tribunal)\b", re.I),
    ),
]


def signals_in_text(text: str) -> list[str]:
    """Return pattern ids found in text. Empty if text is not a string."""
    if not isinstance(text, str) or not text.strip():
        return []
    return [name for name, pattern in _PATTERNS if pattern.search(text)]


def question_refusal_reasons(text: str) -> list[str]:
    """Reasons to refuse a handbook question. Empty if the text can be matched to a topic."""
    if not isinstance(text, str) or not text.strip():
        return []
    return [name for name, pattern in QUESTION_REFUSALS if pattern.search(text)]
