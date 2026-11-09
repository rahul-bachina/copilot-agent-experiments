# Which harness

Both harnesses call the same Python core, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 9 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The page also says the harness shares underlying technology and SDK components with GitHub Copilot.

These were not opened on 9 November 2026:

- Usage-based billing
- The billing overview for agents powered by the GitHub Copilot harness
- Licensing for agents powered by the standard harness
- Skills overview, and the page for adding an uploaded skill
- The Customer Conversation harness article linked from the overview
- Compare Copilot Studio agent harnesses, beyond the table on the overview itself

No price is stated on the overview. This note does not invent one. The overview did not use the word preview for the three harnesses on the page that was read. That is not a general-availability claim for the authoring click-path, which was not exercised in a tenant.

## When to use the standard harness

Use it when every case goes through the same topic: paste the JSON, run `propose_route`, show the result, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". It gives an internal help desk that routes simple requests as an example of that shape. A queue proposal with a fixed human stop is the same shape: one topic, one result, no second reasoning loop. The guide is `copilot-studio/README.md`. There is no skill on that path. The queue in the result is the Python rule match. It is not produced by a topic description. Billing for the standard harness is on a licensing page that was not opened. This is not a licence opinion.

## When to use the GitHub Copilot harness

Use it when an adviser wants to work through one awkward case: run the core, then ask which rule matched, why the confidence band was not used, or which sentence is a citation and which is a fixed reason.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's skills tell the agent to call the core and to stop. They do not tell it to move a case or to edit a rule. This folder does not use the file-creation feature.

Each skill says when to use it. The overview describes this harness as taking a goal and breaking it into steps.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, including contact centres, with a route to a human representative. Agents on it use Copilot Credits. Publishing, on the comparison table, is "Website chat or a phone number".

This starter does not implement that harness. The detail beyond the overview is unverified in this folder. An unattended router that reroutes, closes, or escalates on that harness would sit outside this A1 design. The human route in this starter is a sentence and a handover record, not a tool call on that harness.

## What is the same on both shipped harnesses

- `src/routing.py` decides the queue, the priority, the reason, the confidence band, and the empty approval.
- `agent-manifest.yaml` is the permission boundary. `permissions.yaml` is the same file.
- Writes are disabled. Sends are disabled.
- An adviser confirmation does not reroute. A queue owner's approval does not edit a rule.
- Vulnerability and statutory-clock cases propose a human queue. The band cannot move them.
- The tests and the smoke evaluation do not call either harness.

## Cost and licensing

Copilot Credits are named for the GitHub Copilot harness and for the Customer Conversation harness. The standard-harness licence article was not opened. Nothing in this folder is a quote of a price, a credit rate, or an entitlement. Confirm the tenant's licence before anyone builds the agent.

## Microsoft Foundry

Optional. A short brief may be written from the JSON. The queue, the band, and the empty approval stay in the Python core. See [foundry.md](foundry.md). No Foundry resource is deployed in this folder.
