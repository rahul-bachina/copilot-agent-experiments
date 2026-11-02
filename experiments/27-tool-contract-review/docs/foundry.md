# Microsoft Foundry and Azure API Management

The catalogue stack for G005 is Microsoft Foundry plus Azure API Management. This note is a path for a team that wants the findings JSON beside a later Foundry agent, and a policy sketch an API owner can take to API Management. It is not a deployed project. No Foundry resource is created by this repository. No API Management instance is called.

The reviewer in `src/review.py` remains the system of record. A model does not change a score, does not apply a diff, and does not publish a policy.

The Microsoft Foundry Agent Service overview was not opened for this experiment. Claims about prompt agents, hosted agents, preview features, and region lists are not repeated here. UK region availability is unverified.

Prompt Shields were not opened for this experiment. This reviewer does not call them. The local scan is the pattern list in `src/injection.py`.

## API Management, as opened on 2 November 2026

These pages were opened. The reviewer does not download them at run time.

- [API Management policy reference](https://learn.microsoft.com/en-us/azure/api-management/api-management-policies)
- [rate-limit policy](https://learn.microsoft.com/en-us/azure/api-management/rate-limit-policy)
- [authentication-managed-identity policy](https://learn.microsoft.com/en-us/azure/api-management/authentication-managed-identity-policy)
- [validate-parameters policy](https://learn.microsoft.com/en-us/azure/api-management/validate-parameters-policy)

What those pages said:

- `rate-limit` prevents usage spikes on a per subscription basis. When the call rate is exceeded, the caller receives HTTP 429. `calls` and `renewal-period` are required. `renewal-period` is in seconds and the maximum allowed value is 300. Policy expressions are not allowed for those attributes. The policy is only applied when an API is accessed using a subscription key. Rate limiting is never completely accurate, because of the distributed nature of the throttling architecture. The example on the page uses 20 calls per 90 seconds. That example is not a limit this reviewer recommends. The proposed XML uses `calls="SET_BY_API_OWNER"` and `renewal-period="SET_BY_API_OWNER"`.
- The policy index lists "Limit call rate by key" as not supported on the Consumption gateway. The element name for that policy was not on the page that was opened, so the proposed XML uses `rate-limit` only. "Limit call rate by subscription" and "Set usage quota by subscription" depend on the subscription key.
- `authentication-managed-identity` authenticates to a backend with the managed identity and sets a bearer token. On managed gateways, omitting `client-id` uses the system-assigned identity. The policy page says the customer is responsible for forwarding the token only to an intended backend. The policy index lists "Authenticate with managed identity" as not supported on the workspace gateway. The policy page's usage line lists classic, v2, consumption, and self-hosted. Those two statements are both what the pages said. This note does not reconcile them. The proposed XML includes the element only when authentication is not a pass, and it sets `resource="SET_RESOURCE_APPLICATION_ID"`.
- `validate-parameters` validates header, query, or path parameters against the API schema. Actions include ignore, prevent, and detect. A `prevent` action on an inbound policy returns HTTP 400. The maximum schema size for the validation policy is 4 MB. Validation can reduce throughput and load tests are recommended. This reviewer does not run a load test. The proposed XML includes the element only when input validation is not a pass.
- `rate-limit` does not, by itself, authenticate the caller.

The proposed XML is a sketch. `policy_published` stays false. It is not valid until the security/API owner replaces every `SET_` placeholder.

Copilot Studio, MCP, and Foundry tool blocks in a bundle are reading shapes for this reviewer. They are not claimed to be an export from a live connector, a live MCP server, or a Foundry tool blade. That export format was not opened. An OpenAPI document is read as a subset of OpenAPI: paths, methods, parameters, request and response schemas, and security.

## What a later model may do

- Turn the JSON into a short brief for the security/API owner, using only fields that are in the JSON.
- Repeat a finding, the cited operation, and the contract note already on that finding.
- Point at `prompt_injection` and `do_not_rely` in the first paragraph.
- Show the policy XML already on `proposed_diff` without filling a placeholder.

## What the model must not do

- Invent a Microsoft Learn URL or a source id.
- Browse the web to update the catalogue.
- Change a check result or the percent.
- Apply the diff, publish the policy, or set `contract_approved`, `diff_applied`, or `policy_published`.
- Choose a number of calls or a renewal period.
- Recommend autonomy A3.
- Mark the manifest approved, or enable a high-risk action.
- Deploy, send, or write a production record.
- Quote a price.
- Repeat a secret-shaped value the checker found.

## Suggested shape

One orchestration, not a free chat over the open internet.

1. The security/API owner supplies the bundle and the as-of date.
2. The orchestration calls `src/review.py` and passes the JSON to the model.
3. The model writes the brief. It does not call a second tool and it does not call API Management.
4. The security/API owner reads the brief beside the JSON. They approve the contract, or they do not, outside this path. They approve a policy change before anyone publishes it.

There is no Foundry project file in this folder and no API Management service configuration. Creating either is a later decision for the organisation.
