# Architecture

The explainer reads one synthetic plan, one approved rules table, one question, and an as-of date. It returns one JSON document. The same inputs return the same JSON.

```
adviser supplies plan, table, question, as-of
        |
        v
either Copilot Studio harness
        |
        v
src/explainer.py
  drop prohibited payload keys
  record instruction spans and keep the surrounding words
  match at most one approved rule
  Experiment 38 normalise() checks the clause
        |
        +-- one supported current rule --> explanation of the table
        |                                  human_approval stays null
        |                                  a person is still offered
        |
        +-- dispute, ambiguity, conflict, gap, stale, or conditional
                                           --> route to a person
                                               no position is stated
        |
        v
entitlement owner may record a decision code
the code is not applied to a record
grant, refuse, change, send, and write are not tools
```

## Human approval points

1. Tell the customer that the draft is the organisation's position. The JSON is a draft. The agent does not send it.
2. Decide a disputed, ambiguous, conditional, conflicting, or stale entitlement. The agent routes these and does not state a position.
3. Grant, refuse, or change the entitlement on the organisation's system. Those functions raise. A recorded code does not do them.
4. Confirm a lawful basis before any live plan is processed. Article 6 was not opened. The manifest does not choose a basis.

## What is cited

A stated position repeats the rule's approved plain-English sentence and quotes the clause. Experiment 38's `normalise()` requires the support phrase to be a contiguous part of that clause after case and whitespace are folded. A paraphrase fails. A conflict marker routes the question and clears the position.

Experiment 40 is not imported. The human route follows its shape: always offered, a non-digital counter, and a telephone number that is not live.

## Diagram

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py`. Matplotlib is used only by that script. It is not a runtime dependency.
