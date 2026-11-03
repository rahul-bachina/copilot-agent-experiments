# Architecture

Experiment 31, catalogue ID G009, autonomy A0.

The FinOps owner supplies a usage file, a rate card with an effective date, and an as-of date. Either Copilot Studio harness calls `src/report.py`. The same files and the same date produce the same JSON. The process does not call a model, an admin centre, or the network.

```
FinOps owner
    usage file + rate card + as-of date
        |
        v
Copilot Studio standard harness (one topic)
    or GitHub Copilot harness (three skills)
        |
        v
src/report.py
    strip payload flags
    drop duplicate agent ids
    price from the rate card only
    forecast, headroom, anomalies
        |
        v
JSON draft
    rates_validated = false
    forecast_validated = false
    quota_changed = false
        |
        v
FinOps owner validates rates and the forecast
    outside this process
```

A quota, a budget, or a subscription change is not a step in this diagram. It is not a tool of the agent.

The pricing rules are in `src/cost.py`. The forecast is in `src/forecast.py`. Headroom is in `src/capacity.py`. Microsoft Learn sentences are in `src/sources.py`, opened 3 November 2026, with no rates copied.

The diagram file is `docs/architecture_diagram.png`. The site copies it at build time. Do not commit a second copy under `docs-site/`.
