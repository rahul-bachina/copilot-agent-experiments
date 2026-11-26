# Which harness

The page [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) was opened on 26 November 2026. This note says what that page showed. It does not state a price. A later change to the page is unverified.

| Harness on that page | What the page showed | This experiment |
| --- | --- | --- |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. It can take a goal, call tools, and create and edit Word, Excel, PowerPoint, and PDF files. It supports skills and memory and runs a task in a sandbox governed by Copilot Studio. Agents and workflows on this harness use Copilot Credits. The page states no price. The accounts-payable example on the page routes exceptions for approval. That is Microsoft's example, not a deployment of this starter. | The skills in this folder are the layout the common brief calls the GitHub Copilot harness. |
| Customer Conversation harness | Customer questions over voice and chat, with a route to a person. Agents on this harness use Copilot Credits. The page states no price. | Not used. This starter is not a customer bot. |
| Standard harness | Follows the topics, prompts, and paths the maker defines. The comparison table says billing is described in "Licensing for agents powered by the standard harness". That licensing page was not opened on 26 November 2026. No price is stated here. | Shipped as the topic guide in `copilot-studio/`. |

The page does not use the words "GitHub Copilot harness". The common brief for this repository asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships. The sentence that this harness is not the GitHub Copilot service was not on the page. That sentence is unverified.

Both harnesses call `src/coordinator.py`. Neither approves, rejects, signs, submits, pays, or sends. The Microsoft Foundry note is optional and is not a third harness.

Catalogue row O007 names Copilot Studio, Power Platform, and Microsoft 365. Power Platform, in this folder, is the flow note in [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md). It is guidance. It is not an importable solution. No mailbox or SharePoint library is connected.
