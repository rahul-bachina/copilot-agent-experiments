# Power Automate flow

One flow for each topic. Each flow runs the Python core and returns JSON to the Copilot Studio topic. It is a design note, not an exported solution.

The flow's only job is to return JSON. It does not call SharePoint, it does not call Microsoft Graph, and it does not delete a page.

## What a later connector must not do

If an organisation later adds a connector, the manifest has to be updated first, and a person has to confirm the write outside this starter. This folder does not include that connector.

Do not add a connector that:

- updates page metadata in SharePoint or through Microsoft Graph;
- publishes, unpublishes, deletes, or moves a page;
- changes permissions or grants access;
- sends mail.

The list sitePage page opened on 12 November 2026 names `Sites.Read.All` as least privileged and `Sites.ReadWrite.All` as higher. This flow uses neither. Whether `Sites.Selected` is accepted for that list method was not stated on that page.

## DLP

A Power Platform DLP policy that blocks SharePoint write, Graph write, and mail connectors would match this design. No such policy is configured in this folder. That product behaviour was not opened on 12 November 2026 and is unverified here.
