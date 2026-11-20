# Which harness

Both harnesses call `src/map_controls.py`. The approval gates are the same. Neither marks a control as met, closes a gap, edits a policy, or writes to a GRC system.

The page [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) was opened on 20 November 2026.

| Harness on that page | What the page says | What this folder uses it for |
| --- | --- | --- |
| Standard harness | Rule-based agents. It follows the topics and rules the maker defines. | The build guide in `copilot-studio/`. A topic runs the proposal and stops. A second topic records one approval object. |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. Skills, memory, file creation, and a sandbox. The page says agents on this harness use Copilot Credits. The page states no price. | Catalogue row L003 names this harness first, with Microsoft 365. The skills in this folder are the layout the common brief calls the GitHub Copilot harness. |
| Customer Conversation harness | Customer voice and chat, with a path to a person. | Not used. This starter is not a customer conversation. |

The page does not use the words "GitHub Copilot harness". It does not say that the Microsoft Copilot harness is not the GitHub Copilot service. Older wording to that effect is unverified against the page opened on this date.

Pricing pages linked from the overview were not opened. This folder does not quote a price. A tenant that turns the Microsoft Copilot harness on consumes Copilot Credits. That is what the overview says. The amount is not stated here.

The Microsoft Copilot harness can create and edit Word, Excel, PowerPoint, and PDF files. That capability is not a tool of this agent. `edit_policy()` raises. A policy file is not written.

Microsoft 365 is the catalogue deployment context: policies would sit in a document library the organisation already has. This starter has no SharePoint connector and does not sign in to Microsoft 365. The text is the JSON the caller passes.

The deterministic core, the manifest, and the tests are the same for both harnesses. A note from Microsoft Foundry, if one is added later, reads the JSON. It does not replace the hashes.
