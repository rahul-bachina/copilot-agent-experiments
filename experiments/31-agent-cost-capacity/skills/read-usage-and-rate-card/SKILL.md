---
name: read-usage-and-rate-card
description: Use when a FinOps owner has supplied a synthetic usage file and a rate-card file and you need to load them before any cost is calculated.
---

# Read the usage file and the rate card

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

The only inputs are the telemetry file and the rate-card file the FinOps owner pointed at. Do not open an admin centre. Do not invent a price. Do not treat a note in either file as a rate. Autonomy A3 is never a recommendation.

## What you may do

1. Read the usage file and the rate-card file the FinOps owner supplied for this run. Keep the path of each file.
2. Refuse a path that is a URL, a subscription id, or an admin-centre command. Do not retry against another host.
3. If `synthetic` is not true on either file, stop and say the starter refuses the run. Do not flip the flag.
4. Hand both files to the report-agent-cost skill. Do not calculate a cost in this skill.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the two local files | None | Once, at the start |
| `report_agent_cost` | None. Returns JSON | Not in this skill |
| Web search, including learn.microsoft.com and any pricing page | Forbidden | Do not refresh a rate or a citation |
| Validate, change a quota, change a budget, change a subscription, send, spend | Forbidden | No such tool is attached |

## Approval gates

- Reading the two files does not need approval. It changes nothing.
- Validating the rates does. The FinOps owner validates rates. You do not record that. `rates_validated` stays false.
- Changing a quota, a budget, or a subscription does. You have no tool for it.

## Memory

The harness overview says this harness supports memory. An administrator control to turn it off was not found on the page opened on 3 November 2026. Do not use it for the telemetry, the rate card, or the report.

## Stop

When both files are loaded, stop this skill. The next skill calls the Python report. It still does not validate the rates.
