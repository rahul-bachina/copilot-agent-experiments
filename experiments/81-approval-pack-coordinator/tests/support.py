"""Shared synthetic requests. Invented. Not a real spend."""

AS_OF = "2026-11-25"


def quote(value=4000, content=None, **extra):
    body = content or f"Quote for Northfold Supplies. The price is {value} pounds.\n"
    row = {
        "evidence_id": "EV-QUOTE",
        "checklist_id": "quote",
        "version": "1.0",
        "status": "current",
        "document_date": "2026-10-01",
        "expiry_date": "2027-04-01",
        "signed": True,
        "signed_by_ref": "SUP-0001",
        "value_gbp": value,
        "content": body,
        "metadata": {"marking": "OFFICIAL", "legal_hold": False, "retention": ["keep 6 years"]},
    }
    row.update(extra)
    return row


def budget(value=4000, **extra):
    row = {
        "evidence_id": "EV-BUDGET",
        "checklist_id": "budget_code",
        "version": "1.0",
        "status": "current",
        "document_date": "2026-11-01",
        "signed": False,
        "value_gbp": value,
        "content": "Budget code B-14 covers this roof.\n",
        "metadata": {"marking": "OFFICIAL", "legal_hold": False, "retention": ["keep 6 years"]},
    }
    row.update(extra)
    return row


def business_case(value=18400):
    return {
        "evidence_id": "EV-CASE",
        "checklist_id": "business_case",
        "version": "1.0",
        "status": "current",
        "document_date": "2026-10-15",
        "expiry_date": "2027-04-15",
        "signed": True,
        "signed_by_ref": "SUP-0001",
        "value_gbp": value,
        "content": "The business case supports replacing the north depot roof.\n",
        "metadata": {"marking": "OFFICIAL", "legal_hold": False, "retention": ["keep 6 years"]},
    }


def spend(request_id="REQ-8101", amount=4000, requester="REQ-8101", evidence=None, **extra):
    request = {
        "synthetic": True,
        "request_id": request_id,
        "request_type": "spend",
        "requester_ref": requester,
        "title": "Replace the north depot roof",
        "supplier_name": "Northfold Supplies",
        "amount_gbp": amount,
        "description": "One request for the north depot roof.",
        "evidence": evidence if evidence is not None else [quote(amount), budget(amount)],
    }
    request.update(extra)
    return request


def approval_for(result, approver, decision="approve"):
    payload = {
        "item": "approval-pack",
        "decision": decision,
        "approver_ref": approver,
        "request_id": result["request_id"],
        "content_hash": result["content_hash"],
    }
    for key in result["required_acknowledgements"]:
        payload[key] = True
    return payload
