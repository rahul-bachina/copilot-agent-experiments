# Which harness

Both harnesses call the same Python core, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 12 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The harness overview says the GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. It says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement. The page also says the harness shares underlying technology and SDK components with GitHub Copilot.

These were not opened on 12 November 2026:

- Usage-based billing
- The billing overview for agents powered by the GitHub Copilot harness
- Licensing for agents powered by the standard harness
- The skills overview, and the page for adding an uploaded skill
- The Customer Conversation harness article linked from the overview
- Compare Copilot Studio agent harnesses, beyond the table on the overview itself
- Microsoft 365 Copilot licensing

No price is stated on the overview. This note does not invent one. The overview did not use the word preview for the three harnesses on the page that was read. That is not a general-availability claim for the authoring click-path, which was not exercised in a tenant.

## When to use the standard harness

Use it when every invitation goes through the same topic: paste the JSON, run `draft_proposal`, show the matrix, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. Files, skills, and memory are "not a focus". An author who pastes one pack and needs the cited draft back is that shape. The guide is `copilot-studio/README.md`. There is no skill on that path. Billing for the standard harness is on a licensing page that was not opened. This is not a licence opinion.

## When to use the GitHub Copilot harness

Use it when an author wants to work through one awkward pack: run the core, then ask which source was refused, which figure was withheld, or why an acceptance did not submit.

Microsoft's overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. The overview says that. It does not state a price. This experiment's Word file is built by `src/word_draft.py`. The skills tell the agent to call the core and to stop. They do not tell it to upload the file. The harness file-creation feature was not exercised in a tenant.

Each skill says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, including contact centres, with a route to a human representative. Agents on it use Copilot Credits. Publishing, on the comparison table, is "Website chat or a phone number".

This starter does not implement that harness. The detail beyond the overview is unverified in this folder. An unattended sender that submits a bid would sit outside this A1 design. The author accepts the draft. The human route in this starter is a sentence and an acceptance record, not a tool call on that harness.

## Copilot in Word

A dedicated Copilot in Word product overview was not opened. What was opened:

- The [Current Channel release notes](https://learn.microsoft.com/en-us/OfficeUpdates/current-channel). Version 2602 (Build 19725.20172), dated 10 March on that page, says Agent mode in Word adds a conversational chat that helps create, edit, and refine document content, and that natural-language requests can draft text and rewrite sections. The same page mentions Draft with Copilot in resolved issues. Behaviour of those features was not checked in a tenant.
- The training module [Draft impactful documents using AI](https://learn.microsoft.com/en-us/training/modules/draft-impactful-documents-using-ai/). It says the module covers drafting with Copilot in Word from referenced files, emails, and meetings. A training module is not a product contract.
- [Word.Body.insertParagraph](https://learn.microsoft.com/en-us/javascript/api/word/word.body?view=word-js-preview), API set WordApi 1.1. This starter does not call it.
- [Graph driveItem upload](https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0). `PUT` content uploads a file of up to 250 MB. The least-privileged delegated permission named on the page is `Files.ReadWrite`. The page's example is a text file, and it says `Content-Type: text/plain` is required. It does not describe editing a Word paragraph. This starter does not call Graph.

Work IQ is named in the catalogue row for M004. The Work IQ pages were not opened for this experiment. Nothing here is a claim about Work IQ.

## What is the same on both shipped harnesses

- `src/proposal.py` decides the citations, the gaps, the withheld figures, and the empty approval.
- `screen_tone()` and `screen_plain_english()` from Experiment 43 run on a quoted body.
- `line_applicability()` from Experiment 09 decides whether an entry may be cited.
- `score_claim()` from Experiment 29 decides whether the quote is supported.
- `normalise_value()` and `classify_values()` from Experiment 36 compare price placeholders. The figures are not copied out.
- `agent-manifest.yaml` is the permission boundary. `permissions.yaml` is the same file.
- Writes are disabled. Sends are disabled.
- An author's acceptance of the complete draft does not submit it.
- The tests and the smoke evaluation do not call either harness.

## Cost and licensing

Copilot Credits are named for the GitHub Copilot harness and for the Customer Conversation harness. The standard-harness licence article was not opened. Nothing in this folder is a quote of a price, a credit rate, or an entitlement. Confirm the tenant's licence before anyone builds the agent.
