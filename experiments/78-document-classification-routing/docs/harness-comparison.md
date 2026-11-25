# Which harness

Opened on 25 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview). The notes below are that reading. A later change to the page is unverified.

| Harness on that page | What the page said | This experiment |
| --- | --- | --- |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. It can take a goal, break it into steps, and call tools. It creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox governed by Copilot Studio. Agents and workflows on this harness use Copilot Credits. The page states no price. | The skills in this folder are the layout the common brief calls the GitHub Copilot harness. This starter does not create those Office files and does not use memory. |
| Customer Conversation harness | Customer questions over voice and chat, with a route to a person. Agents on this harness use Copilot Credits. The page states no price. | Not used. This starter is not a customer bot. |
| Standard harness | Follows the topics and rules the maker defines. Billing is described on a licensing page that was not opened. | Shipped as the topic guide in `copilot-studio/`. |

The page, on that reading, does not use the words "GitHub Copilot harness". It does not say that the Microsoft Copilot harness is not the GitHub Copilot service. The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. Whether an earlier page used the name "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page opened on 25 November 2026. Those points are unverified.

The page did not label the Microsoft Copilot harness as preview. This starter does not turn that silence into a separate availability claim.

Both harnesses call `src/classify.py`. Neither files a document. The Microsoft Foundry note is optional and is not a third harness. No price is stated here because the page stated none.

Catalogue row O003 names AI Builder or Microsoft Foundry, and Power Platform. AI Builder was not opened on 25 November 2026. Treat a claim about what AI Builder classifies as unverified. Power Platform, if a team adds it, would be the flow in [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md). It is a build note. It is not an importable solution. The Foundry note is still here because a team may want a short narrative beside the JSON. The runnable sample does not call either product.
