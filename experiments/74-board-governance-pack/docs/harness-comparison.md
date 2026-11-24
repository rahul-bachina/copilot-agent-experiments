# Which harness

This experiment did not re-open the harness overview. The notes below follow the page [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) as recorded for Experiment 70 on 20 November 2026. A fresh opening was not done on 24 November 2026. Treat any change on that page since then as unverified.

| Harness on that page | What Experiment 70 recorded from the page | This experiment |
| --- | --- | --- |
| Microsoft Copilot harness | Reasoning-heavy, multi-step work. Skills, memory, and file creation. The prose says agents and workflows on this harness use Copilot Credits. The page states no price. | The skills in this folder are the layout the common brief calls the GitHub Copilot harness. |
| Customer Conversation harness | Customer questions over voice and chat, with a route to a person. | Not used. This starter is not a customer bot. |
| Standard harness | Follows the topics and rules the maker defines. Billing is described on a licensing page that was not opened. | Shipped as the topic guide in `copilot-studio/`. |

The page, on that reading, does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. Whether Microsoft renamed an earlier "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page Experiment 70 opened. Those points are unverified.

Both harnesses call `src/pack.py`. Neither circulates a pack or approves minutes. The Microsoft Foundry note is optional and is not a third harness. No price is stated here because the page stated none.

Catalogue row L010 names M365 and Work IQ. Work IQ is not called. A live permission-aware read is unverified. Power Platform, in this folder, is the flow in [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md). It is a build note. It is not an importable solution. The Foundry note is still here because a team may want a short narrative beside the JSON.
