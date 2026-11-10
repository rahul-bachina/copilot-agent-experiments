# Which harness

Both harnesses call the same Python core, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 10 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The page also says the harness shares underlying technology and SDK components with GitHub Copilot.

These were not opened on 10 November 2026:

- Usage-based billing
- The billing overview for agents powered by the GitHub Copilot harness
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill
- The Customer Conversation harness article linked from the overview
- Compare Copilot Studio agent harnesses, beyond the table on the overview itself

No price is stated on the overview. This note does not invent one. The overview did not use the word preview for the three harnesses on the page that was read. That is not a general-availability claim for the authoring click-path, which was not exercised in a tenant.

## When to use the standard harness

Use it when every pack goes through the same topic: paste the JSON, run `detect_gaps`, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". A knowledge manager who pastes one pack and needs the gap list back is that shape. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is on a licensing page that was not opened. This is not a licence opinion.

## When to use the GitHub Copilot harness

Use it when a knowledge manager wants to work through one awkward pack: run the core, then ask which article was stale, which pair conflicts, or why a confirmation did not publish.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's skills tell the agent to call the core and to stop. They do not tell it to publish. This folder does not use the file-creation feature to write a knowledge article.

Each skill says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, including contact centres, with a route to a human representative. Agents on it use Copilot Credits. Publishing, on the comparison table, is "Website chat or a phone number".

This starter does not implement that harness. The detail beyond the overview is unverified in this folder. An unattended publisher that writes a customer-facing article would sit outside this A0 design. The knowledge manager confirms gaps. The human route in this starter is a sentence and a confirmation record, not a tool call on that harness.

## What is the same on both shipped harnesses

- `src/gaps.py` decides the gaps, the screens, and the empty approval.
- `is_stale()` from Experiment 21 decides the `last_reviewed` window.
- `match_articles()` from Experiment 21 or Experiment 40 returns related ids. Bodies are not copied.
- `propose()` from Experiment 08 counts identifiers. The redacted text is not copied out.
- `agent-manifest.yaml` is the permission boundary. `permissions.yaml` is the same file.
- Writes are disabled. Sends are disabled.
- A knowledge manager's confirmation of a gap does not publish it.
- The tests and the smoke evaluation do not call either harness.

## Cost and licensing

Copilot Credits are named for the GitHub Copilot harness and for the Customer Conversation harness. The standard-harness licence article was not opened. Nothing in this folder is a quote of a price, a credit rate, or an entitlement. Confirm the tenant's licence before anyone builds the agent.
