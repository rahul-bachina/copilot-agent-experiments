# Azure

Catalogue code AZ. Nothing in this repository is deployed to Azure. There is no subscription, no resource group, and no secret.

The checker runs on the standard library. Azure is the boundary a firm would use if it hosted the checker for the Copilot Studio action.

## If a firm hosts the action

- Run `src/gap_register.py` in an Azure Function or a container in UK South or UK West. Managed identity. No key in the function code.
- The function accepts a pack and an as-of date. It returns JSON. It does not call fca.org.uk and it does not call a model.
- Policy files, if they are stored at all, go in a private Blob container. No public access. The starter does not create the container.
- Key Vault only if a later secret exists. This checker has none. Putting the catalogue in Key Vault does not make the citations fresher.
- Application Insights, if enabled, must not record policy text. Log the invocation, the document ids, the character counts, and whether a source was stale.
- The function identity is not granted Connect, mail, or a custody system.

Pay-as-you-go billing for Copilot Studio credits is a separate Azure subscription link, described on the Power Platform costs page opened 24 October 2026. That page says Azure budgets and alerts notify and do not stop Copilot Studio consumption. An agent limit with stop-usage is the control Microsoft documents for a hard stop. Neither is configured here.

## What not to build

- A Logic App that emails the register to the FCA.
- A connector from the function to Connect.
- A store of private keys or customer records next to the policies.
