"""Reasonable-endeavours drafts and Housing Ombudsman information.

The record does not decide that a defence is made out. The Ombudsman block
does not refer a complaint. Nothing here is filed or sent.
"""

from __future__ import annotations

from datetime import date

OMBUDSMAN_HOME = "https://www.housing-ombudsman.org.uk/"
OMBUDSMAN_COMPLAIN = "https://www.housing-ombudsman.org.uk/residents/how-to-complain-to-your-landlord/"
OMBUDSMAN_WHEN = "https://www.housing-ombudsman.org.uk/residents/when-to-get-help-from-the-housing-ombudsman/"
CODE_PDF = "https://www.housing-ombudsman.org.uk/app/uploads/2024/09/03.Complaint-Handling-Code-24.pdf"

STEP_KINDS = (
    "access_attempt",
    "tenant_contact",
    "consent_request",
    "regulator_application",
    "contractor_search",
    "decant_search",
    "other",
)


def ombudsman_information() -> dict:
    """Published escalation information. Not a referral and not a deadline."""
    return {
        "service": "Housing Ombudsman Service",
        "referral_made_by_agent": False,
        "jurisdiction_decided_by_agent": False,
        "urls": {
            "service": OMBUDSMAN_HOME,
            "how_to_complain_to_the_landlord": OMBUDSMAN_COMPLAIN,
            "when_to_contact_the_ombudsman": OMBUDSMAN_WHEN,
            "complaint_handling_code": CODE_PDF,
        },
        "retrieved_on": "2026-10-24",
        "landlord_procedure": {
            "stages": 2,
            "source": "Housing Ombudsman Complaint Handling Code, and the resident pages cited above",
            "stage_1": {
                "acknowledge_within_working_days_of_receipt": 5,
                "respond_within_working_days_of_acknowledgement": 10,
                "extension_without_good_reason_further_working_days": 10,
                "extension_must_include_ombudsman_contact_details": True,
            },
            "stage_2": {
                "acknowledge_within_working_days_of_escalation_request": 5,
                "final_response_within_working_days_of_acknowledgement": 20,
                "extension_without_good_reason_further_working_days": 20,
                "extension_must_include_ombudsman_contact_details": True,
                "decided_by_a_different_person_from_stage_1": True,
            },
            "working_day_defined_in_the_code_text_read": False,
            "note": (
                "The Code text read on 24 October 2026 did not define 'working day'. "
                "This module does not turn those numbers into an operative date. "
                "The landlord's own procedure should be checked."
            ),
        },
        "after_the_landlords_final_response": (
            "The resident pages read on 24 October 2026 say the Ombudsman can "
            "accept a complaint for investigation where the landlord's stage 2 "
            "response is dated within 12 months. The agent does not refer the "
            "resident and does not decide that the Ombudsman can consider the complaint."
        ),
    }


def draft_endeavours_record(
    steps: list[dict] | None = None,
    *,
    barrier: str | None = None,
    officer_approved: bool = False,
) -> dict:
    """Draft a record from steps the officer typed. No step is invented."""
    supplied = list(steps or [])
    cleaned = [_clean_step(step, index) for index, step in enumerate(supplied, start=1)]
    return {
        "status": "draft_for_officer",
        "may_be_filed_by_agent": False,
        "officer_approved": officer_approved,
        "defence_made_out": False,
        "decided_by_agent": False,
        "barrier_recorded_by_officer": barrier,
        "steps": cleaned,
        "steps_invented": False,
        "statutory_hooks": [
            {
                "id": "section_10A_5",
                "text": (
                    "In proceedings for breach of the covenant implied by section 10A(2), "
                    "it is a defence for the lessor to prove that the lessor used all "
                    "reasonable endeavours to avoid that breach."
                ),
            },
            {
                "id": "consent_off_ramp",
                "text": (
                    "Regulations 5(6), 11(3) and 13(5) stop particular duties where work "
                    "cannot lawfully be done without another person's consent and the lessor "
                    "has exhausted all reasonable endeavours to obtain it. Recording a step "
                    "is not a finding that endeavours are exhausted."
                ),
            },
        ],
        "guidance_note": (
            "MHCLG guidance retrieved on 24 October 2026 says landlords should keep "
            "records of access attempts, correspondence, approvals and attempts to "
            "find contractors or accommodation, and that a court decides whether all "
            "reasonable endeavours were used. This draft does not decide that."
        ),
        "note": (
            "No visit, call, letter or application has been added by the agent. "
            "If the list is empty, that is because the officer has not entered a step."
            + (
                " An officer has marked this draft as ready for them to file outside this agent. The agent has not filed it."
                if officer_approved
                else " An officer has not approved this record."
            )
        ),
    }


def _clean_step(step: dict, index: int) -> dict:
    if not isinstance(step, dict):
        raise ValueError(f"step {index} must be an object")
    kind = step.get("kind", "other")
    if kind not in STEP_KINDS:
        raise ValueError(f"step {index} has an unknown kind")
    on = step.get("on")
    if not on:
        raise ValueError(f"step {index} needs a date")
    parsed = date.fromisoformat(str(on))
    what = str(step.get("what", "")).strip()
    if not what:
        raise ValueError(f"step {index} needs a description of what was done")
    return {
        "on": parsed.isoformat(),
        "kind": kind,
        "what": what,
        "outcome": str(step.get("outcome", "")).strip(),
        "entered_by": "officer",
    }
