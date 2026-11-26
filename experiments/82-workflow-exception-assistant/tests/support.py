"""Builders for synthetic run requests."""

from src.workflow import pinned_directory


AS_OF = "2026-11-26"


def step(step_id, name, status="Failed", codes=None, text="", output="", **extra):
    row = {
        "step_id": step_id,
        "name": name,
        "status": status,
        "started_at": "2026-11-20T09:00:00Z",
        "ended_at": "2026-11-20T09:01:00Z",
        "error_codes": list(codes or []),
        "error_text": text,
        "output_text": output,
    }
    row.update(extra)
    return row


def run(run_id, steps, process_id="PROC-LOOKUP-01", status="Failed", **extra):
    row = {
        "run_id": run_id,
        "process_id": process_id,
        "status": status,
        "started_at": "2026-11-20T09:00:00Z",
        "ended_at": "2026-11-20T09:02:00Z",
        "trigger_user_ref": "USR-8201",
        "protective_marking": "OFFICIAL",
        "legal_hold": False,
        "retention": ["RETAIN 6 YEARS"],
        "cover": "",
        "notes": "",
        "steps": steps,
    }
    row.update(extra)
    return row


def request(runs, process_id="PROC-LOOKUP-01", diagnosis_id="DX-8210", **extra):
    row = {
        "synthetic": True,
        "diagnosis_id": diagnosis_id,
        "process_id": process_id,
        "owner_ref": "OWN-8201",
        "question_date": AS_OF,
        "runs": runs,
    }
    row.update(extra)
    return row


def decision_for(result, action="route", approver="OWN-8201", **extra):
    decision = {
        "item": "owner-decision",
        "decision": action,
        "action_id": action,
        "approver_ref": approver,
        "diagnosis_id": result["diagnosis_id"],
        "content_hash": result["content_hash"],
    }
    for key in result["required_acknowledgements"]:
        decision[key] = True
    decision.update(extra)
    return decision


def directory():
    return pinned_directory()
