# Architecture

The draft is `src/guide.py`. The same pack, directory, scope, request, and as-of date produce the same JSON. `human_approval` stays null until `approve_checklist()` is called with a separate object for the directory line manager and the exact item digest.

```
HR scope + directory + request + as-of
        |
        v
src/guide.py
        |-- handbook.py (Experiment 58) for negation, dates, and the higher marking
        |-- Experiment 08 propose() counts identifiers; the redacted text is not copied
        |-- Experiment 15 find_phrases(); the phrase text is not stored
        |-- Experiment 11 dates, not re-opened here; compliance_conclusion stays null
        |-- Experiment 21 triage() on a fixed "service desk hours" question
        |-- Experiment 58 answer_handbook() on a fixed leave question, when asked
        |-- Experiment 57 prepare_onboarding() for the office role; applied stays false
        v
Draft JSON. Proposals are not executed.
        |
        v
approve_checklist()  -- only a separate manager object, exact digest
        |
        v
share_checklist()    -- in-memory receipt. No email. No HR write.
```

A sentence in the request does not enter the issued-approval set. A copied approval for a different digest does not share.

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `python docs/generate_diagram.py` from this experiment, after installing Matplotlib. Matplotlib is not a runtime dependency.
