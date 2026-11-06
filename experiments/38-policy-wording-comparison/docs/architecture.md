# Architecture

The runnable core is `src/compare.py`. It is deterministic. The same pack, the same as-of date, and the same window produce the same JSON.

```
specialist pack
    -> strip decision keys
    -> Experiment 12 inventory (no purpose, no routing)
    -> drop stale, unread, and identifier-bearing files
    -> copy clauses whose topic and subject are in the closed lists
    -> Experiment 33 span check and Experiment 29 number check
    -> side-by-side row, or "not stated"
    -> stop for the wording specialist
```

A topic that appears in one wording and not another is a `not_stated_in_one` row. The absent cell is the words `not stated`, with `inferred` false and no citation. That class means the normalised texts are not the same, or one wording has no usable clause for that caller-supplied subject. It is not a finding that the difference changes cover, and it is not a finding that one wording is more favourable.

If every document on a wording was withheld or stale, the cell is `not_quoted` rather than `not_stated`. Silence is not inferred from a document the checker refused to read.

Azure Document Intelligence is described in [foundry.md](foundry.md). It is not called. The caller supplies lines that are already split.

The diagram is [architecture_diagram.png](architecture_diagram.png).
