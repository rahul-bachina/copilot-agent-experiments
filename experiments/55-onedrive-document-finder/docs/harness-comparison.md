# Which harness

Both harnesses call `find_documents` in `src/find.py`. The selection object, the withheld counts, the labels, and the tests are the same. Neither harness is a licence to search outside the confirmed locations.

Opened on 13 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

| | Standard harness | Microsoft Copilot harness |
|---|---|---|
| What the page says | Follows the topics and rules the maker defines. A fit for a well-understood request. | Reasoning-heavy multi-step work. Skills, memory, file creation, and a sandbox. Billed in Copilot Credits. The page states no price. |
| How this starter uses it | Three topics: confirm locations, return the JSON, acknowledge from a separate review object. | Four skills in `skills/`. The same Python calls. No second search. |
| When it fits | The question is stable: locations, then a list, then stop. | The user asks a follow-up about one rank, a duplicate, or a safeguarding flag, still on the same JSON. |
| What it must not do | Add a connector that can move, delete, share, or send. | Use file creation to write a copy of a withheld file. This starter does not. |

The page names a third harness, Customer Conversation, for customer voice and chat, with a route to a human representative, billed in Copilot Credits. It is not built here. The detail page linked from the overview was not opened.

The page opened on 13 November 2026 does not use the words GitHub Copilot harness. It does not say that harness is not the GitHub Copilot service. Catalogue wording from October 2026 used that sentence. Against the page opened for this experiment, that sentence is unverified. The skill files in this folder are the packaging the common brief asks for, pointed at the runtime the current page describes.

Copilot Credits are the tenant's billing if a tenant later builds the Microsoft Copilot harness. This repository does not spend them and does not quote a price. The linked billing page was not opened.

Microsoft Foundry is optional and is not a third harness. See [foundry.md](foundry.md).
