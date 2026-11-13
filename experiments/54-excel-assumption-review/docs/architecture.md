# Architecture

The model owner confirms one synthetic workbook. Either Copilot Studio harness calls `src/review.py`. The core does not call a model and does not call the network.

```text
Model owner
    |  separate confirmation: workbook, ranges, formulas
    v
Copilot Studio
    |  standard topic, or the three skills
    v
src/review.py
    |-- formulas.py          closed reader and 1 percent shock
    |-- Experiment 36        paired values, neither side chosen
    |-- Experiment 08        identifier types, text not copied
    |-- Experiment 15        safeguarding stop
    |-- Experiment 30        draft regression cases, not merged
    v
JSON report
    |  findings_accepted is null
    v
Model owner reads it. The workbook is not edited.
```

A safeguarding phrase stops the path before the inventory. A stale pin stops it before findings. A missing confirmation stops it before any range is inspected.

The picture is `docs/architecture_diagram.png`, drawn by `docs/generate_diagram.py`. The docs site copies that file at build time.
