# Architecture

The knowledge manager confirms gaps. The agent prepares a review of one synthetic pack against the approved articles. It does not publish.

```
Knowledge manager
    |
    | one synthetic pack, one as-of date
    v
Either Copilot Studio harness
    |
    | same call
    v
src/gaps.py
    |-- Experiment 08 propose()          counts identifiers, does not copy the redacted text
    |-- Experiment 21 is_stale()         last_reviewed window for this starter's articles
    |-- Experiment 21 match_articles()   only when the sector is it_service; ids only
    |-- Experiment 40 match_articles()   public, financial, energy, telecoms; ids only
    v
JSON review
    human_approval is null
    published is false
    outlines are drafts
    v
Knowledge manager
    confirm_gap, reject_gap, or defer
    confirmation does not publish
```

Publishing, editing, deleting, sending, and choosing a winner are not tools of the agent. They stay outside it after confirmation.

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `python docs/generate_diagram.py` from this experiment. Matplotlib is used only for that script. It is not a runtime dependency.

## What is deterministic

Gap ids, retrieval misses, stale and withdrawn articles, conflicts, the plain-English screen, the accessibility flag, and the empty approval are computed in Python. A later Microsoft Foundry brief may restate fields that are already in the JSON. It must not add an article body or a publish.

## What is reused

- Experiment 08 is the identifier gateway. This folder does not carry a second copy.
- Experiment 21's `is_stale()` is the window on `last_reviewed`. Its `match_articles()` is called for an IT pack.
- Experiment 40's `match_articles()` is called for the sectors that catalogue already knows.

A related catalogue id is evidence. It does not close a gap in the approved base, and the body is not copied.
