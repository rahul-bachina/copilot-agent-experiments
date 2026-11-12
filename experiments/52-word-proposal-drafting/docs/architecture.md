# Architecture

The author supplies one synthetic invitation and an as-of date. Either Copilot Studio harness calls `src/proposal.py`. The core calls Experiment 43 for the tone and plain-English screens, Experiment 09 for the citation gate Experiment 43 already uses, Experiment 29 for `score_claim`, and Experiment 36 to compare price placeholders. A local `.docx` is built from the same JSON. Nothing is submitted.

```
Author
  |
  | one synthetic pack, as-of date
  v
Copilot Studio (standard topic, or GitHub Copilot harness skills)
  |
  v
src/proposal.py
  |-- Experiment 43 screen_tone / screen_plain_english
  |-- Experiment 09 line_applicability
  |-- Experiment 29 score_claim / passage_currency
  |-- Experiment 36 normalise_value / classify_values
  |
  v
JSON matrix + optional local .docx
  |
  v
Author accepts the complete draft  -->  still not submitted
```

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py`. Matplotlib is used only by that script. It is not a runtime dependency.

## Approval points

1. Prepare the draft. `human_approval` is null. This step has no external effect, and the author is still offered.
2. The author reads every row, including gaps, withheld prices, and anything that was not marked met.
3. The author accepts the complete draft, asks for a revision, or rejects it. Acceptance does not submit.
4. Submit, send, and upload stay outside the agent.

## What is deterministic

The same pack and the same as-of date produce the same JSON. A requirement is marked met only when the quote is the library body and Experiment 29 returns `supported`, and the entry is a plain capability. Price figures are compared and then withheld. The requirement text is not stored on the result.
