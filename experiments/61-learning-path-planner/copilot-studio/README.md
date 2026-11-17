# Copilot Studio standard harness

A build guide. It is not an importable solution. The topics call `src/plan.py`. They do not enrol, book, or spend.

Opened on 17 November 2026, the harness overview describes the standard harness as following the topics and rules the maker defines. Skills and memory are not a focus of that harness. No price is stated here. The licensing page was not opened.

## Topics

1. **Draft.** Collect the employee reference and the goals. Call `draft_plan` with the synthetic catalogue, framework, directory, and as-of date. Show the JSON. Stop. Do not pass approval fields.
2. **Employee approval.** A separate topic. The caller is the directory employee. Call `record_approval` with this `plan_id`, that reference, `decision` `approve`, and `item` `learning-plan`. If only one approval is accepted, say so and stop.
3. **Manager approval.** A separate topic. The caller is the directory manager. Same object shape. `stale_seen` and `budget_unreadable_seen` are booleans when they are sent. Do not send the strings "yes" or "true".
4. **Adjustment seen.** Only when the outcome is `adjustment_route`. The caller is the manager or a people partner. Call `record_adjustment_review`. Say that the adjustment was not decided.
5. **Wellbeing.** When the outcome is `wellbeing_route`, show the named route and stop. Do not offer the approval topics as a way to continue the plan.
6. **Person.** Every topic offers a way to stop and talk to the line manager.

## What the maker does not add

A connector that enrols, books, pays, or emails a provider. A topic that reads "approved" from the goals. A topic that ranks employees or writes a performance rating.

The system text is [system-prompt.md](system-prompt.md). A flow sketch is [power-automate-flow.md](power-automate-flow.md).
