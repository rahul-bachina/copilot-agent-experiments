# Microsoft Foundry

A path for a team that wants a short narrative around the checklist JSON. It is not a deployed project. No Foundry resource is created by this repository. The name is Microsoft Foundry.

The checklist in `src/review.py` remains the system of record. A model does not set a regulation row, a stale flag, a risk rating, or the customer note. Experiment 12 remains the inventory. Experiment 08 remains the identifier gateway. A model does not replace either.

## What was not called

This starter makes no network call. Azure Document Intelligence and Content Understanding were not re-opened for this experiment. Experiment 12's note, written the same day, records a reading of those pages and says they are not called. This experiment relies on that boundary: a file that Experiment 12 marks `not_read` stays a gap. Treat any detail of those product pages that is not repeated here as unverified for this folder.

## What a model may do, if a team adds a narrative

- Turn the checklist JSON into a short brief for the reviewer, using only fields that are already in the JSON.
- Point at `prompt_injection`, `stale`, `sources_stale`, and `customer_facing.hints_at_suspicion` in the first paragraph.
- Repeat that `final_risk_rating` is null and that the nested gateway output is not anonymised.

## What the model must not do

- Invent a regulation row, a hash, an entity type, or a country classification.
- Set `documents_confirmed`, `purpose_confirmed`, or `final_risk_rating`.
- Decide that regulation 33 applies, or that a country is on the FATF list.
- Put suspicion, a report, a PEP, or a rating into the customer note.
- Clear a stale date because the file says the document is current.
- Describe the text as anonymised, or reconstruct the file body.
- Approve, reject, or onboard the customer, or file a report.

Prompt shields in Microsoft Foundry are named in the security note as a tenant control. The product page was not opened for this experiment. Availability in a given tenant is unverified here.

## Region

If a narrative is added later, run it in UK South or UK West and confirm the data-use terms at the time. This folder does not create that resource.
