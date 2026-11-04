# Architecture

Experiment 34, catalogue ID UK10, autonomy A1.

The caseworker supplies a synthetic advice bundle and an as-of date. Either Copilot Studio harness calls `src/assemble.py`. The same bundle and the same date produce the same JSON. The process does not call a model or the network. It calls Experiment 08 only to test paragraph text for identifier patterns, and it does not copy a paragraph that matches.

```
Caseworker
    synthetic advice bundle + as-of date
        |
        v
Copilot Studio standard harness (one topic)
    or GitHub Copilot harness (three skills)
        |
        v
src/assemble.py
    refuse a bundle that is not synthetic
    strip payload keys
    call Experiment 08 propose, model suggestions off
    file a paragraph only under its own section tag
    withhold section I
    flag gaps, conflicts, unsupported statements, stale advice
        |
        v
JSON draft
    needs_decided = false
    placement_decided = false
    export_blocked = true
        |
        v
Caseworker authors the final text
    and checks the local template
        |
        v
Optional local copy, only if the sign-off object passes
    still not sent
```

Sending the plan, naming a placement, and writing the local authority system are not steps in this diagram. They are not tools of the agent.

Section letters are in `src/sections.py`. The gate and the filing are in `src/assemble.py`. Pages opened on 4 November 2026 are in `src/sources.py`.

The diagram file is `docs/architecture_diagram.png`. The site copies it at build time. Do not commit a second copy under `docs-site/`.
