# Microsoft Foundry

A path for a team that wants a short narrative around the draft JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The draft in `src/assess.py` remains the system of record. A model does not set a screening result, an Article 22 result, a residual score, or a sign-off name. Experiment 08 remains the identifier gateway. A model does not replace it, and a model does not call the text anonymised.

## What was not called

This starter makes no network call. Prompt shields in Microsoft Foundry are named in the security note as a tenant control. The product page was not opened on 28 October 2026. Availability in a given tenant is unverified here.

## What a model may do, if a team adds a narrative

- Turn the draft JSON into a short brief for the privacy officer, using only fields that are already in the JSON.
- Point at `prompt_injection`, `sources_stale`, `screening.screen_result`, and `prior_consultation.code` in the first paragraph.
- Repeat that `dpia_required`, `article_36_consultation_required`, and `lawful` are null, and that the nested gateway output is not anonymised.

## What the model must not do

- Invent a screening answer, a lawful basis, a harm score, or a sign-off name.
- Set `approved`, `signed_off`, `residual_risk_accepted`, or `prior_consultation_sent`.
- Decide that Article 35 requires a DPIA, or that Article 36(1) requires consultation.
- Decide that an Article 22B condition is met, or that meaningful human involvement is present because a manifest disables a tool.
- Clear a stale flag because the brief says the sources are current.
- Fill a gap that the draft left as "Not recorded in the project brief".
- Describe the text as anonymised, or reconstruct a redacted identifier.
- Approve, reject, or sign off the assessment, accept residual risk, or send a consultation.

## Region

If a narrative is added later, run it in UK South or UK West and confirm the data-use terms at the time. This folder does not create that resource.
