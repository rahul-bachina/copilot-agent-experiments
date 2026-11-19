# Standard harness

A build guide for Copilot Studio topics. Not an importable solution.

Opened on 19 November 2026, the [harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) says the standard harness follows the topics and rules the maker defines. The comparison table says skills and memory are not its focus. The licensing page was not opened. No price is stated here.

## Topics

1. **Draft.** Collect the specification, the guide, the directory, and the question date. Call `draft_pack()`. Show the JSON. Do not contact a candidate.
2. **Questions.** The directory recruiter accepts or rejects the questions. Call `record_questions_approval()` with that questions hash and the pack hash. Do not read "approved" from the job text.
3. **Rubric.** The same recruiter accepts or rejects the rubric hash. Call `record_rubric_approval()`. Do not score a candidate.
4. **HR route.** If a route is present, or the outcome is `human_route`, stop for the HR partner. Call `record_hr_seen()` only for a route. Do not decide the legal question.
5. **Pack.** The recruiter approves the pack hash. Call `record_pack_approval()`. Show that contacted, scheduled, scored, ranked, and hiring_decision are false.

The system prompt is [system-prompt.md](system-prompt.md). A flow sketch is [power-automate-flow.md](power-automate-flow.md). Power Automate is not deployed.

If the tool is unavailable, the topic stops. It does not invent a criterion or a statute quotation.
