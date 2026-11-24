# Which harness

The page [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) was opened on 24 November 2026.

| Harness on that page | What the page said | This experiment |
| --- | --- | --- |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. It can take a goal, break it into steps, and adjust. It creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox. The prose says agents and workflows on this harness use Copilot Credits. The page states no price. | The skills in this folder are the layout the common brief calls the GitHub Copilot harness. |
| Customer Conversation harness | Customer questions over voice and chat, with a route to a person. The prose says agents on this harness use Copilot Credits. | Not the implementation in this folder. A resident chat could use it later. This starter does not publish a phone number or a website bot. |
| Standard harness | Follows the topics and rules the maker defines. The comparison table points billing to a licensing page. That page was not opened. | Shipped as the topic guide in `copilot-studio/`. |

The page does not use the words "GitHub Copilot harness". It does not say that this harness is not the GitHub Copilot service. Those points in the common brief are unverified against the page opened on 24 November 2026. No price is stated here because the page stated none. Nothing on the page was marked preview in the sections that were read. A later change to the page is unverified.

Both shipped harnesses call `src/assistant.py`. Neither decides eligibility. The Microsoft Foundry note is optional and is not a third harness.

Catalogue row V009 names Copilot Studio and Microsoft 365. Power Platform, in this folder, is the flow in [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md). It is a build note. It is not an importable solution.
