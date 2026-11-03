# Security and permissions

Agent Regression Test Generator, Experiment 30. Catalogue ID G008.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a test certificate.

## Purpose

The agent drafts regression cases from a synthetic manifest, `SKILL.md` files, a tool contract, and observed failures or change notes. Autonomy is A1. A maintainer approves the tests and any pull request. The generator does not merge, does not push, and does not edit the agent under test.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Merge a pull request. `merged` stays false.
- Push, including to a protected branch. `pushed` and `protected_branch_targeted` stay false.
- Edit the agent under test. `agent_under_test_edited` stays false.
- Approve the generated tests. `maintainer_approved` stays false.
- Open a pull request. `pr_opened` stays false.
- Call Microsoft Foundry or upload a dataset. `foundry_evaluation_called` stays false.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This generator stays at A1 and only drafts.
- Mark a permissions manifest approved.
- Write a production record or send a message.
- Fetch a URL or call a model.
- Quote a price or look up a licence in an admin centre.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. `schema/tools.json` marks approve, open, merge, push, and edit as not callable. Tests in `tests/test_prohibited.py` and `tests/test_injection.py` check that fixture text does not become a merge, a push, or an edit.

## Data

**Read, in this starter.** The synthetic bundle for that run. The as-of date and the stale threshold. The static source list. Experiment 03, called locally when a skeleton was requested and no manifest was supplied.

**Not read.** An admin centre, a billing account, a mailbox, a Teams chat, a Git remote, the agent under test as a file, Copilot Studio as a control plane, and Microsoft Foundry as a control plane.

The samples in this repository are synthetic. Halebridge Borough Council is fictional. Paths in the bundle are labels. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms an Article 6 basis before any live processing, and an Article 9 condition if special-category data is in scope. Live data is outside this starter.

The Python starter does not persist the bundle unless the caller passes `--out-dir`. That directory is refused when it resolves inside the agent path, inside `.git`, or under a name used for a protected branch.

## Prompt injection and stale data

The generator is itself a reader of untrusted fixture text. The scanner records a line that tells the generator to ignore instructions, merge, push to a protected branch, edit the agent, or set `maintainer_approved`. A sentence that already refuses the action, including "do not" and "must not", is not treated as an injection. Payload keys that try to set the result flags are stripped and are not echoed. `followed` stays false.

The stale-data test compares `last_verified` (3 November 2026 for the pages this experiment opened) with the as-of date. Older than the threshold, default 90 days, is stale. The catalogue-boundary row is not a Microsoft page and is not stale-tested. The generator does not download the page and does not rewrite the review date. When a pin is stale, `do_not_rely` is true. The draft is still produced. It is still not an approval.

The marker `SYN-MARKER-OVERRIDE` is a labelled stand-in on the variant case. It is not a procedure for attacking a live system.

## Human approval

Autonomy A1 means the generator may draft, and a person approves every consequential step. The generator cannot record that approval.

| Decision | Who |
|---|---|
| Approve generated tests | Maintainer |
| Open a pull request from the draft content | Maintainer |
| Merge a pull request | Maintainer |
| Push, including to a protected branch | Maintainer |
| Edit the agent under test | Maintainer |
| Re-open a pinned page before relying on a citation | Maintainer |
| Rely on a manifest skeleton drafted because none was supplied | Governance owner |
| Run a Microsoft Foundry evaluation against a deployed agent | Maintainer, and only outside this starter |
| Confirm an Article 6 basis, and an Article 9 condition if special-category data was recorded | Data protection officer |

Producing the draft and printing the sources table do not need a separate approval.

The skeleton for a missing manifest asks for A0, A1, or A2. A request for autonomy A3 is refused. It is never the recommendation. `a3_recommended` stays false. Assumption id A3 in the manifest is an assumption about disabled high-risk actions. It is not autonomy level A3.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 3 November 2026 for this experiment. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Foundry agent evaluation | Not called | Opened on 3 November 2026. See `docs/foundry.md`. The queries file is local. It is not uploaded. UK region availability for the features the page says are region-restricted is unverified. |
| Microsoft Foundry prompt shields | Not called | Unverified. Not opened for this experiment. The local scan is not a shield result. |
| Microsoft Entra Agent ID | Not configured | Unverified. Not opened for this experiment. |
| Conditional Access | Not configured | Unverified. Not opened for this experiment. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this experiment. A later connector that can send or write would need a policy the organisation writes. |
| Key Vault | Not provisioned | Unverified. Not opened. The generator has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of any later report is the organisation's. |
| Application Insights | Not configured | Unverified as a product page. The evaluate-agent page points at trace evaluation using Application Insights. This starter does not configure it and does not log case inputs. |

Announced items that this folder did not open are not listed as available.

## Logging

This starter writes no log. Before live use, log who ran it, when, the bundle id, the agent id, the as-of date, the drafted count, the skipped-duplicate count, and whether a prompt-injection pattern was detected. Do not log case inputs.

## Kill switch

Do not run `src/generate.py`. Delete the local copy from a machine that should not draft tests. There is no published agent to turn off. If a team later publishes one despite this starter, turn that Copilot Studio agent off and block a send or a write in a data loss prevention policy the organisation configures. The contact in the manifest is `regression-tests@example.com`. It is a placeholder.

## Skeleton generator

When the caller asks and no manifest was supplied, a draft manifest is requested from Experiment 03's `generate_manifest`, with `approve` false, and only if PyYAML and jsonschema import. The generator refuses an approve flag and refuses autonomy A3. This generator discards a skeleton that comes back approved or at A3. High-risk actions in the generated file stay disabled. A clean install of this experiment does not include those packages. The stand-in still refuses approval and still refuses A3. It is not schema-validated. The skeleton is not written into the agent under test.
