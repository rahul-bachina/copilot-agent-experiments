# Skills layout

The catalogue row M006 names a Copilot Studio GitHub Copilot harness. The three skills in `skills/` are that layout. Each description says when to use the skill. This starter does not assign a weight to a skill.

Page opened on 13 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

The page names three harnesses: the Microsoft Copilot harness, the Customer Conversation harness, and the standard harness. It describes the Microsoft Copilot harness as reasoning-heavy and multi-step. It says that harness creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and uses Copilot Credits. No price is on the page.

The page opened that day does not use the catalogue's older name for this skills layout. Earlier experiments in this repository recorded a sentence, from pages opened in October and early November 2026, about the relationship between that layout and the GitHub Copilot service. That sentence was not on the page opened for this experiment. This file does not repeat it as a current quotation.

The skills tell the agent to call `src/review.py` and to stop. They do not tell it to edit the workbook, even though the page says the Microsoft Copilot harness can edit Excel files. That file-editing feature was not exercised in a tenant.

## Skills

| Skill | When |
| --- | --- |
| `confirm-workbook-scope` | The model owner still has to confirm the workbook, the ranges, and the formulas. |
| `review-assumptions` | The confirmation exists and the owner wants the inventory, the formula checks, and the sensitivity. |
| `explain-finding` | The JSON already exists and the owner asks what one field means. |

## What was not opened

- Copilot Studio billing pages linked from the overview. No price is copied.
- The skills overview, and the page for adding an uploaded skill.
- The Customer Conversation harness article beyond the overview.
- A tenant click-path. Nothing here is a general-availability claim.
