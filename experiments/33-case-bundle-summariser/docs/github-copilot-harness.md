# GitHub Copilot harness

This is the Copilot Studio **GitHub Copilot harness**. The harness overview, opened 4 November 2026, says it is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The same page says customer data is not sent to or processed by the GitHub Copilot service when the agent runs in Copilot Studio. That is Microsoft's statement. This repository cannot see a tenant's traffic.

It is the path for a decision-maker who drops in one synthetic bundle and then asks a follow-up: which sentence failed, which line did not contain the words, which fact key was missing. The standard harness is the fixed topic. Both call `src/summarise.py`.

The overview says this harness can take a goal, break it into steps, call tools across connectors, knowledge, MCP, and connected agents, create and edit Word, Excel, PowerPoint, and PDF files, and use skills and memory. Each task runs in a sandbox governed by Copilot Studio. Agents on this harness use Copilot Credits. No quantity is copied. File creation is a capability of the harness. This experiment's skills may write a draft JSON in the sandbox. They do not recommend an outcome and they do not make a disclosure decision.

The overview does not mark this harness as preview. A comparison page that describes maturity, latency, and a Bash container was not opened for this experiment, so those claims are not copied.

Billing and licensing pages were not opened on 4 November 2026. No price is copied. Holding only the GitHub Copilot service does not, on the overview, make this harness available. The overview says the harness is a Copilot Studio framework.

Generative orchestration on this harness selects from the skill description. This starter does not assign routing weights and does not use classic-orchestration trigger phrases.

## Skills

Three skills, under `skills/`. Upload each folder, or the `SKILL.md`, as the tenant's current screen requires. Do not upload them onto a standard-harness agent. A skills-upload article was not opened on 4 November 2026. Treat the click-path as something to confirm in the tenant.

| Skill | Calls | Stops |
|---|---|---|
| `extract-cited-summary` | `summarise()` in `src/summarise.py`, with no proposed sentences | When the JSON is shown. The sentences have not been reviewed. |
| `check-pinpoint-citations` | `summarise()` with `proposed_sentences` | When each verdict is shown. The draft is not accepted. |
| `list-gaps-and-contradictions` | No second writer. It reads the JSON. | When the gaps and contradictions are shown and `contradiction_resolved` is still false. |

The tools `extract_cited_summary`, `check_pinpoint_citations`, and `list_gaps_and_contradictions` have no side effect. There is no tool that recommends an outcome, makes a disclosure decision, finds credibility, accepts the summary, calls Foundry, or sends. `record_sentence_review` is not an agent tool. Do not add one.

## What the decision-maker sees

1. Injection and unused-document flags, before the sentence table.
2. One row per sentence, with document id, page, paragraph, and line range. `verdict_total` equals `sentence_count`. `other_failures` are on the row and are not in the total.
3. `gap_count`, `contradiction_count`, and `not_used_count` on their own lines. They are not added to `verdict_total`.
4. `checker_passed` and `do_not_rely` as separate flags. A passed checker can still say not to rely on the draft.
5. Approval points, including the decision-maker reviewing every cited sentence.

A sandbox file `draft-case-reading.json` is the tool JSON. It is not an accepted reading and it is not a case decision. The decision-maker's review is made outside the agent.

## Memory

The overview says the harness supports memory. An administrator control to turn memory off was not found on the page opened on 4 November 2026. The skills say not to store the bundle, the sentences, or the draft. Assume memory is a risk and do not use it for case text.

## What this note does not verify

- Credit amounts, monthly limits, or a billing-rates table. Those pages were not opened.
- That a sandbox file cannot be exfiltrated by a connector someone adds later. The manifest forbids that connector. A Data Loss Prevention policy is a deployment control. It was not opened for this experiment.
- The Customer Conversation harness. The overview describes it for customer voice and chat. This experiment does not use it to read a case bundle.
