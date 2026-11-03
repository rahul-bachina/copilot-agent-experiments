# Security and permissions

Groundedness Evaluation Agent, Experiment 29. Catalogue ID G007.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA and not as a penetration test.

## Purpose

The agent reads one synthetic Q&A bundle and returns a groundedness report. Each claim gets one verdict against the passages the agent under test was shown. Autonomy is A0. It has no action to take on the draft. An evaluation owner approves the thresholds and records any pass or fail release. A governance owner approves any manifest skeleton before anyone relies on it.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Approve a threshold. `threshold_approved_by_evaluation_owner` stays false.
- Record a pass or a fail release. `release_decision` stays null. `pass_fail_released` stays false.
- Call the Microsoft Foundry groundedness evaluator or Groundedness Pro. `foundry_evaluator_called` stays false.
- Recommend autonomy A3. The catalogue levels are A0, A1, and A2. This checker stays at A0.
- Mark a permissions manifest approved.
- Write a production record or send a message.
- Score a bundle that is not marked synthetic.
- Quote a price or look up a licence in an admin centre.
- Refresh citations from the web. URLs come from `src/sources.py`.

There is no tool whose side effect is any of the above. `schema/tools.json` marks `approve_thresholds`, `record_release`, and `call_foundry_evaluator` as not callable. Tests in `tests/test_prohibited.py` and `tests/test_injection.py` check that answer text does not become an approval or a release.

## Data

**Read, in this starter.** The synthetic bundle for that run. The as-of date and the pin window. The static source list. Experiment 03, called locally only when the bundle asks for a skeleton.

**Not read.** An admin centre, a billing account, a mailbox, a Teams chat, a production agent, Copilot Studio as a control plane, Microsoft Foundry as a control plane, and Power Automate as a control plane.

The samples in this repository are synthetic. Northfen Borough Council, Fenwick Mutual, and Rivertrust NHS Trust are fictional. The Rivertrust note is a corporate leave sentence and is not a clinical record. The manifest does not assert a UK GDPR lawful basis. The organisation's data protection officer confirms an Article 6 basis before any live processing, and an Article 9 condition if special-category data is in scope. Live data is outside this starter.

The Python starter does not persist the bundle. The report keeps claim text, because that is what was scored, and passage titles and review dates. It does not copy the passage body into a second store.

## Prompt injection and stale data

The checker is itself a reader of untrusted answer text. The scanner records a line that tells the checker to ignore instructions, approve the thresholds, mark a release, set groundedness clearance, mark every claim supported, or take a new persona. A sentence that already refuses the action, including "do not" and "must not", is not treated as an injection. Payload keys that try to set `threshold_approved_by_evaluation_owner`, `release_decision`, `pass_fail_released`, `groundedness_clearance`, or a verdict are stripped and are not echoed. `followed` stays false.

The stale-data test compares `last_verified` (3 November 2026 for the pages this experiment opened) with the as-of date. Older than the threshold, default 90 days, is stale. Passage review dates use the draft window in the bundle, default 180 days, which is not approved. The catalogue-boundary row is not a Microsoft page and is not stale-tested. The checker does not download the page and does not rewrite the review date. When a pin or a passage is stale, `do_not_rely` is true. The draft is still produced. It is still not a release. `reopened_for_this_experiment` stays as stored.

The residual risk is a misleading draft if a model is later wrapped around the JSON, or if a reader treats `draft_bar_met` as a release. The evaluation owner is the control. There is no autonomous action behind a bad draft. Residual risk R3 in the manifest is Medium for the word match.

## Human approval

Autonomy A0 means this checker cannot release an agent even after a person agrees. The person still has to record the decision outside the tool.

| Decision | Who |
|---|---|
| Approve the draft thresholds | Evaluation owner |
| Record a pass or fail release | Evaluation owner |
| Re-open a pinned page before relying on a citation | Evaluation owner |
| Rely on a manifest skeleton | Governance owner |
| Call the Microsoft Foundry groundedness evaluator | Evaluation owner, and only outside this starter |
| Confirm an Article 6 basis, and an Article 9 condition if special-category data was recorded | Data protection officer |
| Deploy, publish, or turn a flow on | Outside this agent |

Producing the draft and printing the sources table do not need a separate approval.

The skeleton, when one is requested, asks for A0 unless the bundle names A1 or A2. A request for autonomy A3 is refused. It is never the recommendation. `a3_recommended` stays false. Assumption id A3 in the manifest is an assumption about disabled high-risk actions. It is not autonomy level A3.

## Controls a tenant would discuss

This starter configures none of them. A row says "opened" only when the body was opened on 3 November 2026 for this experiment. Otherwise the control is unverified. Do not treat an unverified row as a product capability.

| Control | In this starter | Note |
|---|---|---|
| Microsoft Foundry groundedness evaluator | Not called | Opened on 3 November 2026. LLM-judge. Needs `deployment_name`. Scores from 1 to 5. Default pass threshold 3 on that scale. This checker does not apply that number. |
| Microsoft Foundry Groundedness Pro | Not called | Marked preview on the page opened on 3 November 2026. Uses Azure AI Content Safety. Returns a boolean. No UK region was named. UK region availability is unverified. |
| Microsoft Foundry prompt shields | Not called | Unverified. That page was not opened for this experiment. |
| Microsoft Entra identity for Foundry Agent Service | Not configured | Unverified. That page was not opened for this experiment. |
| Microsoft Entra Agent ID | Not configured | Unverified. Not opened for this experiment. |
| Conditional Access | Not configured | Unverified. Not opened for this experiment. |
| Power Platform data loss prevention | Not configured | Unverified. Not opened for this experiment. A later connector that can send or write would need a policy the organisation writes. |
| Key Vault | Not provisioned | Unverified. Not opened. The checker has no secret. |
| Microsoft Purview | Not configured | Unverified. Not opened. Classification of any later report is the organisation's. |
| Application Insights | Not configured | Unverified. Not opened. This starter writes no log. |

## Logging

This starter writes no log. Before a deployment, log who ran it, when, the bundle id, the as-of date, the claim count, the verdict counts, and whether `do_not_rely` was true. Do not log passage bodies into an unreviewed store.
