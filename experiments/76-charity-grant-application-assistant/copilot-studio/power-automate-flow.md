# Power Automate flow

This is a build note. It is not an importable flow.

The flow runs `prepare_application` and returns the JSON to the topic. A second flow runs `record_route_seen` when the applicant records that they have seen a route. A third flow runs `record_applicant_approval` when the approval object is present. The third flow writes only the synthetic staging row inside the Python process. It does not post to a funder portal.

Do not add a connector for mail, SharePoint, Dataverse, or a funder website. Power Platform DLP should block those connectors for this agent. This starter does not create the policy. A configured DLP policy was not opened on 24 November 2026. Treat that product behaviour as unverified.

A connector added later for a funder portal would be a manifest change, not a setting on this flow.
