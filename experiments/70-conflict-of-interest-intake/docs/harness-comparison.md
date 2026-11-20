# Which harness

Opened on 20 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page names three harnesses. No "last updated" line was in the extract. That date is unverified.

| Harness on that page | What the page says | This experiment |
| --- | --- | --- |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. Skills, memory, and file creation. The prose says agents and workflows on this harness use Copilot Credits. The page states no price. The comparison table points at an overview of billing rather than repeating the words Copilot Credits in that cell. | The skills in this folder are the layout the common brief calls the GitHub Copilot harness. |
| Customer Conversation harness | Customer questions over voice and chat, with a route to a person. The page says agents on this harness use Copilot Credits. | Not used. This starter is not a customer bot. |
| Standard harness | Follows the topics and rules the maker defines. Billing is described on a licensing page that was not opened. | Shipped as the topic guide in `copilot-studio/`. |

The page does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. Whether Microsoft renamed an earlier "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page that was opened. Those points are unverified against that page.

Both harnesses call `src/declaration.py`. Neither decides that a conflict exists. The Microsoft Foundry note is optional and is not a third harness. No price is stated here because the page stated none.

Catalogue row L005 names Copilot Studio and Power Platform first. Power Platform, in this folder, is the flow in [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md). It is a build note. It is not an importable solution. Azure is not a stack code on this row. The Foundry note is still here because a team may want a short narrative beside the JSON.
