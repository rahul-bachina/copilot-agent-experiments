# Which harness runs this draft

Both harnesses call the same assembler, the same manifest, and the same tests. The difference is how much reasoning sits around that call. Neither harness decides needs, provision, placement, or outcomes.

Pages opened on 4 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)
- [Overview of usage-based billing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview)
- [Standard harness licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing)

The cost-management page and the Microsoft Foundry cost page were not opened for this experiment. They are not sources here.

The harness overview says the GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

A Learn page on generative orchestration was not opened. This note does not assign a weight to a phrase. Where generative orchestration is on, selection is described as using the topic description. That page was not checked on 4 November 2026, so the exact behaviour is unverified.

## GitHub Copilot harness

Use it when the caseworker drops in an advice bundle and then asks follow-up questions: which advice is missing, why two reports conflict, why section I is blank.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox. The overview does not mark the harness itself as preview. The page does not describe a control to turn memory off. The skills say not to store the advice.

This experiment's skills are under `skills/`. They tell the agent to call `assemble_ehcp_draft` and to stop. They do not tell it to decide provision or to send the draft.

## Standard harness

Use it when the caseworker wants the same topic every time: point at the bundle, run the draft, show the JSON, stop.

Microsoft's overview says the standard harness follows the topics and rules the maker defines. Skills and memory are listed as "Not a focus" for that harness. The guide is `copilot-studio/README.md`. There is no skill on that path.

## Customer Conversation harness

The overview describes a third harness for customer voice and chat. It is not built here.

## Cost and licensing

Only what the three pages above said on 4 November 2026. No prices are copied here. The billing overview had a diagram of ranges. The numbers on that diagram were not transcribed.

| | GitHub Copilot harness | Standard harness |
|---|---|---|
| What Microsoft says it is for | Reasoning-heavy, multi-step work, tools, files, skills | Topics and rules the maker defines |
| Billing page | For these experiences, Copilot Credits are charged for large language model tokens, tools including knowledge and MCP, and the harness. Charged from the moment you start building, including testing. | The billing overview says the standard harness starts billing after publish. |
| Microsoft 365 Copilot licence | The licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for this harness. A second sentence on that page is about answer types in Copilot Chat, Teams, or SharePoint. The two sentences are not merged. | The cost-management page was not opened for this experiment. This cell does not state a coverage rule for the standard harness. |

The common currency changed from messages to Copilot Credits on 1 September 2025. The licensing page says the quantity per prepaid pack and the pay-as-you-go rate did not change. The quantity is not stated here.

## Microsoft Foundry

The catalogue row names Microsoft Foundry and Azure. This folder does not call either. A later host that proposed section tags would be deciding needs or provision. That host is not built. See `docs/foundry.md`.
