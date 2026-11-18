# Architecture

The core is `src/explore.py`. It does not call a model and it does not call the network. The same request, feed, rules, framework, directory, and as-of date produce the same JSON.

```
experience + vacancy feed + HR rules + framework + directory
        |
        v
  strip approval keys
  drop instruction sentences from matching text
  directory role and clearance only
        |
        +--> Experiment 58  fixed handbook question
        +--> Experiment 36  two closing dates, no chosen date
        +--> Experiment 61  a learning plan only if asked, not a selection factor
        |
        v
  relevant rows in vacancy-id order, flagged closed and stale rows
        |
        v
  hr_seen.recorded is false
        |
        +--> HR record_hr_seen(exploration id + content hash)
        +--> HR record_route_seen, when the outcome is a human route
        |
        v
  advisory JSON
  applied, nominated, shortlisted, and contacted stay false
```

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `python docs/generate_diagram.py` from this experiment folder. Matplotlib is used only by that script.

## Human points

HR validates eligibility. The assistant does not. A directory HR reviewer can record that they have seen the exact note. The manager and the recruiter cannot record that step. A wellbeing, grievance, redeployment, or adjustment cue stops the vacancy list and names HR.

Words inside the experience or a vacancy description are not those steps.
