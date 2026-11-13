# Architecture

The presenter supplies one synthetic pack and an as-of date. Either Copilot Studio harness calls `src/narrative.py`. The core calls Experiment 29 for `score_claim` and `passage_currency`, and Experiment 36 for `normalise_value` and `classify_values`. A local `.pptx` is built from the same JSON only after the presenter has approved the outline and every citation. Nothing is shared.

```
Presenter
  |
  | one synthetic pack, as-of date
  v
Copilot Studio (standard topic, or the skills layout)
  |
  v
src/narrative.py
  |-- Experiment 29 score_claim / passage_currency
  |-- Experiment 36 normalise_value / classify_values
  |
  v
JSON outline. human_approval is null. Slides are not produced.
  |
  v
Presenter approves the outline and every citation
  |
  v
Local .pptx, still not shared
```

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py`. Matplotlib is used only by that script. It is not a runtime dependency.

## Approval points

1. Prepare the outline. `human_approval` is null. `slides_produced` is false. This step has no external effect, and the presenter is still offered.
2. The presenter reads every claim, every citation, every gap, the accessibility checklist, and the markings. A safeguarding sentence is flagged for a person and is not a slide.
3. The presenter approves the outline and every citation, asks for a revision, or rejects it. Approval does not produce slides and does not share the deck.
4. `produce_slides()` writes a local file only after that record. `shared` stays false.
5. Publish, send, and share stay outside the agent.

## What is deterministic

The same pack and the same as-of date produce the same JSON. A claim is sourced only when the citation quote is the passage and Experiment 29 returns `supported`. A material figure discrepancy copies neither number. The request text is not stored on the result.
