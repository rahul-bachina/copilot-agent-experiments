# Power Automate note

Catalogue row L009 names Power Platform beside the GitHub Copilot harness. This note is a build guide. It is not an importable solution, and this starter enables no connector.

1. A manual trigger collects the control id, the tester reference, the period, the sample seed, and the question date.
2. An action runs `prepare_test` and returns the JSON. It does not write to Dataverse and it does not send mail.
3. A condition stops when `distress.routed` is true until a person records that the route was seen.
4. An approval action, the platform's own approval, is still not enough unless the following step calls `record_tester_approval` with the content hash. The evidence text is not that action.
5. A later action may call `record_tester_result` with the tester's words. It does not update a GRC row and it does not send.

If a connector to a GRC system is added later, it is outside this starter. `production_written` stays false here.
