# Power Platform

Copilot Studio and Power Automate are the Power Platform parts of this starter. Dataverse is described as a boundary. It is not connected. There is no Power BI file. A compliance dashboard would be a different product, and this repository does not imply that one exists.

## What is in the guide

- A standard-harness agent for intake. [../copilot-studio/README.md](../copilot-studio/README.md).
- One Power Automate flow that returns the clock JSON and stops. [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md).
- Tool schemas that reject extra fields. [../schema/](../schema/).

## What is not connected

**Dataverse.** A later design could store the officer's approved draft on a custom table, written by the officer's security role and not by the agent. That is a production write. The manifest sets writes to disabled. Adding the connector means editing the manifest in the same change, naming the table, and keeping the agent's role off that table. The agent would still not write it.

**Housing management systems.** No connector to a housing, repairs, or finance product. The officer files anything they choose to keep.

**Mail and SMS.** Not added. Regulation 10 lists ways a lessor may give a document, including post and electronic transmission. The agent does not give the document.

**Power BI.** Not built. Counts of missed timeframes would be management information from the landlord's own case data. They are not in this folder, and no figure is invented here.

## Timers

A Power Automate delay or a service-level timer is a reminder, not the statutory count. If a landlord wants a chase at the investigation date, the flow should store the date the Python clock returned and wait until that instant. It should not add ten working days with the flow calendar. The emergency period is 24 hours from a time, including the weekend, which a working-day timer will get wrong.

The timer, if built later, notifies an officer. It does not email the tenant and it does not change the category.
