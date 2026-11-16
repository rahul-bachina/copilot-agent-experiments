# Which harness

Both harnesses call `src/answer.py`. The scope, the tests, and the manifest are the same. Neither harness decides an entitlement, sends a message, or writes a record.

Opened on 16 November 2026: [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview).

The page names three harnesses.

- **Standard harness.** Rule-based agents and structured conversations. The maker defines the topics and the paths. Skills and memory are "not a focus". Billing is described on a licensing page that was not opened. No price is stated here.
- **Microsoft Copilot harness.** Reasoning-heavy, multi-step work. It can take a goal, call tools, and adjust when a step fails. The page says it creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and runs each task in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No price was on the page.
- **Customer Conversation harness.** Voice and chat for customers, with a path to a person. This handbook agent is not that product. It is an internal policy answer.

The page does not use the words "GitHub Copilot harness". The common brief for this repository still asks for a GitHub Copilot harness layout: skills under `skills/`, tool contracts, and the same approval gates. That layout is what this folder ships for the reasoning-heavy harness. Whether Microsoft renamed an earlier "GitHub Copilot harness", and the sentence that it is not the GitHub Copilot service, were not on the page that was opened. Those points are unverified against that page.

This file does not say that routing weights or trigger phrases select a skill. The skill `description` says when to use it. Generative orchestration, where the tenant uses it, can select from that description. Classic orchestration limits are a different page, the knowledge-sources summary, and they are about how many knowledge sources a topic searches. They are not a routing weight for these skills.

## Which one to use

Use the **standard harness** when the paths are known: a policy question, a personal case, a gap. The topics are in [../copilot-studio/README.md](../copilot-studio/README.md).

Use the **Microsoft Copilot harness** when a person needs to follow the same JSON across a route, a withheld marking, and a statutory pin in one task. The skills are in [../skills/](../skills/). It still cannot approve a source or decide a case. File creation on that harness is a platform capability. This agent does not ask it to write a handbook or a letter.

## Knowledge sources, SharePoint, and Microsoft 365 Copilot

These products are not called by the Python. A tenant that later grounds a Copilot Studio agent should read the pages below rather than this readme's paraphrase. The limits below are what those pages said on 16 November 2026.

[Knowledge sources summary](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio). SharePoint connects to a SharePoint URL and uses Graph Search. Generative mode: 25 URLs. Classic mode: four URLs per generative answers node. Authentication is the agent user's Microsoft Entra ID. The page says the agent surfaces only content that user can access. "Allow ungrounded responses", when off, blocks a turn that used no knowledge source or tool. The page also says turning that setting off does not guarantee the model never uses general knowledge when it combines it with retrieved text. Citations returned from a knowledge source cannot be used as inputs to other tools. Uploaded files and SharePoint files have separate size notes on that page. The limits page linked from it was not opened.

[Add SharePoint as a knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint). The article says it describes the standard harness. The agent searches the registered URL and its subpaths, not parent or sibling sites, unless those are registered. Hyperlinks inside a registered page are not crawled. SharePoint lists selected in the upload path are ingested into Dataverse. Read is the minimum the page states. If the user has no permission, the response is no response. `Sites.Read.All` and `Files.Read.All` are the scopes named for manual authentication. The page says those scopes do not increase the user's own permissions. Restricted SharePoint Search, when enabled, blocks SharePoint. Generative answers from SharePoint are not available to guest users in SSO-enabled apps.

[What is Microsoft Copilot?](https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-overview). Experiences differ by grounding, integration, and licensing. The page says experiences are grounded in web and/or organisational data (Microsoft Graph and Work IQ) and that access is scoped by user permissions. Microsoft 365 Copilot (Premium) is described as grounding in organisational data through Microsoft Graph, Work IQ, Copilot Search, and semantic indexing, and as including SharePoint Advanced Management and Microsoft Purview controls. Copilot Chat (Basic) is described as primarily web data, with organisational content only when the user supplies it. This starter does not call Microsoft 365 Copilot, Work IQ, Graph, or Purview. A licence comparison on that page is not a price.

Experiment 50 reads one synthetic snapshot and proposes curation. `sharepoint_called` and `graph_called` stay false. A proposal is not a published page.
