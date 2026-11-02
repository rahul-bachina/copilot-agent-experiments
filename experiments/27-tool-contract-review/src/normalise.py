"""Turn one pasted contract into operations.

OpenAPI is read as a subset of OpenAPI 3. The MCP list, the Copilot Studio
action list, and the Foundry-shaped list are reading shapes for this
reviewer. They are not a claim about a vendor export file.
"""

from __future__ import annotations

import json
import re
from typing import Any

FILTER_NAMES = {"filter", "query", "search", "where", "sql", "odata", "q", "select"}
BOUNDED_FORMATS = {"date", "date-time", "uuid"}
HTTP_KINDS = {"openapi", "copilot_studio"}

_WRITE = re.compile(r"\b(create|update|write|insert|upsert|post|apply|deploy|publish|modify|patch)\b", re.I)
_DELETE = re.compile(r"\b(delete|destroy|purge|drop|remove)\b", re.I)
_SEND = re.compile(r"\b(send|email|e-mail|notify)\b", re.I)
_READ = re.compile(r"\b(get|read|list|search|query|fetch|describe|review|record|propose|inventory)\b", re.I)
_ASSIGN = re.compile(
    r"(?i)\b(api[_-]?key|password|client[_-]?secret|accountkey|connection[_-]?string)\b"
    r"\s*[:=]\s*['\"]?([A-Za-z0-9+/=_.-]{8,})"
)
_PLACEHOLDER = re.compile(r"^(?:SET_|YOUR_|CHANGEME|example|placeholder|<)", re.I)
_ACCOUNT_KEY = re.compile(r"AccountKey=", re.I)
_BEARER_SK = re.compile(r"Bearer\s+sk-")
_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
_SPECIAL = re.compile(
    r"(health|diagnosis|disability|ethnic|religion|religious|sexual|sexlife|"
    r"tradeunion|genetic|biometric|political|nhsnumber)",
    re.I,
)
_EXCLUDED = re.compile(r"\b(not returned|do not return|excluded|minimised|minimized)\b", re.I)


def detect_kind(document: dict[str, Any], requested: str | None) -> str:
    if requested in {"openapi", "mcp", "copilot_studio", "foundry", "repo_tools"}:
        return requested
    if any(key in document for key in ("openapi", "swagger", "paths")):
        return "openapi"
    if "actions" in document and "tools" not in document:
        return "copilot_studio"
    tools = document.get("tools")
    if isinstance(tools, list) and tools and isinstance(tools[0], dict):
        sample = tools[0]
        if "inputSchema" in sample:
            return "mcp"
        if isinstance(sample.get("authentication"), dict):
            return "foundry"
        return "repo_tools"
    raise ValueError("The contract shape was not recognised.")


def normalise(document: dict[str, Any], kind: str | None = None) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ValueError("The contract must be a JSON object.")
    resolved = detect_kind(document, kind)
    if resolved == "openapi":
        operations = _openapi(document)
    elif resolved == "copilot_studio":
        operations = [_action(item, "copilot_studio") for item in _list(document, "actions")]
    elif resolved == "mcp":
        operations = [_mcp(item) for item in _list(document, "tools")]
    elif resolved == "foundry":
        operations = [_foundry(item) for item in _list(document, "tools")]
    else:
        operations = [_repo(item) for item in _list(document, "tools")]
    text = json.dumps(document, ensure_ascii=False, sort_keys=True)
    secrets = _secrets(text)
    for operation in operations:
        if secrets and not operation["auth"]["secret_labels"]:
            operation["auth"]["secret_labels"] = list(secrets)
    http = resolved in HTTP_KINDS or any(operation.get("http_method") for operation in operations)
    return {
        "kind": resolved,
        "http_contract": http,
        "operations": operations,
        "secret_labels": secrets,
        "reading_shape": resolved != "openapi",
    }


def _list(document: dict[str, Any], key: str) -> list[dict[str, Any]]:
    raw = document.get(key)
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"The contract needs a non-empty {key} list.")
    items = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError(f"Each entry in {key} must be an object.")
        items.append(item)
    return items


def _words(text: str) -> str:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text or "")
    return spaced.replace("_", " ").replace("-", " ")


def _effect(name: str, description: str, method: str | None, explicit: str | None, repo_default_read: bool) -> str:
    if explicit in {"read", "write", "delete", "send"}:
        return explicit
    blob_name = _words(name)
    blob = f"{blob_name} {_words(description)}"
    verb = (method or "").upper()
    if verb == "DELETE" or _DELETE.search(blob_name):
        return "delete"
    if verb in {"PUT", "PATCH"}:
        return "write"
    if _SEND.search(blob_name) or (verb == "POST" and _SEND.search(blob) and not _READ.search(blob_name)):
        return "send"
    if verb == "POST":
        if _READ.search(blob_name) or (_READ.search(description or "") and not _WRITE.search(blob_name)):
            return "read"
        return "write"
    if verb in {"GET", "HEAD", "OPTIONS"}:
        return "read"
    if _DELETE.search(blob_name):
        return "delete"
    if _SEND.search(blob_name):
        return "send"
    if _WRITE.search(blob_name):
        return "write"
    if _READ.search(blob_name) or _READ.search(description or ""):
        return "read"
    if repo_default_read:
        return "read"
    return "unknown"


def _bounded(schema: Any, depth: int = 0) -> tuple[bool, str]:
    if depth > 6:
        return False, "schema nested too deeply"
    if not isinstance(schema, dict):
        return False, "missing schema"
    if schema.get("enum"):
        return True, "enum"
    if schema.get("const") is not None:
        return True, "const"
    typ = schema.get("type")
    if typ == "boolean":
        return True, "boolean"
    if typ in {"integer", "number"}:
        has_min = "minimum" in schema or "exclusiveMinimum" in schema
        has_max = "maximum" in schema or "exclusiveMaximum" in schema
        if has_min and has_max:
            return True, "range"
        return False, "number without a minimum and a maximum"
    if typ == "array":
        if "maxItems" not in schema:
            return False, "array without maxItems"
        return _bounded(schema.get("items") or {}, depth + 1)
    if typ == "object" or "properties" in schema:
        if schema.get("additionalProperties") is True:
            return False, "additionalProperties is true"
        properties = schema.get("properties") or {}
        if not isinstance(properties, dict):
            return False, "properties is not an object"
        if not properties and schema.get("additionalProperties") is not False:
            return False, "object with no properties"
        for name, prop in properties.items():
            ok, reason = _bounded(prop if isinstance(prop, dict) else {}, depth + 1)
            if not ok:
                return False, f"{name}: {reason}"
        return True, "object"
    if schema.get("maxLength") or schema.get("pattern"):
        return True, "string bound"
    if schema.get("format") in BOUNDED_FORMATS:
        return True, "format"
    return False, "unbounded string"


def _schema_of(parameter: dict[str, Any]) -> dict[str, Any]:
    schema = parameter.get("schema")
    if isinstance(schema, dict):
        return schema
    lifted = {}
    for key in ("type", "maxLength", "minLength", "pattern", "enum", "format", "minimum", "maximum", "maxItems", "items"):
        if key in parameter:
            lifted[key] = parameter[key]
    return lifted


def _fields_from_schema(schema: Any, location: str, components: dict[str, Any], prefix: str = "") -> list[dict[str, Any]]:
    resolved = _resolve(schema, components)
    if not isinstance(resolved, dict):
        return [_field(prefix or "(body)", {}, location, True)]
    if resolved.get("type") == "object" or "properties" in resolved:
        properties = resolved.get("properties") if isinstance(resolved.get("properties"), dict) else {}
        required = set(resolved.get("required") or [])
        fields = []
        for name, prop in properties.items():
            full = f"{prefix}.{name}" if prefix else str(name)
            prop_resolved = _resolve(prop, components)
            if isinstance(prop_resolved, dict) and (
                prop_resolved.get("type") == "object" or "properties" in prop_resolved
            ):
                fields.extend(_fields_from_schema(prop_resolved, location, components, full))
            else:
                fields.append(_field(full, prop_resolved if isinstance(prop_resolved, dict) else {}, location, name in required))
        if resolved.get("additionalProperties") is True:
            fields.append(
                {
                    "name": f"{prefix}.*" if prefix else "*",
                    "location": location,
                    "required": False,
                    "bounded": False,
                    "reason": "additionalProperties is true",
                    "additional": True,
                    "special_category": False,
                    "excluded": False,
                }
            )
        return fields
    return [_field(prefix or "(body)", resolved, location, True)]


def _field(name: str, schema: dict[str, Any], location: str, required: bool) -> dict[str, Any]:
    ok, reason = _bounded(schema)
    compact = re.sub(r"[^a-z0-9]", "", _words(name).lower())
    special = bool(name) and bool(_SPECIAL.search(compact))
    description = str(schema.get("description") or "")
    excluded = schema.get("x-excluded") is True or schema.get("returned") is False or bool(_EXCLUDED.search(description))
    return {
        "name": name,
        "location": location,
        "required": required,
        "bounded": ok,
        "reason": reason,
        "additional": schema.get("additionalProperties") is True,
        "special_category": special,
        "excluded": excluded,
    }


def _resolve(schema: Any, components: dict[str, Any]) -> Any:
    if not isinstance(schema, dict):
        return schema
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/components/schemas/"):
        return schema
    name = ref.rsplit("/", 1)[-1]
    target = components.get(name)
    if isinstance(target, dict):
        return target
    return schema


def _parameter_fields(parameters: Any, components: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(parameters, list):
        return []
    fields = []
    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue
        location = str(parameter.get("in") or "query")
        if location == "body":
            location = "body"
        schema = _resolve(_schema_of(parameter), components)
        name = str(parameter.get("name") or "")
        if isinstance(schema, dict) and (schema.get("type") == "object" or "properties" in schema):
            fields.extend(_fields_from_schema(schema, "body" if location == "body" else location, components, name))
        else:
            fields.append(_field(name, schema if isinstance(schema, dict) else {}, location, parameter.get("required") is True or location == "path"))
    return fields


def _rate(node: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
    raw = node.get("x-rate-limit") or node.get("rateLimit") or node.get("rate_limit") or {}
    if not isinstance(raw, dict):
        raw = {}
    calls = raw.get("calls")
    renewal = raw.get("renewal_period_seconds", raw.get("renewal-period", raw.get("renewal_period")))
    policies = node.get("x-apim-policies") or node.get("apim_policies") or []
    if isinstance(policies, str):
        policies = [policies]
    named = any(str(item) in {"rate-limit", "rate-limit-by-key"} for item in policies)
    codes = {str(code) for code in responses}
    return {
        "calls": calls if isinstance(calls, int) else None,
        "renewal": renewal if isinstance(renewal, int) else None,
        "has_429": "429" in codes,
        "named_policy": named,
    }


def _approval(node: dict[str, Any], description: str) -> dict[str, bool]:
    structured = any(
        node.get(key) is True
        for key in (
            "humanApprovalRequired",
            "human_approval_required",
            "x-human-approval",
            "human_approval_to_run",
        )
    )
    text_gate = bool(
        re.search(r"\b(approves?|approval|must confirm|human gate)\b", description, re.I)
        and re.search(
            r"\b(security/api owner|api owner|security owner|agent owner|approver|human|officer|reviewer)\b",
            description,
            re.I,
        )
    )
    return {"structured": structured, "text": text_gate}


def _auth_from_flags(oauth: bool, managed: bool, api_key: bool, scopes: list[str]) -> dict[str, Any]:
    return {
        "oauth": oauth,
        "managed_identity": managed,
        "api_key": api_key,
        "scopes": scopes,
        "broad_scopes": [scope for scope in scopes if _broad(scope)],
        "secret_labels": [],
    }


def _broad(scope: str) -> bool:
    text = scope.strip()
    if text in {"*", "full_access", "admin"}:
        return True
    if ".All" in text or "ReadWrite" in text:
        return True
    return False


def _secrets(text: str) -> list[str]:
    labels: list[str] = []
    for match in _ASSIGN.finditer(text):
        value = match.group(2)
        if _PLACEHOLDER.match(value):
            continue
        label = "secret-shaped assignment"
        if label not in labels:
            labels.append(label)
    if _ACCOUNT_KEY.search(text):
        labels.append("account key marker")
    if _BEARER_SK.search(text):
        labels.append("bearer token marker")
    if _PRIVATE_KEY.search(text):
        labels.append("private key marker")
    return labels


def _base_operation(
    *,
    operation_id: str,
    description: str,
    effect: str,
    http_method: str | None,
    path: str | None,
    fields: list[dict[str, Any]],
    auth: dict[str, Any],
    approval: dict[str, bool],
    rate: dict[str, Any],
    error_codes: list[str],
    error_text: str,
    callable_by_agent: bool,
) -> dict[str, Any]:
    inputs = [field for field in fields if field["location"] in {"path", "query", "header", "cookie", "body"}]
    outputs = [field for field in fields if field["location"] == "response"]
    special = [field for field in fields if field["special_category"]]
    return {
        "operation_id": operation_id,
        "description": description,
        "effect": effect,
        "http_method": http_method,
        "path": path,
        "callable": callable_by_agent,
        "fields": fields,
        "inputs": inputs,
        "outputs": outputs,
        "special_category": special,
        "auth": auth,
        "approval": approval,
        "rate": rate,
        "error_codes": error_codes,
        "error_text": error_text,
        "wildcard_path": bool(path) and "*" in str(path),
    }


def _openapi(document: dict[str, Any]) -> list[dict[str, Any]]:
    paths = document.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise ValueError("The OpenAPI document needs a paths object.")
    components = {}
    raw_components = document.get("components") if isinstance(document.get("components"), dict) else {}
    schemas = raw_components.get("schemas") if isinstance(raw_components.get("schemas"), dict) else {}
    components = schemas
    schemes = raw_components.get("securitySchemes") if isinstance(raw_components.get("securitySchemes"), dict) else {}
    operations = []
    methods = {"get", "post", "put", "patch", "delete", "head", "options"}
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        path_parameters = item.get("parameters") if isinstance(item.get("parameters"), list) else []
        for method, operation in item.items():
            if method.lower() not in methods or not isinstance(operation, dict):
                continue
            description = str(operation.get("description") or operation.get("summary") or "")
            parameters = list(path_parameters)
            if isinstance(operation.get("parameters"), list):
                parameters.extend(operation["parameters"])
            fields = _parameter_fields(parameters, components)
            body = operation.get("requestBody") if isinstance(operation.get("requestBody"), dict) else {}
            content = body.get("content") if isinstance(body.get("content"), dict) else {}
            for media in content.values():
                if isinstance(media, dict):
                    fields.extend(_fields_from_schema(media.get("schema") or {}, "body", components))
            responses = operation.get("responses") if isinstance(operation.get("responses"), dict) else {}
            error_bits = []
            for code, response in responses.items():
                if isinstance(response, dict):
                    error_bits.append(str(response.get("description") or ""))
                    response_content = response.get("content") if isinstance(response.get("content"), dict) else {}
                    for media in response_content.values():
                        if isinstance(media, dict) and str(code).startswith("2"):
                            fields.extend(_fields_from_schema(media.get("schema") or {}, "response", components))
            auth = _openapi_auth(document, operation, schemes)
            operations.append(
                _base_operation(
                    operation_id=str(operation.get("operationId") or f"{method}_{path}"),
                    description=description,
                    effect=_effect(
                        str(operation.get("operationId") or ""),
                        description,
                        method,
                        operation.get("x-effect") if isinstance(operation.get("x-effect"), str) else None,
                        False,
                    ),
                    http_method=method.upper(),
                    path=str(path),
                    fields=fields,
                    auth=auth,
                    approval=_approval(operation, description),
                    rate=_rate(operation, responses),
                    error_codes=[str(code) for code in responses if str(code) != "200"],
                    error_text=" ".join(error_bits),
                    callable_by_agent=operation.get("x-callable-by-agent") is not False,
                )
            )
    if not operations:
        raise ValueError("The OpenAPI document has no operations.")
    return operations


def _openapi_auth(document: dict[str, Any], operation: dict[str, Any], schemes: dict[str, Any]) -> dict[str, Any]:
    if "security" in operation:
        security = operation.get("security")
    else:
        security = document.get("security")
    oauth = False
    api_key = False
    managed = False
    scopes: list[str] = []
    if isinstance(security, list):
        for requirement in security:
            if not isinstance(requirement, dict):
                continue
            for name, granted in requirement.items():
                scheme = schemes.get(name) if isinstance(schemes.get(name), dict) else {}
                kind = str(scheme.get("type") or "")
                if kind == "apiKey":
                    api_key = True
                elif kind in {"oauth2", "openIdConnect"}:
                    oauth = True
                    if isinstance(granted, list):
                        scopes.extend(str(item) for item in granted)
                description = str(scheme.get("description") or "")
                if re.search(r"managed identity", description, re.I):
                    managed = True
    if re.search(r"managed identity", json.dumps(operation.get("description") or ""), re.I):
        managed = True
    return _auth_from_flags(oauth, managed, api_key, scopes)


def _repo(tool: dict[str, Any]) -> dict[str, Any]:
    name = str(tool.get("name") or "tool")
    description = str(tool.get("description") or "")
    sends = tool.get("sends") is True
    writes = tool.get("writes") is True
    explicit = "send" if sends else "write" if writes else None
    effect = _effect(name, description, None, explicit, True)
    return _base_operation(
        operation_id=name,
        description=description,
        effect=effect,
        http_method=None,
        path=None,
        fields=[],
        auth=_auth_from_flags(False, False, False, []),
        approval=_approval(tool, description),
        rate=_rate(tool, {}),
        error_codes=[],
        error_text="",
        callable_by_agent=tool.get("callable_by_agent") is not False,
    )


def _mcp(tool: dict[str, Any]) -> dict[str, Any]:
    name = str(tool.get("name") or "tool")
    description = str(tool.get("description") or "")
    fields = _fields_from_schema(tool.get("inputSchema") or {}, "body", {})
    return _base_operation(
        operation_id=name,
        description=description,
        effect=_effect(name, description, None, None, False),
        http_method=None,
        path=None,
        fields=fields,
        auth=_auth_from_flags(False, False, False, []),
        approval=_approval(tool, description),
        rate=_rate(tool, {}),
        error_codes=[],
        error_text="",
        callable_by_agent=tool.get("callable_by_agent") is not False,
    )


def _foundry(tool: dict[str, Any]) -> dict[str, Any]:
    name = str(tool.get("name") or "tool")
    description = str(tool.get("description") or "")
    method = tool.get("method") if isinstance(tool.get("method"), str) else None
    fields = _fields_from_schema(tool.get("parameters") or {}, "body", {})
    authentication = tool.get("authentication") if isinstance(tool.get("authentication"), dict) else {}
    kind = str(authentication.get("type") or "").lower().replace("-", "").replace("_", "")
    scopes = [str(item) for item in authentication.get("scopes") or []]
    auth = _auth_from_flags(
        kind in {"oauth", "oauth2", "entra", "microsoftentra"},
        kind in {"managedidentity"},
        kind in {"apikey", "key"},
        scopes,
    )
    return _base_operation(
        operation_id=name,
        description=description,
        effect=_effect(name, description, method, None, False),
        http_method=method.upper() if method else None,
        path=str(tool["path"]) if tool.get("path") else None,
        fields=fields,
        auth=auth,
        approval=_approval(tool, description),
        rate=_rate(tool, tool.get("responses") if isinstance(tool.get("responses"), dict) else {}),
        error_codes=[str(code) for code in (tool.get("responses") or {})] if isinstance(tool.get("responses"), dict) else [],
        error_text="",
        callable_by_agent=tool.get("callable_by_agent") is not False,
    )


def _action(action: dict[str, Any], _kind: str) -> dict[str, Any]:
    name = str(action.get("name") or "action")
    description = str(action.get("description") or "")
    method = action.get("method") if isinstance(action.get("method"), str) else None
    fields = _parameter_fields(action.get("parameters") or [], {})
    connection = action.get("connection") if isinstance(action.get("connection"), dict) else {}
    connection_kind = str(connection.get("kind") or "").lower().replace("-", "").replace("_", "")
    scopes = [str(item) for item in connection.get("scopes") or []]
    auth = _auth_from_flags(
        connection_kind in {"oauth", "oauth2", "entra"},
        connection_kind in {"managedidentity"},
        connection_kind in {"apikey", "key"},
        scopes,
    )
    responses = action.get("responses") if isinstance(action.get("responses"), dict) else {}
    return _base_operation(
        operation_id=name,
        description=description,
        effect=_effect(name, description, method, None, False),
        http_method=method.upper() if method else None,
        path=str(action["path"]) if action.get("path") else None,
        fields=fields,
        auth=auth,
        approval=_approval(action, description),
        rate=_rate(action, responses),
        error_codes=[str(code) for code in responses],
        error_text=" ".join(str(item.get("description") or "") for item in responses.values() if isinstance(item, dict)),
        callable_by_agent=action.get("callable_by_agent") is not False,
    )
