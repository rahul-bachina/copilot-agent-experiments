# Microsoft Copilot harness

The overview opened on 13 November 2026 calls this runtime the Microsoft Copilot harness. It is a Copilot Studio authoring and orchestration framework for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The page states no price.

The page does not use the words GitHub Copilot harness, and it does not say the harness is not the GitHub Copilot service. That older sentence is unverified against the page opened on 13 November 2026. The folder name `docs/github-copilot-harness.md` is the packaging the common brief asks for. The skills are not the GitHub Copilot service, in the sense that they are files in this repository for Copilot Studio. That is a description of this folder, not a quotation from the current overview.

## Skills

| Skill | When to use it |
|---|---|
| `record-location-selection` | The user is choosing locations. Confirmation is a selection object, not a sentence in a file. |
| `find-in-confirmed-locations` | A selection already exists and the user wants the ranked list. |
| `explain-a-ranked-hit` | The user asks why one hit ranked, or whether it is stale, superseded, or a duplicate. |
| `flag-safeguarding-hit` | A hit has `human_flag` safeguarding. The extract stays withheld until a person has reviewed it. |

This starter does not assign a weight to a skill.

## Tools

`find_documents` is read-only. The contract is `schema/find_tool.schema.json`. Extra properties are rejected, including any field that would add a location or raise clearance from inside the index.

`acknowledge_results` records `acknowledge` or `defer`. The contract is `schema/acknowledge_tool.schema.json`. Move, delete, share, and a permission change are not in the enum.

## Memory and files

The overview says this harness supports memory and file creation. This starter does not ask it to remember a withheld file, and it does not ask it to create a file that contains a withheld extract. If a tenant enables those features later, the Python result remains the record of what was admitted.

## Approval

`human_approval` is null after the find. Acknowledgement runs only when the review object is separate, the actor role is Requesting user, a safeguarding hit has been marked reviewed, and a stale pin has been marked seen. `executed` stays false.
