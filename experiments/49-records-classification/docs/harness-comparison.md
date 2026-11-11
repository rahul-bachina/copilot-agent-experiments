# Which harness

Both harnesses call the same Python core, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 11 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The page also says the harness shares underlying technology and SDK components with GitHub Copilot.

The same page says agents and workflows on the GitHub Copilot harness use Copilot Credits. The comparison table's billing cell for that harness points at a billing overview. That billing page was not opened. No price is stated on the overview. This note does not invent one.

These were not opened on 11 November 2026:

- Usage-based billing
- The billing overview for agents powered by the GitHub Copilot harness
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill
- The Customer Conversation harness article linked from the overview
- Compare Copilot Studio agent harnesses, beyond the table on the overview itself

The overview did not use the word preview for the three harnesses on the page that was read. That is not a general-availability claim for the authoring click-path, which was not exercised in a tenant.

## When to use the standard harness

Use it when every document goes through the same topics: paste the JSON, run `classify_record`, show the result, stop. Confirmation and the label stub are separate topics with the same stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". A records manager who pastes one document and needs the draft back is that shape. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is on a licensing page that was not opened. This is not a licence opinion.

## When to use the GitHub Copilot harness

Use it when a records manager wants to work through one awkward document: run the core, then ask which phrase matched, why the item is queued, or why a stub did not run.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's skills tell the agent to call the core and to stop. They do not tell it to delete a record. This folder does not use the file-creation feature.

Each skill says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, including contact centres, with a route to a human representative. Agents on it use Copilot Credits. Publishing, on the comparison table, is "Website chat or a phone number".

This starter does not implement that harness. The detail beyond the overview is unverified in this folder. An unattended disposal agent on that harness would sit outside this A1 design. The human route in this starter is a sentence and a review record, not a tool call on that harness.

## Microsoft Foundry

Optional. A short note may be written from the JSON. The category, the retention entry, the marking, the confidence, and the empty approval stay in the Python core. See [foundry.md](foundry.md). No Foundry resource is deployed in this folder.

## What this folder does not verify

- A price, a credit rate, or a licence entitlement.
- That a skill upload succeeds in a tenant. The click-path was not exercised.
- The Customer Conversation harness beyond the overview.
- That the word "preview" is absent from every related page. Only the overview was opened.
