# Architecture

Policy Q&A for NHS and public-sector corporate services, Experiment 06. Catalogue ID M003.

The policy owner approves sources. The register quotes, refuses, or says "I don't know". Nothing is published and nothing is sent.

![Architecture diagram titled Policy Q&A, NHS corporate services. A member of staff asks one question. The Python register quotes an approved in-date clause with its review date, or says I don't know, or refuses a clinical question. The policy owner approves sources and any change note. A separate box states what is not a tool: no clinical advice, no entitlement decision, no publish, no send, and no spend.](architecture_diagram.png)

```mermaid
flowchart TD
    A["1. Staff member asks one corporate question and supplies the as-of date"] --> B["2. Register: approved, in-date clauses only"]
    B --> C["3. Quotation with version and review date, or I don't know, or a refusal"]
    C --> D["4. Human: the person decides whether to rely on a quotation"]
    E["Policy owner approves a document before it can be quoted"] --> B
    F["Policy owner review: coverage, conflicts, stale policies, draft change note"] --> G["5. Human: policy owner accepts a change note outside the agent"]
    B --> F
```

Step 4 and step 5 are the human approvals. Publishing, sending, and clinical advice stay outside the agent even after someone has read the draft.

## Two harnesses, one register

The standard harness is the lead path for staff. It is one topic and one action: `src/answer.py`. The GitHub Copilot harness is for the policy owner. It calls `src/review.py` through three skills. The comparison is in [harness-comparison.md](harness-comparison.md).

A SharePoint library is not a knowledge source. The approved export is. Connecting generative answers to the whole library would bypass the approval flag and the review date.

## Modules

| Module | Role |
| --- | --- |
| `src/corpus.py` | Load the register. Quarantine instructing clauses. Apply the owner-approval and review-date rules. |
| `src/answer.py` | One staff question. Quotation, refusal, conflict, stale withholding, or "I don't know". |
| `src/review.py` | Coverage, stale policies, conflicts, and draft change notes. |
| `src/time_saving.py` | Score paired timestamps. Reject self-reported minutes. Exclude ungrounded items. |
| `fixtures/policies.json` | Synthetic Northmere policies. Fictional trust. |

`eval/evaluate.py` runs the matcher on 28 synthetic questions and scores the time-saving fixture. The agreement rate is a pipeline check. The median is fixture arithmetic.
