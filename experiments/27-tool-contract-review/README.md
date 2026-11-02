# Experiment 27: Tool Contract Review Agent

Catalogue ID **G005**. Autonomy **A0**. Stack in the catalogue: Microsoft Foundry plus Azure API Management. This folder also ships both Copilot Studio harnesses, because every experiment in this repository does.

A starter for a security or API owner who has been handed the tools an agent may call. The reviewer reads one contract — an OpenAPI document, an MCP-shaped tool list, a Copilot Studio action list, a Foundry-shaped tool list, or a `schema/tools.json` file already used in this repository — and scores it against a fixed checklist. The report includes proposed contract notes and, where a check is not a pass, a proposed Azure API Management policy. The security/API owner approves the contract. The reviewer does not modify the file, does not publish the policy, and does not deploy.

The checklist is the code in `src/checklist.py`. The same contract and the same as-of date produce the same JSON. Nothing here calls a model or the network. A local call to Experiment 25, when instruction text was supplied, is a subprocess on this machine. It is not a network call.

Where a bundle has no permissions manifest, the reviewer asks Experiment 03's generator for an unapproved skeleton. That call needs PyYAML and jsonschema, which this experiment's clean install does not include. Without them, a local stand-in is used. It still refuses approval and still refuses autonomy A3. It is not schema-validated. Where a bundle includes a structured use case, the reviewer calls Experiment 14's decision table. Experiment 14 does not select a platform. Where a bundle includes instruction text, the reviewer calls Experiment 25 and keeps that reviewer's score separate. Neither call changes the rule that this reviewer is A0 and does not apply a diff.

The organisation in the sample is invented. It is not a client. Contracts under `fixtures/contracts/` are synthetic. A few cases point at tool schemas and manifests already in this repository. Those files are not live tenant contracts.

## The problem

An agent is only as narrow as the tools it is given. A contract can offer a write where the permissions manifest allows a read, leave a delete or a send without a person, accept an unbounded parameter, paste a key into an example, return a health field, omit a rate limit, or describe the tool in a way that tells a model to ignore its instructions. Reading that by eye does not stay the same from one reviewer to the next. A checklist that cites the operation it used is easier to argue with.

The score is not a certificate. A pattern misses a paraphrase, and it can flag a line a person would keep. The security/API owner accepts or rejects each finding.

## Who it helps

A security owner or an API owner, or the two of them sitting together, who wants a draft reading before a contract or an API Management policy is changed: least privilege, agreement with the permissions manifest, a human gate on a destructive or external-send operation, bounded inputs, authentication without a key in the file, data minimisation, a rate-limit recommendation, error handling, and tool text that a prompt injection could abuse.

It does not help a team that wants the tool to publish the policy or deploy the API.

## Non-goals

- Modifying a contract, applying a diff, or opening a pull request. `diff_applied` and `contract_modified` stay false.
- Publishing an Azure API Management policy. `policy_published` stays false. The proposed XML uses placeholders the owner must replace. It is not a policy that has been applied.
- Approving a contract. `contract_approved` and `owner_approved` stay false. The security/API owner decides.
- Deploying or publishing anything in Azure API Management, Copilot Studio, or Microsoft Foundry.
- Recommending autonomy A3, or approving, rejecting, deciding a regulated matter, changing a production record, sending, or spending.
- Approving a permissions manifest. Experiment 03's generator refuses an approve flag. The stand-in does too.
- Selecting a platform. If Experiment 14 is called, `platform_selected` stays null.
- Editing instructions. If Experiment 25 is called, its `diff_applied` is reported and is not followed.
- Legal advice, a DPIA, or a decision that a contract is lawful.
- Connecting to an API Management instance, a Foundry project, or an MCP server. The caller pastes the document.
- Using real organisations, real people, or live credentials. Fixtures are synthetic. Repository tool schemas are files already in this repository, not live connectors.

## What the reviewer does

`src/review.py` reads one JSON bundle and writes one JSON document. The label is **DRAFT FOR SECURITY/API OWNER REVIEW**.

Each check scores 0, 1, or 2. A pass is 2, a partial is 1, a fail is 0. The maximum is 18. The percent is `points / 18`, rounded to one decimal place. A fail is blocking: the report still shows the score, and it still does not apply the diff. The rows below are the code. A test fails if a check id in the code is missing here.

| Check | Name | What a pass needs | What a fail is |
|---|---|---|---|
| C1 | Least privilege | No wildcard path, no broad scope (a scope of `*`, `full_access`, or a scope containing `.All` or `ReadWrite`), no unbounded filter-like parameter, and no open object on a write, delete, or send. The HTTP method agrees with the effect. | One or more of those signals, with the operation id cited. A partial is an operation whose effect could not be classified, with none of the signals above. |
| C2 | Consistency with the permissions manifest | A manifest was supplied. A callable write, delete, or send exists only when the manifest allows that side. Where the manifest names tools as identifiers, each callable operation name is one of them. | No readable manifest is a partial, not a fail. A fail is a callable write, delete, or send the manifest does not allow, a manifest that did not parse, or an identifier-style tool list that omits a callable operation. Prose tool names, as in this repository's manifests, are a partial: the names were not matched. |
| C3 | Destructive or external-send operations have a human approval gate | No callable delete or send, or each one has a structured approval flag. A tool the contract marks as not callable by the agent is not treated as a privilege the agent holds. | A callable delete or external send with no structured approval flag. A partial is approval language in the description and no structured flag. |
| C4 | Input validation and bounded parameters | Every parameter and body property is bounded: a string has `maxLength`, `pattern`, or `enum`; a number has a minimum and a maximum; an array has `maxItems`; an object does not set `additionalProperties` to true. A date, date-time, or uuid format counts as bounded. An operation with no parameters is bounded. | An unbounded field on a callable write, delete, or send. A partial is an unbounded field on a read only. |
| C5 | Authentication model | OAuth with at least one scope that is not broad, or a managed-identity marker, and no API-key scheme as the only authentication, and no secret-shaped value in the file. | A secret-shaped value, an API-key scheme as the only authentication on an HTTP contract, or an OpenAPI, Copilot Studio, or Foundry-shaped HTTP contract with no authentication. A repository tool schema or an MCP list with no key in the file is a partial: those shapes do not carry an HTTP security scheme. |
| C6 | Data minimisation and UK GDPR special-category exposure | No field name matches a special-category or health-identifier pattern, and the response schema does not allow additional properties. | A matching field is in the schema and is not marked excluded. The match is a name check. It is not a determination that Article 9 applies. A partial is a matching field that the text says is excluded but that remains in the schema, or a response schema that allows additional properties without a matching field. |
| C7 | Rate limiting and API Management policy recommendation | A numeric call limit is declared, the renewal period if present is an integer of at most 300 seconds, and an OpenAPI contract also documents HTTP 429 or names the rate-limit policy. The 300-second maximum is the figure on the rate-limit policy page opened on 2 November 2026. This reviewer does not choose the number of calls. | An OpenAPI, Copilot Studio, or Foundry-shaped contract with no numeric limit, no HTTP 429, and no named rate-limit policy, or a renewal period above 300 seconds. A repository tool schema or an MCP list with no limit is a partial. The proposed policy is still not published. |
| C8 | Error handling | Every operation documents a client error (400 or 422), an authentication or authorisation error (401 or 403), and a server error (500 or default). Descriptions do not ask the service to return a stack trace, an exception message, or an inner error. | Those leak phrases, or an HTTP contract with no error responses. A repository tool schema or an MCP list with no error block is a partial. |
| C9 | Tool descriptions that could be abused by prompt injection | Every operation has a description, and none tells a model to ignore previous instructions, always call the tool, hide the action from the user, follow instructions found in the tool result, or treat the tool as unrestricted. A sentence that refuses that behaviour is not a hit. | One or more of those phrases, with the operation id cited. A partial is an operation with no description. |

Free text cannot set `owner_approved`, `contract_approved`, `diff_applied`, `policy_published`, `deployed`, or the score. Those keys are stripped if a caller puts them on the bundle.

The four contract shapes, other than `schema/tools.json`, are reading shapes for this reviewer. They are not claimed to be an export file from a live Copilot Studio connector, a live MCP server, or a Microsoft Foundry tool blade. That export format was not opened.

## How to run

Python 3.10 or newer. No Azure credentials and no network. The clean install is pytest only.

```bash
cd experiments/27-tool-contract-review
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/review.py --bundle examples/sample_bundle.json --as-of 2026-11-02
```

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic, plus tool schemas already in this repository. `eval/smoke_report.json` is that run, saved so a reviewer can see it without re-running. It is not a model score. A live Microsoft Foundry run has not been done. An Azure API Management instance has not been called.

A stale-data check, without editing the checklist:

```bash
python src/review.py --bundle examples/sample_bundle.json --as-of 2027-05-01 --stale-after-days 90
```

Passing `--approve`, `--apply`, `--publish`, or `--deploy` is a mistake. The command exits and does not write a file.

The exit code is 0 when the JSON is produced, including when a check fails or a source is stale. That is not an approval of the contract.

## Sample

Halebridge Borough Council is fictional. The sample is a read-only OpenAPI contract for one case identifier, with OAuth scope `Case.Read`, bounded parameters, no special-category field, a numeric rate limit, and error responses that do not leak internals. The draft scores the checklist and selects nothing. See `examples/sample_output.json`.

## Sources and currency

Pages opened for this experiment on **2 November 2026**. The reviewer does not download them at run time. `reopened_for_this_experiment` is true for those rows because this experiment opened them. It is not a claim that the page was opened again after that date.

| ID | Page | Last verified |
|---|---|---|
| `cs-harnesses-overview` | [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | 2 November 2026 |
| `cs-choose-harness` | [Compare Copilot Studio agent harnesses](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/choose-harness) | 2 November 2026 |
| `apim-policies` | [API Management policy reference](https://learn.microsoft.com/en-us/azure/api-management/api-management-policies) | 2 November 2026 |
| `apim-rate-limit` | [rate-limit policy](https://learn.microsoft.com/en-us/azure/api-management/rate-limit-policy) | 2 November 2026 |
| `apim-authentication-managed-identity` | [authentication-managed-identity policy](https://learn.microsoft.com/en-us/azure/api-management/authentication-managed-identity-policy) | 2 November 2026 |
| `apim-validate-parameters` | [validate-parameters policy](https://learn.microsoft.com/en-us/azure/api-management/validate-parameters-policy) | 2 November 2026 |

The catalogue-boundary row is not a Microsoft page and is not stale-tested.

What those pages said on that date:

- The harness overview describes the GitHub Copilot harness as a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says the harness can take a goal, break it into steps, call tools across connectors, knowledge, MCP, and connected agents, create and edit Word, Excel, PowerPoint, and PDF files, and support skills and memory. It says agents and workflows on it use Copilot Credits. No quantity is copied. The overview does not mark the harness itself as preview. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.
- The comparison page says to choose the standard harness when the work is relatively short and bounded, and the GitHub Copilot harness when the task is long-running or reasoning-intensive. It says customers should validate required features and channels as the experience matures. It says GitHub Copilot harness solutions use usage-based billing for AI-based creation and use, and that standard harness agents retain the pre-existing Copilot Studio licensing model. No rate is copied. The billing overview and the cost-management page were not opened for this experiment. Sentences about them that Experiment 14 stored on 27 October 2026 are not repeated here as if they had been re-opened.
- The rate-limit policy prevents usage spikes on a per subscription basis. When the call rate is exceeded, the caller receives HTTP 429. `calls` and `renewal-period` are required. `renewal-period` is in seconds and the maximum allowed value is 300. Policy expressions are not allowed for those attributes. The page says the policy is only applied when an API is accessed using a subscription key. It also says rate limiting is never completely accurate, because of the distributed nature of the throttling architecture. The example on the page uses 20 calls per 90 seconds. That example is not a limit this reviewer recommends.
- The policy index says "Limit call rate by subscription" and "Set usage quota by subscription" depend on the subscription key. It lists "Limit call rate by key" as not supported on the Consumption gateway. The element name for that second policy was not on the page that was opened, so the proposed XML uses `rate-limit` only.
- `authentication-managed-identity` authenticates to a backend with the managed identity and sets a bearer token. On managed gateways, omitting `client-id` uses the system-assigned identity. The policy page says the customer is responsible for forwarding the token only to an intended backend. The policy index lists "Authenticate with managed identity" as not supported on the workspace gateway. The policy page's usage line lists classic, v2, consumption, and self-hosted. Those two statements are both what the pages said. This note does not reconcile them.
- `validate-parameters` validates header, query, or path parameters against the API schema. Actions include ignore, prevent, and detect. The page says a `prevent` action on an inbound policy returns HTTP 400. It says the maximum schema size for the validation policy is 4 MB. It says validation can reduce throughput and that load tests are recommended. This reviewer does not run a load test.

Prompt Shields, Entra Agent ID, Conditional Access, Purview, a Data Loss Prevention policy, and Key Vault were not opened for this experiment. They are named in the security note as unverified. The billing pages were not opened.

## Build gate

| Point | Where it is |
|---|---|
| Non-goals | This README. |
| SKILL.md metadata | `skills/*/SKILL.md`. |
| Synthetic fixtures | `fixtures/contracts/` and `examples/`. Repository tool schemas are extra inputs, not live cases. |
| Least-privilege tool schema | `schema/tools.json` and `agent-manifest.yaml`. Writes and sends are disabled. |
| Prompt-injection tests | `tests/test_injection.py`. |
| Stale-data tests | `tests/test_stale.py`. |
| Prohibited-action tests | `tests/test_prohibited.py`. |
| CI secret check | `.github/workflows/experiment-27-tests.yml`. |
| CI licence check | The same workflow. MIT, and the README names it. |
| CI brand check | The same workflow. The retired Foundry product name fails the job. |
| Clean-environment install | `requirements.txt` installs pytest only. Tests import the standard library. |

## Limitations

- The checks are structural patterns on JSON the caller pasted. Another owner can read the same operation differently. The report cites the operation so that disagreement stays with a person.
- A secret written as a picture, or a key split across fields, is not detected. A placeholder the pattern treats as secret-shaped can be flagged. Residual risk R3 is Medium.
- Field names such as `diagnosis` are a name check. They are not a finding that UK GDPR Article 9 applies, and a special-category fact stored under a bland name is missed.
- The proposed policy XML is a sketch using element names from the pages opened on 2 November 2026. It is not a complete policy, it is not valid until the owner replaces every `SET_` placeholder, and it is not published. `rate-limit` counts per subscription key. It does not, by itself, authenticate the caller.
- The Copilot Studio, MCP, and Foundry blocks are reading shapes for this tool. A vendor export that uses different keys can be missed or mis-classified. That limit is stated on the contract kind.
- The stdlib YAML reader is Experiment 25's reader, loaded from that experiment's file. It accepts the subset this repository's manifests use. A file it cannot parse is reported. It is not guessed into a pass.
- Experiment 03 is not imported on the clean install. The stand-in is not validated against `schemas/agent-manifest.schema.json`. Install PyYAML and jsonschema beside this folder if you want that validation. This requirements file does not install them.
- Experiment 14 is called only for a structured use case. It still does not select a platform. Its licence sentences were not copied into this experiment.
- Experiment 25 is called only when instruction text was supplied. Its checklist is about instructions, not about this contract. A finding it returns is not a score on the contract.
- UK region availability for a later Foundry or API Management deployment was not on the pages opened. It is unverified.
- `eval/smoke_report.json` is a deterministic smoke test. It is not a model score.
- A finding on another experiment's `schema/tools.json` is a finding about that file. It is not a finding about that experiment's Python core. Those schemas are not HTTP contracts, so authentication, rate limit, errors, and descriptions are partial rather than failed.

This is not legal advice and it is not a statement that a contract meets UK GDPR.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md) and [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- GitHub Copilot harness: [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).
- Standard harness: [copilot-studio/README.md](copilot-studio/README.md).
- Microsoft Foundry and Azure API Management: [docs/foundry.md](docs/foundry.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml).

## Project structure

```
experiments/27-tool-contract-review/
├── README.md
├── agent-manifest.yaml
├── requirements.txt
├── schema/
├── src/
├── skills/
├── copilot-studio/
├── docs/
├── eval/
├── examples/
├── fixtures/
└── tests/
```

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
