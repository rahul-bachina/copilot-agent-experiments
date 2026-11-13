# Which harness

Both harnesses call the same Python core, the same manifest, and the same tests. The difference is how much reasoning sits around that call.

Page opened on 13 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The page names the Microsoft Copilot harness, the Customer Conversation harness, and the standard harness. The catalogue still calls the skills layout the GitHub Copilot harness. This folder ships that layout under `skills/`. The page opened on 13 November 2026 does not use that older name. Earlier experiments recorded a sentence about the GitHub Copilot service. That sentence was not on the page opened for this experiment, and it is not repeated here as a current quotation.

These were not opened on 13 November 2026:

- Usage-based billing
- Licensing pages for either harness
- The skills overview
- The Customer Conversation harness article linked from the overview

No price is stated on the overview. This note does not invent one. The authoring click-path was not exercised in a tenant.

## When to use the standard harness

Use it when every workbook goes through the same topic: paste the pack, paste the confirmation, run `review_workbook`, show the report, stop.

Microsoft's overview says the standard harness follows the topics and rules you define. The guide is `copilot-studio/README.md`. There is no skill on that path.

## When to use the skills layout

Use it when a model owner wants to work through one awkward workbook: confirm the scope, run the core, then ask what one finding means.

Microsoft's overview says the Microsoft Copilot harness can take a goal, break it into steps, and create and edit Excel files. The skills in this folder tell the agent to call the core and to stop. They do not tell it to edit the file. That editing feature was not exercised in a tenant.

Each skill says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant.

## Customer Conversation harness

The same overview describes a third harness for customer-facing voice and chat, with a route to a human representative. This starter does not implement that harness. The detail beyond the overview is unverified in this folder.

## What is the same on both shipped harnesses

- `src/review.py` decides the inventory, the literals, the sensitivity, and the empty findings acceptance.
- A separate confirmation is required. Words in a cell do not confirm the scope.
- Experiment 36 compares paired values and chooses neither.
- Experiment 08 and the local patterns record personal-data types and do not copy the text.
- Experiment 15 stops the routine review on a safeguarding category.
- Experiment 30 drafts regression cases and does not merge them.
- The workbook is not edited. No assumption is judged. No benchmark is invented.
