# Architecture

The core is `src/plan.py`. It does not call a model and it does not call the network. The same request, catalogue, framework, directory, and as-of date produce the same JSON.

```
goals + catalogue + framework + directory
        |
        v
  strip approval keys
  drop instruction sentences
  directory role and clearance only
        |
        +--> Experiment 58  fixed handbook question
        +--> Experiment 44  knowledge-base gap, not a course
        +--> Experiment 36  two figures, no chosen source
        |
        v
  sequenced steps, exclusions, budget as information
        |
        v
  human_approval is null
        |
        +--> employee record_approval(plan id)
        +--> manager record_approval(plan id)
        +--> adjustment seen, when the outcome requires it
        |
        v
  enrolment request JSON
  enrolled false, booked false, spent_gbp null
```

A wellbeing cue stops before a routine sequence. Approvals do not restart it.

The rendered picture is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `python docs/generate_diagram.py` if matplotlib is installed. The picture is not produced by the tests.

## What stays in Python

- Whether a phrase is affirmed, including a negation.
- The directory role, manager, and clearance.
- Review dates, costs, durations, and the budget comparison.
- The higher marking, the legal hold, and the retention labels.
- The plan id, and whether both approval objects match it.

## What a model may do later

A Microsoft Foundry deployment may turn the JSON into a short note. It may not add a course, change a cost, set `human_approval`, or decide an adjustment. See [foundry.md](foundry.md).

## Neighbours

Experiment 58 answers one fixed handbook question and does not decide an entitlement. Experiment 44 may report a content gap. That gap is not confirmed and is not copied in as a course. Experiment 36 classifies two figures. A material row is excluded. The agent does not write a correct value.
