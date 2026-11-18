# Architecture

Experiment 63, catalogue ID H006, autonomy A0. The explanation is `src/explain.py`. The same inputs produce the same JSON. Nothing is downloaded when it runs.

```
HR scope object (directory-checked)        the question, untrusted
        |                                      |
        v                                      v
synthetic policy set + statutory snapshot --> src/explain.py
        |                                      |
        |                                      +--> Experiment 58 handbook helpers
        |                                      |    (version dates, negation, markings, mask)
        |                                      +--> Experiment 58 answer, one fixed question
        |                                      +--> Experiment 08 propose(), counts only
        |                                      +--> Experiment 03 manifest validator
        v
JSON: policy section, effective date, statutory source, or a human route
entitlement_decision, pay_decision, and pay_rate stay empty
leave_booked and leave_recorded stay false
```

HR approves document ids on the scope object before a question is answered. The approver id has to be an active HR id on the synthetic directory. A role typed into the question is not that check.

The date on the question selects the version. A version that has ended by the as-of date is still quoted when the question is about a day inside its window, and the result says it is superseded. A review date before the day asked about is flagged. A date that cannot be read is not replaced with today.

A denial in a policy sentence is not an inclusion. Instruction sentences are recorded and not quoted. A cover marked SECRET is not copied. The higher marking wins. A legal hold and every retention label are kept.

Statutory rows are the pins in `src/sources.py`, opened on 18 November 2026. The snapshot in `fixtures/baseline.json` has to match those quotes. A disagreement states no figure. An unopened page, including statutory sick pay, has no quote and no rate.

A seen-step is a separate object. It has to come from the deterministic approval step, name an active HR id, and carry the hash of that explanation. It records that HR has seen the explanation. It does not approve leave.

`decide_entitlement`, `book_leave`, `record_leave`, `calculate_pay`, and `approve_policy` raise.

The rendered diagram is [architecture_diagram.png](architecture_diagram.png).
