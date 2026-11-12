# Which harness

Both harnesses call the same Python core, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 12 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The page also says the harness shares underlying technology and SDK components with GitHub Copilot.

The same page says agents and workflows on the GitHub Copilot harness use Copilot Credits. The comparison table's billing cell for that harness points at a billing overview. That billing page was not opened. No price is stated on the overview. This note does not invent one.

These were not opened on 12 November 2026:

- Usage-based billing
- The billing overview for agents powered by the GitHub Copilot harness
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill
- The Customer Conversation harness article linked from the overview
- The GitHub Copilot harness knowledge-sources page
- Compare Copilot Studio agent harnesses, beyond the table on the overview itself

The overview did not use the word preview for the three harnesses on the page that was read. That is not a general-availability claim for the authoring click-path, which was not exercised in a tenant.

## When to use the standard harness

Use it when every snapshot goes through the same topics: paste the JSON, run `curate_site`, show the result, stop. Approval and the curation stub are separate topics with the same stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". A site owner who pastes one snapshot and needs the draft back is that shape. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is on a licensing page that was not opened. This is not a licence opinion.

## When to use the GitHub Copilot harness

Use it when a site owner wants to work through one awkward snapshot: run the core, then ask which evidence matched, why an item is queued, or why a stub did not run.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's skills tell the agent to call the core and to stop. They do not tell it to delete a page. This folder does not use the file-creation feature.

Each skill says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant.

## SharePoint as a knowledge source

[Add SharePoint as a knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint) was opened on 12 November 2026. The page says it describes features used in agents or agent flows powered by the standard harness. It says the agent surfaces only content the user has permission to access, and otherwise responds with no response. Read is the minimum stated. Searches stay on the registered URL and its subpaths. Hyperlinks inside a registered page are not crawled. SharePoint lists are described as ingested into Dataverse.

This starter does not register a SharePoint site as a knowledge source. The snapshot is pasted JSON. The permission filter is in the Python core: an item is read only when a requesting principal is on its `readers` list.

The GitHub Copilot harness knowledge-sources page was not opened. Whether that harness accepts a SharePoint knowledge source the same way is unverified here.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, including contact centres, with a route to a human representative. Agents on it use Copilot Credits. Publishing, on the comparison table, is "Website chat or a phone number".

This starter does not implement that harness. The detail beyond the overview is unverified in this folder. An unattended publishing agent on that harness would sit outside this A1 design. The human route in this starter is a sentence and a review record, not a tool call on that harness.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The proposals, the confidence, the queue reasons, and the empty approval stay in the Python core. See [foundry.md](foundry.md). No Foundry resource is deployed in this folder.

## What this folder does not verify

- A price, a credit rate, or a licence entitlement.
- That a skill upload succeeds in a tenant. The click-path was not exercised.
- The Customer Conversation harness beyond the overview.
- The GitHub Copilot harness knowledge-sources page.
- That the word "preview" is absent from every related page. Only the overview and the SharePoint knowledge page were opened.
