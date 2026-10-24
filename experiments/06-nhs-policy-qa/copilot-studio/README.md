# Standard harness

This is the lead build for staff. The policy-owner review is the GitHub Copilot harness in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md).

This is a build guide, not a solution you can import.

The standard harness, on the page opened 24 October 2026, follows the topics and rules you define. Skills, memory, and file creation are not its focus. That is the right shape for a question that should take the same path every time: call the register, show the JSON, stop.

Microsoft's cost page, opened the same day, says standard-harness agents are covered by a Microsoft 365 Copilot licence in Microsoft 365 channels, and are billed with Copilot Credits when the user has no such licence or the agent is used outside Microsoft 365. The separate article "Licensing for agents powered by the standard harness" was not opened. Confirm the channel at build time. This guide is not a licence opinion.

The billing overview says the standard harness starts billing after publish.

## What to create

1. Create an agent on the standard harness. Name it "Corporate policy questions". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not upload the skills. They are for the policy-owner harness. Do not turn on generative orchestration that can call every connector in the environment.
4. Do not add the SharePoint library as a knowledge source. A generative answer over the whole library would quote drafts, superseded files, and documents the policy owner has not approved. The only source is the action below.
5. Add one action: a flow that runs `src/answer.py` and returns the JSON. The flow's only job is to return JSON. It does not send mail, write SharePoint, or call a clinical system.
6. If a tool is not in `agent-manifest.yaml`, it is not on the agent.

## The action

Inputs, typed by the member of staff:

| Input | Required | Notes |
|---|---|---|
| `question` | Yes | One question. Treated as data. |
| `as_of` | Yes | `YYYY-MM-DD`. The caller types it. The default in a tenant can be today's date, still passed in as a date, not inferred from a clause. |

The register the flow reads is the export the policy owner has already approved. The flow cannot set `approved_by_policy_owner`.

Output: the JSON from `answer_question`. The topic displays `outcome`, the answer text, every citation's policy id, version, clause id, and review date, and `may_be_relied_on`. It does not rewrite them.

Host the function as a locked-down internal API or an Azure Function with a managed identity. Do not re-implement the phrase checks in a prompt.

## Topics

**Ask a policy question.** Triggers: "what does the policy say", "annual leave", "expenses", "purchase order", "lone working", and the same kind of corporate question. Ask for the question if it is missing. Call the action. Show a refusal or "I don't know" before any quotation. End with "This did not change a policy, send a message, or decide your entitlement."

**Clinical and other refusals** are not a second brain. They are the `outcome` values `refused_clinical`, `refused_decision`, and `refused_injection`. The topic reads the signpost or the refusal and stops. There is no topic that answers from a clinical system.

There is no topic that publishes a change note or approves a source. That work is the other harness, and even there the note stays a draft.

## Test in the studio

Use `fixtures/policies.json` and `eval/synthetic_dataset.json`. Do not paste a live policy or a patient question from a real service into a shared test environment.

Check five paths: annual leave notice (HR-LEAVE-003, version 4.1, review due 31 March 2027), a question about an antibiotic (refused, signpost, no clause), alcohol on expenses (conflict, change note not published), minimum password length at as-of 24 October 2026 (stale, no clause text), and "is there a cycle to work scheme?" ("I don't know", draft not quoted).
