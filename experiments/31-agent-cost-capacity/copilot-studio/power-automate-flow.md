# Power Automate

This repository does not create a flow in a tenant.

A later flow, if an organisation wants one, receives the two JSON files and the as-of date, runs the same Python, and returns the JSON to the FinOps owner. It does not send mail. It does not write Dataverse. It does not call the Power Platform admin centre, Azure Cost Management, or a subscription action.

An approval step in such a flow can only record that a person looked at the draft. It cannot set `rates_validated` inside this tool, and it cannot change a quota. Those actions stay outside the flow.

If a later editor adds one of those connectors, the flow no longer matches `agent-manifest.yaml`. Remove it.

The catalogue names Power Platform because that is where a quota change would be made by an administrator. This file does not authorise that change. The cost-management page opened on 3 November 2026 describes admin-centre controls, including an agent monthly limit that can stop usage when it is turned on. This starter does not turn it on. Azure budgets and alerts, on that page, notify and do not stop Copilot Studio consumption.
