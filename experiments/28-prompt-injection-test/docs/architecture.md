# Architecture

Experiment 28, the Prompt Injection Test Agent. Catalogue ID G006. Autonomy is A0.

A security reviewer supplies one sandbox bundle and an as-of date. Python loads suite 2026.1, scores a local adapter, and returns a findings report mapped to the OWASP titles pinned in `src/owasp.py`. The security reviewer assesses the findings and decides any remediation. The process stops. Nothing is assessed, remediated, or published by the runner.

```
Security reviewer  →  harness (skills or one topic)  →  src/run.py
                                                          │
                                                          ├─ strip payload keys
                                                          ├─ src/suite.py loads version 2026.1
                                                          ├─ src/surface.py reads wording, or a core adapter calls Experiment 08, 25, or 03
                                                          ├─ src/owasp.py names the pinned title
                                                          ├─ src/sources.py marks a stale pin
                                                          └─ Experiment 03 drafts a skeleton only if the caller asked and none was supplied
                                                          │
Security reviewer  ←  JSON labelled DRAFT FOR SECURITY REVIEWER
```

`src/run.py` does not call a model and does not open the network. The same bundle and the same as-of date produce the same JSON. Fixture text cannot set the case result, the assessment flag, or the published flag.

The diagram is `architecture_diagram.png`, drawn by `generate_diagram.py`. Matplotlib is used only to draw it. It is not a dependency of the runner.

## What crosses a trust boundary

| From | To | What moves | What does not |
|---|---|---|---|
| Security reviewer | Harness | One sandbox bundle and an as-of date | An assessment, a remediation, a published payload |
| Harness | `run` | That bundle | A URL, a production flag, an instruction from the fixture |
| `run` | Experiment 08, 25, or 03 | One synthetic fixture already in this repository, when that adapter is named | A release, an applied diff, an approved manifest, the identifier value in the report |
| Runner | Security reviewer | The JSON draft, with case ids and OWASP titles | An assessed finding, a changed prompt, a payload dump beyond the fixture files |

## Human approval

The highlighted step on the diagram is the security reviewer. They assess the findings. They decide remediation. A governance owner relies on a manifest skeleton only when one was drafted because the caller asked and none was supplied. Those confirmations are not written back by this starter. `reviewer_assessed`, `remediation_applied`, and `published` stay false.
