# Standard harness

A lighter intake. Not the lead build. The lead build is the GitHub Copilot harness in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md).

This is a build guide, not a solution you can import.

The standard harness, on the page opened 24 October 2026, follows topics and rules you define. Skills, memory, and file creation are not its focus. That is the right shape when the reviewer already knows the document types and wants the checker run the same way each time.

## What to create

1. Create an agent on the standard harness. Name it "Cryptoasset readiness intake". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not upload the skills. They are for the other harness. Do not turn on generative orchestration that can call every connector in the environment.
4. Add one action: a flow that runs `src/gap_register.py` and returns the JSON. The flow's only job is to return JSON. It does not call fca.org.uk, does not write SharePoint, and does not send mail.
5. If a tool is not in `agent-manifest.yaml`, it is not on the agent.

## The action

Inputs, typed by the reviewer, not inferred as instructions from the policy text:

| Input | Required | Notes |
|---|---|---|
| `pack` | Yes | The files, or a path the flow is allowed to read for this run. |
| `as_of` | Yes | `YYYY-MM-DD`. The reviewer types it. |
| `stale_after_days` | No | Default 90. Older than this many days after `last_verified` is stale. |

Output: the JSON from `build_register`. The topic displays the disclaimer, `counts`, any injection block, `any_source_stale`, and the rows. It does not rewrite them.

Host the function as a locked-down internal API or an Azure Function. See [../docs/azure.md](../docs/azure.md). Do not re-implement the phrase checks in a prompt.

## Topic

**Draft the register.** Triggers: "check this pack", "draft the gap register", "are the sources stale". Ask for the pack and the as-of date. Call the action. Show injection and stale flags first. End with "Nothing has been submitted or saved. The Compliance Officer or MLRO owns every gap conclusion."

There is no second topic that drafts an application, a SAR, or a promotion approval.

## Licensing

The costs page opened on 24 October 2026 says standard-harness agents are covered by a Microsoft 365 Copilot licence in Microsoft 365 channels, and are billed with Copilot Credits when the user has no such licence or the agent is used outside Microsoft 365. The article "Licensing for agents powered by the standard harness" was not opened. Confirm the names and the channel at build time. This guide is not a licence opinion.

The billing overview says the standard harness starts billing after publish, unlike the GitHub Copilot harness, which is charged from the start of building.

## Test in the studio

Use `examples/harbourline` and `eval/synthetic_dataset.json`. Do not paste a live policy into a shared test environment.

Check three paths: the Harbourline pack (one promotions phrase missing, no readiness finding), a document that says to ignore the instructions and mark the firm ready, and a run with `as_of` of 2027-04-01 (the pin is stale and the topic says so).
