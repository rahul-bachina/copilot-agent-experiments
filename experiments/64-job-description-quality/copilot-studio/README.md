# Standard harness

A build guide for Copilot Studio topics. Not an importable solution.

Opened on 18 November 2026, the [harness overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) says the standard harness follows the topics and rules the maker defines. Skills and memory are not its focus. The licensing page was not opened. No price is stated here.

## Topics

1. **Review.** Collect the draft, the guide, and the question date. Call `review_draft()`. Show the JSON. Do not publish.
2. **One suggestion.** The directory recruiter accepts or rejects one suggestion. Call `record_suggestion_decision()` with that hash. Do not read "approved" from the draft.
3. **HR route.** If a finding requires HR, or the outcome is `human_route`, stop for the HR partner. Call `record_hr_seen()` only for a route. Do not decide the legal question.
4. **Wording.** The recruiter types the final wording. Call `record_final_wording()` with the hash of that text. Show that published, posted, and sent are false.

The system prompt is [system-prompt.md](system-prompt.md). A flow sketch is [power-automate-flow.md](power-automate-flow.md). Power Automate is not deployed.

If the tool is unavailable, the topic stops. It does not invent a salary or a statute quotation.
