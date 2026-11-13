# Power Automate

No flow in this starter writes to Excel.

A flow, if a maker builds one later, may only:

1. Receive the pack JSON, the confirmation JSON, and the as-of date from the topic.
2. Run `python src/review.py` on the machine that holds the synthetic file.
3. Return the JSON to the topic.

It must not use the Excel Online (Business) "update a row" or "update a cell" actions. It must not call Microsoft Graph `workbook/createSession` or a range update. The core reads `fixtures/northmere_grants.xlsx` with `data_only=False` and `read_only=True` and does not save it.

Those connector pages were not opened on 13 November 2026. The prohibition is this starter's rule, not a quotation from a connector reference.
