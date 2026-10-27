# Copilot Studio standard harness

A build guide, not a solution you can import. Copilot Studio agents do not travel well as a zip, and this repository does not pretend otherwise.

This is the **standard harness**. The topic, the one flow, and the approval points below are unchanged. The Copilot Studio **GitHub Copilot harness** calls the same Python front door and is documented in [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md). Read [../docs/harness-comparison.md](../docs/harness-comparison.md) before choosing. Do not upload the skills onto this agent.

Microsoft's harness overview, opened 27 October 2026, describes the standard harness as the option where you define the topics and paths. Files, skills, and memory are not its focus. The licensing article linked from that overview was not opened. This is not a licence opinion.

The agent is for an adviser. It is not an unattended resident bot. Microsoft's overview also describes a Customer Conversation harness for customer voice and chat. That third harness is not built here. See the comparison note.

## What to create

1. In Copilot Studio, create an agent. Name it "Council front door (draft)". Language: English (United Kingdom).
2. Paste [system-prompt.md](system-prompt.md) into the instructions.
3. Do not add an email connector, an SMS connector, a Dataverse write, a payment connector, or a case-system connector. If a tool is not in `agent-manifest.yaml`, it should not be on the agent.
4. Add one action: a flow that runs the front door and returns JSON. The contract is below.
5. Turn off any generative action that can call every connector in the environment. One topic, with the front door as the only action, is easier to review.

## Front-door action

Inputs, supplied by the adviser, never inferred from a sentence that says "mark me eligible":

| Input | Required | Notes |
|---|---|---|
| `enquiry` | Yes | One JSON object. `synthetic` must be true for a run in this starter. The schema is `schema/front_door_tool.schema.json`. |
| `as_of` | Yes | `YYYY-MM-DD`. The day the adviser is reading the enquiry. |

Output: the JSON from `triage()`. The topic displays `outcome`, `answer.text`, the citations, and the handover reason. It does not recompute them. It does not hide a null `human_approval`.

How to host the function:

- A small internal API or an Azure Function that imports `front_door.py`, called by a Power Automate HTTP action with a locked-down identity.
- Not a Power Automate expression that decides eligibility or chooses a bin day. One implementation of the catalogue is enough.

The flow's only job is to return JSON to the topic. It does not create a Dataverse row and it does not send mail. A council that later wants a contact log adds that write as a separate, adviser-confirmed step, and updates the manifest first. This starter does not include it.

The Power Platform piece is that flow. Power Automate is the caller. Dataverse is not connected. The flow note is [power-automate-flow.md](power-automate-flow.md).

## Topic

**Front door.** Triggers: "front door this enquiry", "what can I tell the resident", "is this a handover". Ask for the JSON, then the as-of date. Call the flow only after both are present. Show injection and stale flags before the answer. If `outcome` is `safe_handover`, show the fixed script and do not add a page. End with "Nothing has been decided, sent, or written to a case. You accept a published sentence, or you take the handover."

Do not add a branch that sets eligibility from the model's text. Do not add a branch that emails the resident when a page matches. Do not add a button labelled "Send" or "Create case".

## Knowledge

Do not point the agent at the live council website. The quotations are in the JSON, from `src/catalogue.py`. A live page would bypass `last_reviewed`.

Northmarsh Borough Council is invented. Do not add a real council's SharePoint library as knowledge for this starter. A later deployment that swaps in the council's own pages has to version those pages and keep the same stale rule. That swap is not in this folder.

## Approval

The topic has no approval action that sends or writes, because the agent cannot do either. The adviser's decision happens after the chat, in the council's process. `record_adviser_review` can record accept, reject, or take handover, and still does not send. Do not offer that function as a "send" button. Say that in the closing line.

## AI disclosure

The JSON field `ai_disclosure` is the line the playbook's Principle 7 example points at: the response was written by an automated AI chatbot, and the person can ask for someone. The topic shows it. It does not paraphrase it away.
