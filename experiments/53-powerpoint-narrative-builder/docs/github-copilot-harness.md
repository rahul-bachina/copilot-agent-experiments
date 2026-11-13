# GitHub Copilot harness

The catalogue calls this layout the GitHub Copilot harness. The overview opened on 13 November 2026 names three harnesses: Microsoft Copilot, Customer Conversation, and standard. The text retrieved that day does not use the name GitHub Copilot harness, and it does not say that the harness is not the GitHub Copilot service. Experiment 52 recorded both from the same URL on 12 November 2026. Treat that earlier sentence as not re-verified on this read.

The Microsoft Copilot harness, on the page that was opened, can create and edit PowerPoint files, use skills and memory, and run each task in a sandbox. Agents on it use Copilot Credits. The page states no price.

This starter uses the skills for a follow-up on one JSON outline: which passage was cited, which figure was withheld, and why an approval did not share the deck. The skills are in `skills/`. Each description says when to use it. This starter does not assign a weight to a skill. Selection from those descriptions was not exercised in a tenant.

The slide file in this experiment is still `src/slides.py`, and only after `record_presenter_approval()`. A skill must not share that file. The harness file-creation feature was not turned on here. Whether a tenant build would create a second file is unverified.

## Skills

| Skill | When |
|---|---|
| `propose-narrative` | The presenter needs the outline from one synthetic pack. |
| `record-presenter-approval` | The presenter has read the outline and every citation and wants that decision recorded. |
| `produce-slides` | The presenter has approved the outline and every citation and wants a local file that is not shared. |

## Tool contracts

`schema/outline_tool.schema.json` allows one synthetic pack. It has no share field and no logo field.

`schema/approval_tool.schema.json` allows three decisions. It has no email address and no site URL. Additional properties are refused by the schema.

## Approval gates

1. The presenter approves the outline and every citation before slides are produced. `propose_outline()` leaves `human_approval` null and `slides_produced` false.
2. Every sourced citation, every gap, the accessibility checklist, and the markings have to be acknowledged before approval is recorded. A safeguarding flag has to be acknowledged too.
3. `presenter_approve_outline_and_citations` sets `human_approval.recorded` and leaves `slides_produced` and `shared` false.
4. `produce_slides()` writes a local file only after that record. `shared` stays false.
5. Publish, send, and share are not tools. The functions raise `NarrativeForbidden`.

## What the harness must not do

- Share the deck, or say that approval shared it.
- Invent a sentence that is not in a sourced claim.
- Copy a figure that is not on the approved figures sheet.
- Call Microsoft Graph or the PowerPoint JavaScript API. Those pages were not opened. They are not connected.
