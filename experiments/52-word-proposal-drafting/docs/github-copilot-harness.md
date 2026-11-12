# GitHub Copilot harness

A Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 12 November 2026 says customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio, and that agents on this harness use Copilot Credits. The page states no price.

This starter uses the harness for a follow-up on one JSON draft: which source was cited, which figure was withheld, and why an acceptance did not submit. The skills are in `skills/`. Each description says when to use it. This starter does not assign a weight to a skill. Selection from those descriptions was not exercised in a tenant.

The overview says the harness can create and edit Word files. The Word file in this experiment is still `src/word_draft.py`. A skill must not upload that file. The harness file-creation feature was not turned on here. Whether a tenant build would create a second file is unverified.

## Skills

| Skill | When |
|---|---|
| `draft-proposal-response` | The author needs the matrix from one synthetic pack. |
| `check-cited-claims` | The author asks why a row is not met, or why a figure is missing. |
| `record-author-acceptance` | The author has read the complete draft and wants that decision recorded. |

## Tool contracts

`schema/draft_tool.schema.json` allows one synthetic pack. It has no submit field and no price field.

`schema/review_tool.schema.json` allows three decisions. It has no email address and no portal URL. Additional properties are refused by the schema. The core also strips a `submitted` key if one is passed beside the schema.

## Approval gates

1. The author accepts the complete draft before it is used anywhere. `draft_proposal()` leaves `human_approval` null.
2. Every gap and every author check has to be acknowledged before acceptance is recorded.
3. `author_accept_complete_draft` sets `human_approval.recorded` and leaves `submitted` and `used_anywhere` false.
4. Submit, send, and upload are not tools. The functions raise `ProposalForbidden`.

## What the harness must not do

- Submit the bid, or say that acceptance submitted it.
- Invent a sentence that is not in `draft_answer`.
- Copy a figure out of the library file. The core already withheld it.
- Call Microsoft Graph or the Word JavaScript API. Those pages were read. They are not connected.
