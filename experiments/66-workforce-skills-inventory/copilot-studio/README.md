# Copilot Studio standard harness

A build guide. Not an importable solution. The maker defines the topics. The standard harness, on the overview opened on 19 November 2026, follows the topics and rules the maker defines.

Topics, in order:

1. **Propose.** Call `propose_inventory()` with the request, the evidence pack, the example framework, the directory, the transparency record, and the as-of date. Show the JSON. Stop.
2. **Employee decision.** A later topic calls `record_employee_decision()` with a separate object. The evidence text is not that object.
3. **HR validation.** A later topic calls `record_hr_validation()` only when the employee has confirmed or corrected that skill.
4. **Route.** If the outcome is a route, a later topic calls `record_route_seen()`. The cue is not pasted into the topic.

Do not add a topic that writes to an HR system, sets a rating, or emails a manager. The manifest leaves writes and sends off.

The system prompt is `copilot-studio/system-prompt.md`. The flow note is `copilot-studio/power-automate-flow.md`.

The licensing page for the standard harness was not opened. No price is quoted here.
