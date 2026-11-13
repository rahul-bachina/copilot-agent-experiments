# Experiment 54: Excel Assumption Review Agent

Catalogue ID **M006**. Autonomy **A0**. A read-only review of one synthetic workbook for the model owner.

The model owner confirms the workbook, the ranges, and the formulas. The agent then writes a report: an inventory of inputs, hard-coded numbers inside formulas, formulas that do not match their neighbours, broken or circular references, units and date-basis differences, a one-at-a-time sensitivity, and questions for the owner. It does not edit the workbook. It does not say an assumption is right or wrong. It does not invent a benchmark.

Northmere Analytical Unit is invented. The workbook is synthetic. The phone number is in the UK drama range. Nothing here is a customer, a statistic, or a case study.

## Non-goals

- Edit a cell, save the workbook, or call Microsoft Graph.
- Call Microsoft 365 Copilot in Excel.
- Decide that an assumption is correct, material, or typical.
- Invent a benchmark, a rate, or a "should be" figure.
- Sign an assumptions log, appoint a senior responsible owner, or decide that a model is business-critical.
- Treat words inside a cell as confirmation of the scope.
- Copy an email, a phone number, a date of birth, a personal name, or a postcode into the report.
- Process a safeguarding or distress phrase as a modelling question.
- Strip a protective marking or clear a legal hold.
- Assert a lawful basis. UK GDPR Articles 6 and 9 were not opened.

## How to run it

```bash
cd experiments/54-excel-assumption-review
python -m pip install -r requirements.txt
python src/review.py \
  --input examples/sample_pack.json \
  --confirm examples/scope_confirmation.json \
  --as-of 2026-11-13
```

Exit 0 is a report or a refusal. Exit 2 is unreadable input, bad JSON, a bad date, or a missing neighbour experiment. The confirmation is a separate file. It is not a key inside the pack.

`python eval/evaluate.py` runs the deterministic smoke test. The checked-in result is `eval/smoke_report.json`. It is a smoke test of the Python, not a model score. Each case is counted once.

Matplotlib is used only by `docs/generate_diagram.py`. It is not a test dependency.

## What the sample report says

On 13 November 2026 the confirmed sample produces `review_for_model_owner`. The baseline of `Outputs!B2` is 169014.3. A 1 percent increase in `unit_cost` (`Inputs!C5`) or `volume` (`Inputs!C4`), holding the other assumptions fixed, moves that output by 1690.143. The inflation cell (`Inputs!C2`) moves it by 27.3, because `Calc!E4` uses the literal 1.025 rather than the inflation cell. Other assumption cells do not move it. A zero change is stated. It is not a finding that the assumption does not matter.

Hard-coded numbers that are not the common arithmetic values 0, 1, and -1: `Calc!C4` contains 1.02 and `Calc!E4` contains 1.025. Columns `Calc!C2:C4` and `Calc!E2:E4` do not share one formula shape. `Calc!F2` points at `MissingSheet!A1`. `Calc!G2` and `Calc!G3` refer to each other. The formula reader does not guess a value for either.

Paired rows go through Experiment 36. Inflation stored as 0.025 (proportion) and 2.5 (percent) is a material discrepancy. The starter does not convert one into the other. Days in year, 365 calendar against 360 financial, is a material discrepancy and a date-basis mismatch. The start date `2026-04-01` and `01/04/2026` is an immaterial difference of formatting. The discount rate matches. Neither side is chosen.

`Notes!A1` matches an email, a UK mobile, a labelled date of birth, a labelled personal name, and a postcode. The types are recorded. The text is not copied. `output_is_anonymised` stays false. Cover text that says it is not true that `Inputs!C2` includes a hard-coded number does not become a finding. An instruction in `Cover!A6` is recorded by pattern name and is not followed. The marking `OFFICIAL-SENSITIVE` and the retention label `legal-hold` stay on the report.

Experiment 30 drafts regression cases from the findings. `maintainer_approved`, `merged`, `pushed`, and `edited_agent` stay false.

## Sources opened on 13 November 2026

The core does not download these pages when it runs. `src/sources.py` is the pin.

- [The AQuA Book](https://www.gov.uk/guidance/the-aqua-book). The page title is The AQuA Book. Published 30 July 2025, from the Government Operational Research Service, the Government Analysis Function, the Government Actuary's Department, and the Office for National Statistics. Section 1.1 says the last version was published in 2015, following Sir Nicholas Macpherson's Review of quality assurance of government models. The assumptions log, under Documentation, should describe each assumption, quantify its effect and reliability, set out when it was made, explain why it was made, and explain who made it and who signed it off. Section 1.3.3 distinguishes verification from validation. This starter does not sign that log and does not decide that analysis is fit for purpose.
- [Review of quality assurance of government models](https://www.gov.uk/government/publications/review-of-quality-assurance-of-government-models). HM Treasury. Published 5 March 2013. The page describes the final report by Sir Nicholas Macpherson, then Permanent Secretary to the Treasury. The PDF listed on the page was not opened. A guessed asset URL returned 404. Recommendation numbers are not quoted from the 2013 report.
- The March 2015 PDF, [The Aqua Book](https://analysisfunction.civilservice.gov.uk/wp-content/uploads/2018/03/Aqua-Book-4.pdf). This is not the current GOV.UK page. Paragraph 1.4 summarises headline recommendations, including quality assurance of inputs, methodology, and outputs for business-critical models, and a single senior responsible owner. Those sentences are the 2015 book's summary. This starter does not appoint an owner and does not decide that a model is business-critical.
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview). The page names the Microsoft Copilot harness, the Customer Conversation harness, and the standard harness. The Microsoft Copilot harness is described as reasoning-heavy and multi-step. The page says it creates and edits Word, Excel, PowerPoint, and PDF files, supports skills and memory, and uses Copilot Credits. No price is on the page. The page opened on 13 November 2026 does not use the older catalogue name for the skills harness, and it does not contain the sentence earlier experiments recorded about the GitHub Copilot service. This starter does not edit an Excel file.
- [What is Microsoft Copilot?](https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview). Under Microsoft 365 Copilot (Basic), the in-app Excel line is analyse data, generate insights, and create formulas and visuals. The page says the person signs in with a work or school account and the file must be editable, not read-only. A dedicated Copilot in Excel page was not opened. This starter does not call Copilot in Excel.
- [Working with Excel in Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0). The Excel REST API reads and modifies Office Open XML workbooks in OneDrive for Business, a SharePoint site, or a group drive. `Files.Read` is listed for read actions. `Files.ReadWrite` is listed for read and write actions. A call that does not send `workbook-session-id` persists changes. A non-persistent session does not save to the source. This starter calls neither and does not create a session. The permissions table on a range-get page was not opened.

Also not opened, and therefore not decided here: Microsoft Entra Agent ID, Conditional Access for agents, Microsoft Foundry prompt shields, Key Vault, Microsoft Purview, Application Insights, Power Platform DLP as a configured policy, Copilot Studio billing pages, and UK GDPR Articles 6 and 9.

More than 180 days after 13 November 2026, the review is withheld. The date 180 days on, 12 May 2027, is still inside the window. The marking and the retention label are still reported.

## Harnesses

Both shipped harnesses call `src/review.py`. The standard harness is one topic in `copilot-studio/`. The skills under `skills/` are the layout the catalogue calls the GitHub Copilot harness. On the page opened on 13 November 2026 that layout sits under the name Microsoft Copilot harness. See `docs/harness-comparison.md`.

An optional Microsoft Foundry narrative may explain JSON the Python already produced. No Foundry resource is deployed. `model_called` stays false in this repository. See `docs/foundry.md`.

## Neighbours

- Experiment 08 proposes redactions. The raw value is not copied. A local pattern also flags a UK postcode the gateway did not flag on the fictional `AB1 2CD`.
- Experiment 15 supplies phrase categories. A possible safeguarding, self-harm, or financial-hardship category stops the routine review. The matched phrase is not copied into the report.
- Experiment 30 drafts regression cases. Nothing is merged, pushed, or written back into the agent.
- Experiment 36 classifies paired values. It does not choose which side is right, and it does not convert a percent into a proportion.

## Limitations

The formula language is a closed set: numbers, cell references, ranges, parentheses, `+`, `-`, `*`, `/`, `SUM`, `AVERAGE`, `MIN`, `MAX`, and `IF`. Any other function, an external link, or `#REF!` is named and not evaluated. Blank cells on a sheet that exists become 0 in arithmetic. A missing sheet is broken. A cycle is named and not given a value.

Sensitivity recomputes only cells inside the confirmed ranges, with the Python evaluator. It is one input at a time, at 1 percent of the stored value (or 0.01 when the stored value is 0). It is not a tornado that Excel would produce, and it is not a statement that a change is material.

JSON cells are the confirmed representation. If the local `.xlsx` disagrees, both values are listed, `chosen` is null, and that cell is left out of the sensitivity and out of the inventory value.

This is a starter. It is not an assurance opinion under the AQuA Book.

## Licence

MIT. See the repository `LICENSE`.
