# Copilot Studio standard harness

A build guide, not a solution you can import. Copilot Studio agents do not travel well as a zip, and this repository does not pretend otherwise.

This is the **standard harness**. The topic, the one flow, and the approval points below are unchanged. The Copilot Studio **GitHub Copilot harness** calls the same Python checklist and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 27 October 2026, describes the standard harness as the option where you define the topics and paths. In the comparison table, files are "Not a focus" and skills and memory are "Not a focus". The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for an HR lead. It is not a worker-facing bot, and it is not a route to the Acas helpline.

## What to create

1. In Copilot Studio, create an agent. Name it "ERA 2025 HR draft". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, a Teams send action, a Dataverse write, an HR-system connector, or a "send message" tool. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs the checklist and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the checklist as the only action, is easier to review.

## Checklist action

Inputs, supplied by the HR lead or by a form, never inferred by the model from a note that says "dismiss this employee":

| Input | Required | Notes |
|---|---|---|
| `pack` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the HR lead is reading the pack. |

Output: the JSON from `review()`. The topic displays the duties, the prompts, and the empty decision. It does not recompute them. It does not hide a null `hr_decision`.

How to host the function:

- A small internal API or an Azure Function that imports `review.py`, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that decides whether the employer complied. One implementation of the checklist is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not record a training attestation, and it does not send mail. A firm that later wants an attestation log adds that write as a separate, person-confirmed step, and updates the manifest first. This starter does not include it.

The Power Platform piece is that flow. Power Automate is the caller. Dataverse is not connected. SharePoint is not connected. Teams may be where the HR lead opens the agent. The agent is not posted into a channel that workers use.

## Topic

**Review a pack.** Triggers: "review this handbook pack", "which ERA duties are in force", "harassment prevention draft". Ask for the JSON, then the as-of date. Call the flow only after both are present. Show injection and stale flags before the duties. End with "Nothing has been decided, published, written, or sent. You decide what the organisation does next."

Do not add a branch that sets the decision from the model's text. Do not add a branch that emails a worker when a prompt is not evidenced. Do not add a branch that marks the employer compliant when every prompt is evidenced.

## Knowledge

Do not point the agent at the live Acas site, GOV.UK, or legislation.gov.uk. The citations are in the JSON, from `src/sources.py`. A live page would bypass `last_verified`.

Do not add the employer's live handbook as generative knowledge. Handbook text is quoted only from excerpts in the pack that the policy owner has already approved.
