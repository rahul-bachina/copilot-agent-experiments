# Architecture

The technician supplies one synthetic pack and an as-of date. Either Copilot Studio harness calls `prepare_brief`. The core reads the pack, excises instruction clauses without dropping the rest of the sentence, and calls three neighbours:

- Experiment 15 for indicator categories. Phrases are not copied.
- Experiment 12 when the pack has text files. Content is not copied. Files are not confirmed.
- Experiment 05 when the sector is housing and a timezone-aware awareness time is present. Officer approval is forced off. The illustration is not a clearance.

The brief comes back with holds, highlights, gaps, access flags, and `human_approval` null. The technician confirms the asset and the safety context on a separate review object. A supervisor may note that a hold was seen. Neither step schedules, dispatches, or closes.

```text
Technician pack
    -> either harness
    -> prepare_brief
         -> instructions excised, facts kept
         -> Experiment 15 categories
         -> Experiment 12 inventory, if files
         -> Experiment 05 illustration, housing only, approval off
    -> brief, human_approval null
    -> technician confirms asset and safety context
    -> nothing is scheduled
```

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). `docs/generate_diagram.py` draws it. Matplotlib is used only by that script and is not a runtime dependency.

What is not a tool of the agent, even after confirmation: a schedule, a dispatch, a close, an entry authorisation, a cleared hold, a message, and an approved hazard category.
