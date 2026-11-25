# Architecture

The runnable core is `src/classify.py`. Both Copilot Studio harnesses call it. Microsoft Foundry, if used, may only narrate JSON the core has already produced.

1. The caller passes one synthetic document and the date the question is about.
2. Caller-supplied taxonomy, routing table, and directory objects are compared with the pinned fixtures and are not applied.
3. Experiment 12 inventories the file and does not confirm it. Experiment 08 counts UK identifiers and does not describe the text as anonymised. Experiment 49 supplies a body marking and the marking rank. The file plan is not used.
4. The core proposes a class, evidence, a confidence, and a top alternative, or it leaves the class unset. It proposes a destination. It keeps an agent-held copy and its hash.
5. If the outcome is the human queue, the named reviewer records that they have seen the route. That updates the held hash. It does not stage the routing.
6. The named reviewer confirms the class and the destination for that held hash. Only then is a synthetic row written.
7. Filing, moving, deleting, and sending are not tools.

```text
pinned taxonomy, routing table, directory
        |
        v
either Copilot Studio harness
        |
        v
classify_document  ---- held copy and hash
        |
        +-- human queue --> record_route_seen (named reviewer)
        |
        v
record_routing_confirmation (same reviewer, same hash, same class, same destination)
        |
        v
synthetic staging row
        |
        x  file, move, delete, send
```

The rendered diagram is `architecture_diagram.png`.
