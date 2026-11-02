# Architecture

Experiment 26, the Skill Selection Evaluator. Catalogue ID G004. Autonomy of the evaluator is A0.

The maintainer supplies skill or topic metadata and a labelled set of utterances. Either Copilot Studio harness calls `src/report.py`. The report is a draft. The maintainer validates routing tests. The evaluator does not edit a skill and does not deploy.

```
Maintainer
  skills, topics, labelled utterances, as-of date
        |
        v
Either harness (standard topic, or three skills)
        |
        v
src/report.py
  router, precision and recall, confusable pairs
  Experiment 25 on each skill file
  Experiment 14 when a use case is present
  Experiment 03 skeleton when no manifest is present
        |
        v
Draft JSON. diff_applied is false. maintainer_validated is false.
        |
        v
Maintainer validates routing tests
        |
        v
Maintainer edits a skill outside this tool, or does not
```

The diagram is `docs/architecture_diagram.png`. Regenerate it with `docs/generate_diagram.py` if the boxes change. Matplotlib is used only by that script. It is not a test dependency.

## What is not a tool

An applied diff, an edited skill, a validated test suite, an approved manifest, a selected platform, a deployment, a production write, and a send. Those stay outside the evaluator even after the maintainer accepts a finding.
