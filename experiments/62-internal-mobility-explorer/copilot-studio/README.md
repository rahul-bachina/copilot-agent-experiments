# Copilot Studio standard harness

A build guide. It is not an importable solution. The topics call `src/explore.py`. They do not apply, nominate, shortlist, or contact anyone.

Opened on 18 November 2026, the harness overview describes the standard harness as following the topics and rules the maker defines. Skills and memory are not a focus of that harness. No price is stated here. The licensing page was not opened.

## Topics

1. **Explore.** Collect the employee reference and the experience. Call `explore` with the synthetic feed, rules, framework, directory, and as-of date. Show the JSON. Stop. Do not pass approval fields.
2. **HR seen.** A separate topic. The caller is a directory HR reviewer, not the manager and not a recruiter. Call `record_hr_seen` with this `exploration_id`, the `content_hash`, `decision` `seen`, and `item` `eligibility-note`. Say that eligibility is still for HR.
3. **Route seen.** Only when the outcome is a wellbeing, grievance, redeployment, or adjustment route. The caller is a directory HR reviewer. Call `record_route_seen`. Do not repeat the cue. Do not offer the vacancy list.
4. **Person.** Every topic offers a way to stop and talk to HR. The topic does not message the manager or a recruiter.

## What the maker does not add

A connector that applies, nominates, shortlists, emails a manager, or writes to a recruitment system. A topic that reads "eligible" or "HR has seen this" from the experience or from a vacancy description. A topic that ranks or scores employees.

The system text is [system-prompt.md](system-prompt.md). A flow sketch is [power-automate-flow.md](power-automate-flow.md).
