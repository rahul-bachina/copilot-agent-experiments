# Power Automate note

A build note. This folder does not contain an importable solution.

The flow accepts the pack and the as-of date, runs `prepare_brief`, and returns the JSON to the topic. It does not write a Dataverse row. It does not call a scheduling connector. It does not send mail or an SMS.

A second flow may accept a review object that the technician typed into fields, not into the work-order narrative, and call `record_review`. That flow still does not schedule. If the decision is anything other than the three decisions in `schema/review_tool.schema.json`, the core refuses it.

Product click-paths for Power Automate and for Dynamics 365 Field Service were not opened on 10 November 2026. Treat connector names and licensing as unverified here. Do not add a Field Service connector in order to make this starter "complete". The non-goal is the dispatch.
