# Which harness

Opened on 19 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page names three harnesses.

| Harness on that page | What the page says | This experiment |
| --- | --- | --- |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. Skills, memory, file creation, and a sandbox. The prose says agents on this harness use Copilot Credits. The page states no price. | Catalogue row L001 names this harness first, with Azure. The skills in this folder are the layout the common brief calls the GitHub Copilot harness. |
| Customer Conversation harness | Customer questions over voice and chat, with a route to a person. Copilot Credits. | Not used. This starter is not a customer bot. |
| Standard harness | Follows the topics and rules the maker defines. | Shipped as the topic guide in `copilot-studio/`. |

The page does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. Whether Microsoft renamed an earlier "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page that was opened. Those points are unverified against that page.

Both harnesses call `src/review.py`. Neither accepts terms. The Microsoft Foundry note is optional and is not a third harness. No price is stated here because the page stated none.

Azure in the catalogue code is the Microsoft Foundry option in [foundry.md](foundry.md). It is not a second legal engine.
