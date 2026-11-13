# Architecture

The finder is one Python function, `find_documents`, in `src/find.py`. Either Copilot Studio harness calls it. Microsoft Foundry, if used, only narrates the JSON.

```
Requesting user                Either harness                 Python core
confirm locations        -->   standard topics, or      -->   filter locations,
and a find request             Microsoft Copilot harness      principals, clearance
                               (skills in this folder)        then rank
                                                                  |
                                                                  v
                               JSON result  <---------------  Experiments 49, 50, 08
                               human_approval null            admitted files only
                                                                  |
                                                                  v
                               Human acknowledgement        no Graph, no file change
```

The diagram in `architecture_diagram.png` is the same flow, with the human steps highlighted.

## What crosses the boundary

| Crosses | Does not cross |
|---|---|
| Confirmed location ids, principals, fixture clearance | A location id that was only inside a file |
| Title, date, label, reason, short masked snippet for an admitted hit | Title or extract of a withheld file |
| Withheld counts | Hidden file ids |
| Legal hold and retention label on an admitted hit | An instruction to delete or to search everywhere |

Experiment 49 is called on the matching text of an admitted file. Experiment 50 is called on those same files for duplicate proposal ids. Experiment 08 is called on the original extract so an identifier still counts after a negated sentence is cut. None of those calls is a network call.

## Determinism

The same index, request, selection, and as-of date produce the same JSON. Ranks are a sort, not a model score. `eval/evaluate.py` checks 18 synthetic cases and counts each case once.
