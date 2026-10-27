# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. Microsoft's harness overview, opened 27 October 2026, says it is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic. A last-updated date was not in the text retrieved for this experiment.

It is the path for a KYC reviewer who drops in one customer file and then asks follow-up questions: which comment held an instruction, why a date is stale, why a PEP phrase is not a rating. The standard harness is the fixed topic. Both call `src/review.py`.

The overview says this harness can take a goal, break it into steps, call tools, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. The harness section says agents on this harness use Copilot Credits. The comparison table points at a separate billing overview. That article was not opened on 27 October 2026. No price is copied here. Whether a Microsoft 365 Copilot licence covers this harness was not on the overview page. Treat that as unverified.

The overview did not use the word preview for the harness itself. The skills-upload article was not opened on 27 October 2026. Treat the authoring click-path as something to confirm in the tenant.

## Skills

Two skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent.

| Skill | Calls | Stops |
|---|---|---|
| `review-kyc-file` | `review()` in `src/review.py` | When the JSON is shown. `documents_confirmed` and `purpose_confirmed` are false. `final_risk_rating` is null. |
| `explain-kyc-checklist` | No second checklist and no second redactor. It reads the JSON. | When the explanation is tied to fields that are already there. |

The tool `review_kyc_file` has no side effect. There is no tool that confirms the documents, approves a customer, assigns a rating, files a report, or sends the customer note. Do not add one. Do not call `record_reviewer_confirmation`. That function exists for tests. It is not an agent tool, and it still does not approve the customer.

## What the reviewer sees

1. Injection signals, including where the phrase was hidden, before the checklist rows.
2. Unread, empty, oversized, and checksum-failed files.
3. Stale, missing, future, and invalid document dates, and whether the pinned sources are stale.
4. What is evidenced, what is missing, and which regulation 33 phrases were found. `sufficient` is false. `final_risk_rating` is null.
5. The customer note, with `hints_at_suspicion` false, and a line that it was not sent.
6. A line that nothing was confirmed, approved, rated, filed, or sent.

A sandbox file `draft-kyc-checklist.json` is the tool JSON. It is not an approval. The KYC reviewer confirms the documents and the purpose outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 27 October 2026. The skills say not to store the file text, the identifiers, or the screening note. Assume memory is a risk and do not use it.

## What this note does not verify

- Credit amounts, monthly limits, or a preview label. The billing article linked from the overview was not opened on 27 October 2026. The overview text retrieved for this experiment did not call the harness preview.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A DLP policy is a deployment control. It is not applied here.
- The Customer Conversation harness. It is for customer voice and chat. This experiment does not use it. The user is a KYC reviewer. A customer chatting with the checklist would be a different product.
