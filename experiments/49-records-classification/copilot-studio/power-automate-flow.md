# Power Automate flow

One flow for each topic. Each flow runs the Python core and returns JSON to the Copilot Studio topic. It is a design note, not an exported solution.

The flow's only job is to return JSON. It does not create a SharePoint item, it does not call Microsoft Purview, and it does not delete a file.

## What a later connector must not do

If an organisation later adds a connector, the manifest has to be updated first, and a person has to confirm the write outside this starter. This folder does not include that connector.

Do not add a connector that:

- applies a retention label or a sensitivity label in Purview;
- deletes, moves, or declares a record;
- starts a disposition review;
- sends mail.

Purview disposition review, as described on the records-management page opened on 11 November 2026, is a person reviewing an item before deletion. This flow does not start one. The click-path for that review was not opened. Treat the click-path as unverified.

## DLP

A Power Platform DLP policy that blocks Purview, SharePoint write, and mail connectors would match this design. No such policy is configured in this folder. That product behaviour was not opened on 11 November 2026 and is unverified here.
