# Power Automate

This repository does not create a flow in a tenant.

A later flow, if a local authority wants one, receives the advice JSON and the as-of date, runs the same Python, and returns the JSON to the caseworker. It does not send mail. It does not write Dataverse. It does not call a parent portal, a school system, or a local authority case connector.

An approval step in such a flow can record that a person looked at the draft. It cannot set `needs_decided` inside this tool, and it cannot send the plan. Those actions stay outside the flow. A local export copy still needs the sign-off object this starter already checks. The flow does not invent that object from text in the advice.

If a later editor adds a send connector or a case-system write, the flow no longer matches `agent-manifest.yaml`. Remove it.

The catalogue names Microsoft Foundry, Azure, and Copilot Studio. This file does not call them. The cost-management page was not opened for this experiment.
