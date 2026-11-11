# Architecture

The pack is one Python function, `prepare_pack`, with a second function, `record_review`, for the analyst's confirmation. Both harnesses call those functions. Neither publishes.

```
Analyst supplies one synthetic batch and an as-of date
        |
        v
Either harness (standard topic, or GitHub Copilot harness skills)
        |
        v
prepare_pack
        |-- Experiment 08 propose() on each text (no reversible map)
        |-- Experiment 07 cluster_responses() and wilson_interval()
        |-- Experiment 20 classify() for an in-frame financial-services complaint
        |
        v
JSON pack. ready is false. human_approval is null.
        |
        v
Analyst confirms the sample frame and the limitations on a separate review object
        |
        v
ready may become true. published stays false. No customer is contacted.
```

The diagram in this folder is `architecture_diagram.png`. It is copied into the briefing site at build time. Do not commit a second copy under `docs-site/`.

Counts use unique voices. A duplicate is listed under `not_counted_as_extra_voices` and is not added to the denominator. Theme counts overlap and are not a second population. The Wilson interval is a property of one proportion in this sample. It is not a model score and not a finding that PRIN 2A.5 or PRIN 2A.6 was met.

A public-service batch skips Experiment 20 and does not quote PRIN as a duty of the pack. UK GDPR Article 4 and Article 5 quotations still apply to that path, until the as-of date makes every quotation stale.
