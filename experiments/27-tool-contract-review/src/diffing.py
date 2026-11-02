"""Proposed contract notes and an API Management policy sketch.

Nothing here is applied or published. Placeholders are not call volumes.
The 20-calls example on the rate-limit page is not copied.
"""

from __future__ import annotations

from typing import Any


def propose(checks: list[dict[str, Any]]) -> dict[str, Any]:
    notes = [f"{check['id']}: {check['rewrite']}" for check in checks if check["result"] != "pass"]
    policy, policy_notes = _policy(checks)
    return {
        "applied": False,
        "published": False,
        "contract_modified": False,
        "format": "proposed notes and policy XML",
        "contract_notes": notes,
        "policy_xml": policy,
        "policy_notes": policy_notes,
    }


def _policy(checks: list[dict[str, Any]]) -> tuple[str | None, list[str]]:
    by_id = {check["id"]: check for check in checks}
    elements: list[str] = []
    notes: list[str] = []
    if by_id["C4"]["result"] != "pass":
        elements.append(
            '    <validate-parameters specified-parameter-action="prevent" '
            'unspecified-parameter-action="prevent" errors-variable-name="requestParametersValidation" />'
        )
        notes.append(
            "validate-parameters was opened on 2 November 2026. prevent on an inbound "
            "policy returns HTTP 400. The page says validation can reduce throughput. "
            "This sketch is not a load test and it is not published."
        )
    if by_id["C5"]["result"] != "pass":
        elements.append('    <authentication-managed-identity resource="SET_RESOURCE_APPLICATION_ID" />')
        notes.append(
            "authentication-managed-identity was opened on 2 November 2026. resource is "
            "the application ID of the backend API in Microsoft Entra ID. The customer "
            "forwards the token only to an intended backend. Removing a key from the "
            "contract is a separate edit. The policy index lists this policy as not "
            "supported on the workspace gateway."
        )
    if by_id["C7"]["result"] != "pass":
        elements.append('    <rate-limit calls="SET_BY_API_OWNER" renewal-period="SET_BY_API_OWNER" />')
        notes.append(
            "rate-limit was opened on 2 November 2026. calls and renewal-period are "
            "required, renewal-period is seconds, and the maximum is 300. Policy "
            "expressions are not allowed for those attributes. The policy applies when "
            "the API is accessed with a subscription key. It does not authenticate the "
            "caller. The security/API owner sets both numbers. The page's example of "
            "20 calls per 90 seconds is not copied."
        )
    if not elements:
        return None, []
    body = "\n".join(elements)
    xml = (
        "<policies>\n"
        "  <inbound>\n"
        "    <base />\n"
        f"{body}\n"
        "  </inbound>\n"
        "  <outbound>\n"
        "    <base />\n"
        "  </outbound>\n"
        "</policies>\n"
    )
    return xml, notes
