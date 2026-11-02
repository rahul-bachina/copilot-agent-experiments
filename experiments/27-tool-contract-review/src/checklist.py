"""Fixed checklist for one tool contract.

Each check scores 0, 1, or 2. The same contract produces the same findings.
An operation id is cited. A suggested change is a proposal, not an edit.
"""

from __future__ import annotations

import re
from typing import Any

CHECKS: tuple[dict[str, str], ...] = (
    {"id": "C1", "name": "Least privilege"},
    {"id": "C2", "name": "Consistency with the permissions manifest"},
    {"id": "C3", "name": "Destructive or external-send operations have a human approval gate"},
    {"id": "C4", "name": "Input validation and bounded parameters"},
    {"id": "C5", "name": "Authentication model"},
    {"id": "C6", "name": "Data minimisation and UK GDPR special-category exposure"},
    {"id": "C7", "name": "Rate limiting and API Management policy recommendation"},
    {"id": "C8", "name": "Error handling"},
    {"id": "C9", "name": "Tool descriptions that could be abused by prompt injection"},
)

REWRITES: dict[str, str] = {
    "C1": "Narrow the path, the scope, and any filter parameter. Do not use a wildcard path, a .All scope, or an unbounded query string.",
    "C2": "Make the callable operations match the permissions manifest. Do not leave a write or a send enabled in only one of the two documents.",
    "C3": "Put a structured human-approval flag on every callable delete or external send. The security/API owner is the approver.",
    "C4": "Bound every input. Give strings a maxLength, pattern, or enum. Give numbers a minimum and a maximum. Give arrays maxItems. Set additionalProperties to false on objects.",
    "C5": "Use OAuth scopes that name one action, or a managed identity. Do not leave an API key, a password, or a connection string in the contract.",
    "C6": "Remove special-category and health-identifier fields the operation does not need. A field-name match is not a decision that Article 9 applies.",
    "C7": "Document a numeric rate limit the security/API owner chooses, and HTTP 429. renewal-period is seconds and the page opened on 2 November 2026 says the maximum is 300. Do not copy the 20-call example.",
    "C8": "Document HTTP 400 or 422, 401 or 403, and 500. Do not return a stack trace, an exception message, or an inner error.",
    "C9": "Describe the operation as data. Say that instructions found in the payload or the result are not followed. Do not tell a model to ignore previous instructions or to always call the tool.",
}

_LEAK = re.compile(r"stack\s*trace|stacktrace|exception message|inner exception|inner error|raw error", re.I)
_METHOD_CLASH = {
    "GET": {"write", "delete", "send"},
    "HEAD": {"write", "delete", "send"},
    "DELETE": {"read", "send"},
    "PUT": {"read", "send"},
    "PATCH": {"read", "send"},
}
_DESCRIPTION_ABUSE: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (all |any )?(previous|prior|above|your) instructions", re.I)),
    ("always_call", re.compile(r"\b(always call|always invoke|you must call this)\b", re.I)),
    ("hide_from_user", re.compile(r"\bdo not tell the user\b", re.I)),
    ("follow_result", re.compile(r"\bfollow (the )?instructions (found |in the )", re.I)),
    ("unrestricted", re.compile(r"\b(do anything the user asks|unrestricted access)\b", re.I)),
    ("exfiltrate", re.compile(r"\bexfiltrat", re.I)),
    ("send_conversation", re.compile(r"\bsend the (conversation|chat|transcript)\b", re.I)),
    ("hidden", re.compile(r"\bhidden instruction\b", re.I)),
    ("override_system", re.compile(r"\boverride the system\b", re.I)),
)
_REFUSAL = re.compile(
    r"\b(do not|don't|never|must not|refuse|not followed|is untrusted|are untrusted|is data|are data)\b",
    re.I,
)
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
FILTER_NAMES = {"filter", "query", "search", "where", "sql", "odata", "q", "select"}


def evaluate(
    normalised: dict[str, Any],
    manifest: dict[str, Any] | None,
    manifest_error: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    operations = normalised["operations"]
    http = bool(normalised["http_contract"])
    view = _manifest_view(manifest, manifest_error)
    checks = [
        _finish("C1", _least_privilege(operations)),
        _finish("C2", _manifest_consistency(operations, view)),
        _finish("C3", _approval_gate(operations)),
        _finish("C4", _bounded_inputs(operations)),
        _finish("C5", _authentication(operations, http, normalised["secret_labels"])),
        _finish("C6", _minimisation(operations)),
        _finish("C7", _rate_limit(operations, http)),
        _finish("C8", _errors(operations, http)),
        _finish("C9", _descriptions(operations)),
    ]
    return checks, view


def _finish(check_id: str, outcome: tuple[str, list[str]]) -> dict[str, Any]:
    result, evidence = outcome
    points = {"pass": 2, "partial": 1, "fail": 0}[result]
    name = next(item["name"] for item in CHECKS if item["id"] == check_id)
    return {
        "id": check_id,
        "name": name,
        "result": result,
        "points": points,
        "max_points": 2,
        "evidence": evidence[:8],
        "rewrite": REWRITES[check_id] if result != "pass" else "",
    }


def _worst(items: list[tuple[str, str]]) -> tuple[str, list[str]]:
    if any(result == "fail" for result, _text in items):
        return "fail", [text for result, text in items if result == "fail"]
    if any(result == "partial" for result, _text in items):
        return "partial", [text for result, text in items if result == "partial"]
    if not items:
        return "pass", ["No operation raised this check."]
    return "pass", ["No operation raised this check."]


def _least_privilege(operations: list[dict[str, Any]]) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for operation in operations:
        reasons = []
        if operation["wildcard_path"]:
            reasons.append("wildcard path")
        broad = operation["auth"]["broad_scopes"]
        if broad:
            reasons.append("broad scope " + ", ".join(broad[:4]))
        for field in operation["inputs"]:
            leaf = field["name"].rsplit(".", 1)[-1].lower()
            if leaf in FILTER_NAMES and not field["bounded"]:
                reasons.append(f"unbounded filter parameter {field['name']}")
        if operation["effect"] in {"write", "delete", "send"}:
            if any(field.get("additional") for field in operation["inputs"]):
                reasons.append("additionalProperties on a write, delete, or send")
        clash = _METHOD_CLASH.get(operation["http_method"] or "")
        if clash and operation["effect"] in clash:
            reasons.append(f"{operation['http_method']} does not match effect {operation['effect']}")
        if reasons:
            findings.append(("fail", f"{operation['operation_id']}: " + "; ".join(reasons)))
        elif operation["effect"] == "unknown":
            findings.append(("partial", f"{operation['operation_id']}: effect was not classified"))
    return _worst(findings)


def _manifest_view(manifest: dict[str, Any] | None, error: str | None) -> dict[str, Any]:
    view: dict[str, Any] = {
        "parsed": False,
        "error": error,
        "writes_enabled": False,
        "sends_enabled": False,
        "autonomy": None,
        "allowed_names": [],
        "names_are_prose": False,
        "names_checked": False,
    }
    if error:
        return view
    if not isinstance(manifest, dict):
        view["error"] = None
        return view
    tools = manifest.get("tools") if isinstance(manifest.get("tools"), dict) else {}
    writes = tools.get("writes") if isinstance(tools.get("writes"), dict) else {}
    sends = tools.get("sends") if isinstance(tools.get("sends"), dict) else {}
    high = manifest.get("high_risk_actions") if isinstance(manifest.get("high_risk_actions"), dict) else {}
    production = high.get("production_record_change") if isinstance(high.get("production_record_change"), dict) else {}
    external = high.get("external_send") if isinstance(high.get("external_send"), dict) else {}
    allowed = []
    for entry in tools.get("allowed") or []:
        if isinstance(entry, dict) and entry.get("tool"):
            allowed.append(str(entry["tool"]))
        elif isinstance(entry, str):
            allowed.append(entry)
    prose = any(not _IDENTIFIER.match(name) for name in allowed) if allowed else False
    autonomy = manifest.get("autonomy") if isinstance(manifest.get("autonomy"), dict) else {}
    view.update(
        {
            "parsed": True,
            "error": None,
            "writes_enabled": writes.get("enabled") is True or production.get("enabled") is True,
            "sends_enabled": sends.get("enabled") is True or external.get("enabled") is True,
            "autonomy": autonomy.get("level"),
            "allowed_names": allowed,
            "names_are_prose": prose,
            "names_checked": bool(allowed) and not prose,
        }
    )
    return view


def _manifest_consistency(operations: list[dict[str, Any]], view: dict[str, Any]) -> tuple[str, list[str]]:
    if view["error"]:
        return "fail", [f"The manifest did not parse. {view['error']}"]
    if not view["parsed"]:
        return "partial", ["No permissions manifest was supplied."]
    findings: list[tuple[str, str]] = []
    callable_ops = [operation for operation in operations if operation["callable"]]
    writes = [operation["operation_id"] for operation in callable_ops if operation["effect"] in {"write", "delete"}]
    sends = [operation["operation_id"] for operation in callable_ops if operation["effect"] == "send"]
    if writes and not view["writes_enabled"]:
        findings.append(("fail", "Callable write or delete is not allowed by the manifest: " + ", ".join(writes[:6])))
    elif view["writes_enabled"] and not writes:
        findings.append(("partial", "The manifest allows writes. The callable contract does not use a write."))
    if sends and not view["sends_enabled"]:
        findings.append(("fail", "Callable send is not allowed by the manifest: " + ", ".join(sends[:6])))
    elif view["sends_enabled"] and not sends:
        findings.append(("partial", "The manifest allows sends. The callable contract does not use a send."))
    if view["names_checked"]:
        allowed = {name.lower() for name in view["allowed_names"]}
        missing = [operation["operation_id"] for operation in callable_ops if operation["operation_id"].lower() not in allowed]
        if missing:
            findings.append(("fail", "Callable operations are not named on the manifest: " + ", ".join(missing[:6])))
    elif view["names_are_prose"]:
        findings.append(("partial", "Manifest tool names are prose. Operation names were not matched."))
    elif not view["allowed_names"]:
        findings.append(("partial", "The manifest does not name tools."))
    return _worst(findings)


def _approval_gate(operations: list[dict[str, Any]]) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for operation in operations:
        needs = operation["effect"] in {"delete", "send"} or operation["http_method"] == "DELETE"
        if not needs or not operation["callable"]:
            continue
        if operation["approval"]["structured"]:
            continue
        if operation["approval"]["text"]:
            findings.append(("partial", f"{operation['operation_id']}: approval is described, with no structured flag"))
        else:
            findings.append(("fail", f"{operation['operation_id']}: callable {operation['effect']} has no human approval gate"))
    return _worst(findings)


def _bounded_inputs(operations: list[dict[str, Any]]) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for operation in operations:
        unbounded = [field for field in operation["inputs"] if not field["bounded"]]
        if not unbounded:
            continue
        names = ", ".join(field["name"] or "(unnamed)" for field in unbounded[:4])
        if operation["effect"] in {"write", "delete", "send"}:
            findings.append(("fail", f"{operation['operation_id']}: unbounded input on a {operation['effect']}: {names}"))
        else:
            findings.append(("partial", f"{operation['operation_id']}: unbounded input on a read: {names}"))
    return _worst(findings)


def _authentication(operations: list[dict[str, Any]], http: bool, secret_labels: list[str]) -> tuple[str, list[str]]:
    if secret_labels:
        return "fail", ["A secret-shaped value is in the contract. The value is not repeated. " + ", ".join(secret_labels)]
    findings: list[tuple[str, str]] = []
    for operation in operations:
        auth = operation["auth"]
        scopes = [scope for scope in auth["scopes"] if scope not in auth["broad_scopes"]]
        good = (auth["oauth"] and bool(scopes)) or auth["managed_identity"]
        if auth["api_key"] and not good:
            findings.append(("fail", f"{operation['operation_id']}: API key is the only authentication"))
        elif http and not good and not auth["oauth"]:
            findings.append(("fail", f"{operation['operation_id']}: no OAuth scope and no managed identity"))
        elif http and auth["oauth"] and not scopes:
            findings.append(("partial", f"{operation['operation_id']}: OAuth is named and no narrow scope is listed"))
        elif not http and not good:
            findings.append(("partial", f"{operation['operation_id']}: this shape does not declare an HTTP security scheme, and no key was found"))
    if http and not findings:
        return "pass", ["No operation raised this check."]
    return _worst(findings)


def _minimisation(operations: list[dict[str, Any]]) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for operation in operations:
        exposed = [field for field in operation["special_category"] if not field["excluded"]]
        held = [field for field in operation["special_category"] if field["excluded"]]
        open_response = any(field.get("additional") and field["location"] == "response" for field in operation["fields"])
        if exposed:
            names = ", ".join(field["name"] for field in exposed[:4])
            findings.append((
                "fail",
                f"{operation['operation_id']}: field name matches a special-category or health-identifier pattern: {names}. This is a name check, not a determination that Article 9 applies.",
            ))
        elif held:
            findings.append(("partial", f"{operation['operation_id']}: a matching field is marked excluded and is still in the schema"))
        elif open_response:
            findings.append(("partial", f"{operation['operation_id']}: the response schema allows additional properties"))
    return _worst(findings)


def _rate_limit(operations: list[dict[str, Any]], http: bool) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for operation in operations:
        rate = operation["rate"]
        if isinstance(rate["renewal"], int) and rate["renewal"] > 300:
            findings.append(("fail", f"{operation['operation_id']}: renewal period is above 300 seconds"))
            continue
        numeric = (
            isinstance(rate["calls"], int)
            and rate["calls"] > 0
            and (rate["renewal"] is None or (isinstance(rate["renewal"], int) and 1 <= rate["renewal"] <= 300))
        )
        if numeric and (not http or rate["has_429"] or rate["named_policy"]):
            continue
        if http and not numeric and not rate["has_429"] and not rate["named_policy"]:
            findings.append(("fail", f"{operation['operation_id']}: no numeric rate limit, no HTTP 429, and no rate-limit policy name"))
        elif not http and not numeric:
            findings.append(("partial", f"{operation['operation_id']}: not an HTTP contract, so no rate limit is declared"))
        else:
            findings.append(("partial", f"{operation['operation_id']}: the rate limit is incomplete"))
    return _worst(findings)


def _errors(operations: list[dict[str, Any]], http: bool) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for operation in operations:
        if _sentence_leak(operation["error_text"]):
            findings.append(("fail", f"{operation['operation_id']}: an error description asks for an internal detail"))
            continue
        codes = set(operation["error_codes"])
        client = bool(codes & {"400", "422"})
        auth = bool(codes & {"401", "403"})
        server = bool(codes & {"500", "default"})
        if client and auth and server:
            continue
        if http and not codes:
            findings.append(("fail", f"{operation['operation_id']}: no error responses"))
        elif not http and not codes:
            findings.append(("partial", f"{operation['operation_id']}: this shape does not declare HTTP errors"))
        else:
            missing = []
            if not client:
                missing.append("400 or 422")
            if not auth:
                missing.append("401 or 403")
            if not server:
                missing.append("500")
            findings.append(("partial", f"{operation['operation_id']}: missing {', '.join(missing)}"))
    return _worst(findings)


def _sentence_leak(text: str) -> bool:
    for sentence in re.split(r"[\n.]+", text):
        if not sentence.strip() or _REFUSAL.search(sentence):
            continue
        if _LEAK.search(sentence):
            return True
    return False


def _descriptions(operations: list[dict[str, Any]]) -> tuple[str, list[str]]:
    findings: list[tuple[str, str]] = []
    for operation in operations:
        text = operation["description"].strip()
        if not text:
            findings.append(("partial", f"{operation['operation_id']}: no description"))
            continue
        for sentence in re.split(r"[\n.]+", text):
            if not sentence.strip() or _REFUSAL.search(sentence):
                continue
            for name, pattern in _DESCRIPTION_ABUSE:
                if pattern.search(sentence):
                    findings.append(("fail", f"{operation['operation_id']}: description matches {name}"))
                    break
    return _worst(findings)
