# Which harness

Both harnesses call the same Python core, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 13 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The overview names three harnesses: Microsoft Copilot, Customer Conversation, and standard. The text retrieved that day does not use the name GitHub Copilot harness, and it does not say that the harness is not the GitHub Copilot service. This folder still ships the skills layout the catalogue calls the GitHub Copilot harness. Experiment 52 recorded a different sentence from the same URL on 12 November 2026. Treat that earlier sentence as not re-verified on this read.

These were not opened on 13 November 2026:

- Usage-based billing
- A billing overview for agents on the Microsoft Copilot harness
- Licensing for agents on the standard harness
- The skills overview, and the page for adding an uploaded skill
- The Customer Conversation harness article linked from the overview
- A comparison page beyond the table on the overview itself
- Microsoft 365 Copilot licensing prices
- A dedicated Copilot in PowerPoint how-to
- The PowerPoint JavaScript API
- Graph driveItem upload

No price is stated on the overview. This note does not invent one. The overview did not use the word preview for the three harnesses on the page that was read. That is not a general-availability claim for the authoring click-path, which was not exercised in a tenant.

## When to use the standard harness

Use it when every briefing goes through the same topic: paste the JSON, run `propose_outline`, show the outline, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are not a focus of that harness. A presenter who pastes one pack and needs the cited outline back is that shape. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is on a licensing page that was not opened. This is not a licence opinion.

## When to use the skills layout

Use it when a presenter wants to work through one awkward pack: run the core, then ask which passage was refused, which figure was withheld, or why an approval did not share the deck, and then ask for the local file only after approval.

On the page opened 13 November 2026, the reasoning-heavy harness is titled Microsoft Copilot harness. It can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's slide file is built by `src/slides.py` after approval. The skills tell the agent to call the core and to stop. They do not tell it to share the file. The harness file-creation feature was not exercised in a tenant.

Each skill says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, including contact centres, with a route to a human representative. Agents on it use Copilot Credits. Publishing, on the comparison table, is a website chat or a phone number.

This starter does not implement that harness. The detail beyond the overview is unverified in this folder. An unattended sender that shares a deck would sit outside this A1 design. The presenter approves the outline. The human route in this starter is a sentence and an approval record, not a tool call on that harness.

## Copilot in PowerPoint

A dedicated Copilot in PowerPoint how-to was not opened. What was opened:

- The [Microsoft 365 Copilot overview](https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview). The PowerPoint row describes creating a presentation from a prompt or existing content, summarising, and editing, including images and deck-wide formatting. Grounding through Microsoft Graph and Work IQ is described on the same page. Work IQ can be turned on or off. Neither product is called by this starter.
- The [Work IQ overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/). It describes a permission-aware layer with A2A, a remote MCP server, and a REST API. Usage is independent of Microsoft 365 Copilot licensing and consumes Copilot Credits. No price and no general-availability date are on the page that was opened. Work IQ is not called.

The PowerPoint JavaScript API and the Graph upload page were not opened. The local file is Office Open XML from the standard library.

## What is the same on both shipped harnesses

- `src/narrative.py` decides the citations, the gaps, the withheld figures, and the empty approval.
- `score_claim()` and `passage_currency()` from Experiment 29 decide whether a quote is supported and whether a review stamp is stale.
- `normalise_value()` and `classify_values()` from Experiment 36 compare figure values. A material discrepancy is not copied.
- `agent-manifest.yaml` is the permission boundary. `permissions.yaml` is the same file.
- Writes are disabled. Sends are disabled.
- A presenter's approval of the outline and every citation does not produce slides and does not share the deck.
- The tests and the smoke evaluation do not call either harness.

## Cost and licensing

Copilot Credits are named for the Microsoft Copilot harness and for the Customer Conversation harness. The standard-harness licence article was not opened. Nothing in this folder is a quote of a price, a credit rate, or an entitlement. Confirm the tenant's licence before anyone builds the agent.
