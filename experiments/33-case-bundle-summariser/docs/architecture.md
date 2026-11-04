# Architecture

Experiment 33, the evidence and case-bundle summariser. Catalogue ID UK09. Autonomy is A0.

The decision-maker supplies one synthetic bundle, the fact keys they want read, and an as-of date. Either Copilot Studio harness calls `summarise()`. The Python core drops injection lines and payload keys, copies contiguous lines from current documents, and gives each shown sentence one verdict against the cited span. The draft comes back with `case_outcome`, `disclosure_decision`, and `credibility_finding` null, and `summary_accepted_as_reading_aid` false.

```text
Decision-maker
    -> either harness
        -> src/summarise.py
            -> src/citations.py     one verdict per sentence
            -> src/injection.py     instructions recorded, not followed
            -> src/sources.py       pins opened 4 November 2026
    -> DRAFT FOR THE DECISION-MAKER. NOT A DECISION.
Decision-maker reviews every cited sentence, outside this tool
Decision-maker decides any outcome, disclosure, or credibility, outside this tool
```

## What is not a tool

Recommending an outcome, making a disclosure decision, making a credibility finding, accepting the summary, calling Microsoft Foundry, writing a production record, sending, and autonomy A3. `schema/tools.json` marks those functions as not callable, except `record_sentence_review`, which is not an agent tool and is not on the command line. The prohibited functions raise `SummaryForbidden`.

## How this differs from Experiment 18 and Experiment 29

Experiment 18 indexes items. It does not write a sentence about what a document says. Experiment 29 scores someone else's claims, and a shared word can be enough. This experiment copies lines and requires the sentence to be a contiguous part of the cited span. It does not import either experiment.

## Diagram

`docs/architecture_diagram.png` is drawn by `docs/generate_diagram.py`. The briefing site copies that file at build time. Do not commit a second copy under `docs-site/`.
