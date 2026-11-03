# Architecture

Experiment 30 drafts regression cases. It does not merge them, push them, or edit the agent they describe.

```text
Maintainer
    |
    | one synthetic bundle, as-of date
    v
Either Copilot Studio harness
    |
    | same Python
    v
src/generate.py
    |-- strip result-shaped keys (src/injection.py)
    |-- read manifest flags (src/cases.py) — structural, not a schema sign-off
    |-- optional Experiment 03 skeleton, unapproved, only when asked
    |-- draft R1-R5, skip R6, leave R7 undrafted
    |-- render proposed-changes and draft pull-request text (src/render.py)
    |-- Foundry queries file, not uploaded (src/render.py, docs/foundry.md)
    v
JSON labelled DRAFT FOR MAINTAINER REVIEW
    |
    | maintainer approves tests
    | maintainer approves opening a pull request
    v
Outside this generator: the person edits, opens, pushes, or merges, or does not
```

The diagram is `docs/architecture_diagram.png`, drawn by `docs/generate_diagram.py`.

## What crosses a boundary

| From | To | What moves | What does not |
|---|---|---|---|
| Maintainer | Generator | One JSON bundle and an as-of date | A live agent definition, a credential, a Git remote |
| Generator | Maintainer | Draft cases, an index, pull-request text, a queries file | An approval, an open pull request, a Foundry score |
| Generator | Experiment 03 | A skeleton request, and only when the bundle asks and no manifest was supplied | An approve flag that is honoured, autonomy A3 |
| Generator | Disk | Files under `--out-dir`, when that directory is not the agent path | A write into the agent under test |

## Counts

`drafted` plus `skipped_duplicate` equals `considered`. Observations that were not drafted are a separate count. Foundry query lines equal `drafted`, not `considered`. The smoke test uses `passed`, `failed`, and `errored` as three disjoint buckets.

## Human approval

The generator stops at the draft. Approving tests, opening a pull request, merging, pushing, editing the agent, and running a Foundry evaluation are decisions for a person. The manifest lists them. The code refuses the matching flags.
