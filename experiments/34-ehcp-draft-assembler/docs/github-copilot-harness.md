# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness, as described on the harness overview opened on 4 November 2026. It is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. Customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio. That is Microsoft's statement.

The overview says agents on this harness use Copilot Credits, can use skills and memory, can create and edit files, and run each task in a sandbox. The page does not mark the harness as preview. It does not describe a control to turn memory off. The skills below say not to store the advice.

The billing overview says this harness charges Copilot Credits from the moment you start building, including testing, and that those credits are charged for large language model tokens, tools, and the harness. The licensing page says a Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for this harness. A second sentence on that page, about answer types in other channels, is not merged with the first. No quantity is copied. The cost-management page was not opened for this experiment.

## Skills

Run them in this order. Each one stops.

1. `skills/read-advice-reports/SKILL.md` lists the reports.
2. `skills/assemble-ehcp-draft/SKILL.md` calls `assemble_ehcp_draft` and shows the JSON.
3. `skills/explain-ehcp-draft/SKILL.md` reads that JSON and names the gaps and the approval points.

The tool contract is `schema/tools.json`. `decide_needs`, `decide_provision`, `decide_placement`, `decide_outcomes`, `edit_final_plan`, `send_to_parents`, `send_to_school`, `write_to_la_system`, and `secure_provision` always raise. They are not attached. `export_local_copy` is not callable by the agent.

## What the maker does not add

- A connector to email, a parent portal, a school, or a local authority case system.
- A tool that writes the final plan.
- A tool that fills section I.
- A browse of legislation.gov.uk or learn.microsoft.com.

If a tool is not in `agent-manifest.yaml`, it should not be on the agent.

## Approval

Showing the JSON does not need approval. The caseworker authors the final text, resolves conflicts, and checks the local template. A local copy needs the sign-off object. A send stays outside this agent even after that sign-off. Stale advice or a stale pin is re-opened before anyone relies on a line.
