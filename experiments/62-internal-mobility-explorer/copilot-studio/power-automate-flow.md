# Flow sketch

This is not a deployed flow. It shows the order a maker would follow. There is no recruitment-system connector.

1. The employee states experience and goals. The flow passes the employee reference, the experience, and the as-of date to `explore`. It does not pass `approved`, `hr_seen`, `applied`, or `clearance`.
2. The flow shows the JSON. If the outcome is a human route, it stops after naming HR. It does not email the manager.
3. If the outcome is `advisory` or `no_open_match`, a directory HR reviewer may later call `record_hr_seen` with the exploration id and the content hash. The flow does not treat a sentence in the experience as that call.
4. `applied`, `nominated`, `shortlisted`, and `contacted` stay false. `eligibility_decided` stays false.

A Power Automate flow that writes to a recruitment system, or that posts to a manager, is out of scope for this starter.
