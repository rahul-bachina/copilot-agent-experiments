# Microsoft Foundry

A path for a team that wants a short brief around the checklist JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The checklist in `src/precheck.py` remains the system of record. A model does not set `s21_approver_decision`, approve a promotion, publish one, or draft replacement copy. Experiment 08 remains the identifier gateway. Experiment 03 remains the lifecycle proposal. Experiment 04 remains the marketing-page pin. A model does not replace any of them.

## What was not called

This starter makes no network call. It does not open the Handbook, legislation.gov.uk, or the Financial Services Register at run time. Foundry vision is not used. An image, a video, or a screenshot of an app screen is not read. Phrase matching on the text the reviewer pasted is the whole check.

## What a model may do, if a team adds a brief

- Turn the checklist JSON into a short note for the section 21 approver, using only fields that are already in the JSON.
- Point at `prompt_injection`, `sources_stale`, and any row whose status is `flagged_for_review` or `question_for_approver` in the first paragraph.
- Repeat that `s21_approver_decision` is null, that `promotion_approved`, `published`, and `compliance_opinion` are false, and that the nested gateway output is not anonymised.

## What the model must not do

- Set `s21_approver_decision`, `promotion_approved`, `published`, or `compliance_opinion`.
- Say the promotion is approved, compliant, fair, clear, or not misleading.
- Draft replacement copy, including a "corrected" risk warning.
- Decide that section 21, article 73ZA, paragraph 26F, or COBS 4.12A.11R(5) is satisfied.
- Decide that a person has permission under section 55NA. That section was not opened.
- Clear a stale flag because the draft says the rules are current.
- Describe the redacted text as anonymised, or reconstruct a National Insurance number.
- Treat a phrase match as prominence. COBS 4.12A.36R and COBS 4.12A.38R were not opened.
- Read an image or a video and describe it as checked.

Prompt shields in Microsoft Foundry are named in the security note as a tenant control. The product page was not opened for this experiment. Availability in a given tenant is unverified here.

## Region

If a brief is added later, run it in UK South or UK West and confirm the data-use terms at the time. This folder does not create that resource.
