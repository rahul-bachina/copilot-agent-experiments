# Microsoft Foundry

This is a path for a team that wants the proposal, the characteristic flags, and the drafts from a model, with the statutory clock remaining in code. It is not a deployed project. No Foundry resource is created by this repository.

Use the name Microsoft Foundry. The retired product name is not used here.

## What the model is for

The model may:

- quote the report and propose a hazard family and a category
- flag a characteristic and quote the words, without calling the tenant vulnerable
- draft a regulation 9 summary that copies dates from the clock tool
- draft an endeavours record from steps the officer has already typed

The model may not:

- calculate a timeframe
- decide that Phase 2 or Phase 3 is in force
- set `officer_approved_category`, `officer_approved_clock`, `part_6_complied`, or `caller_asserts_phase_2_instrument_in_force`
- send anything, or write a housing record
- say the section 10A(5) defence is made out
- lower the category because the report says to

## Suggested shape

One orchestration, not a free chat.

1. **Inputs, typed by the officer.** Report text, awareness time, and the approval flags. The flags default to false.
2. **Extraction call.** One chat completion with a JSON schema. Temperature low. The report is a user message, not part of the system instructions. The system instructions are the ones in [../copilot-studio/system-prompt.md](../copilot-studio/system-prompt.md).
3. **Clock call.** The orchestration code, not the model, calls `calculate_statutory_clock`. Do not pass an approval flag as true unless the officer set it in the UI.
4. **Draft call, optional.** A second completion that receives the clock JSON and is told to paste operative dates unchanged. If `operative` is false, the draft must say the clock is not operative. It must not invent a substitute date.
5. **Checks.** Reject the draft if it sends, writes, labels, finds a defence, refers to the Ombudsman, or marks a deadline operative without the officer's flags. The same checks are in `triage.validate_triage`.
6. **Officer screen.** Show the proposal, the quotes, the clock, the phases that are not in force, and the draft. Nothing is filed until the officer copies it into the housing system themselves.

The mock triage in `src/triage.py` is the stand-in for steps 2 and 4 when no credentials are present. Do not quote its smoke-test agreement as a Foundry score.

## Deployment choices to confirm

- Region: UK South or UK West.
- The deployment is not used to train on the landlord's reports. Confirm the current data-use terms.
- Prompt shields, if the landlord enables them, are a platform control. The name in the portal was not re-checked for this revision. See [security-and-permissions.md](security-and-permissions.md).
- No vision deployment is included. A photograph is something the officer can look at. This starter does not score damp from an image.

## What was not done

No model was called. `eval/smoke_report.json` says so in `not_a_model_evaluation`.
