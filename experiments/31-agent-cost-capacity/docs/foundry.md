# Microsoft Foundry

This report does not create a Microsoft Foundry agent, a project, or a deployment. No Foundry resource was created while this folder was written. A live Foundry run has not been done.

The catalogue row for G009 names Microsoft Fabric and Power Platform. Foundry is here because usage telemetry can include Foundry model tokens, and because a later host might show this JSON beside other evaluations. This folder does not connect to Fabric and does not recommend a move to Foundry.

## What the cost page said

[Plan and manage costs](https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs) was opened on 3 November 2026.

Foundry resources are charged for the Azure services used. Pay-as-you-go is described as billed according to usage. Token billing units and rates vary by model, deployment type, and meter. The page points at a pricing page for current rates. That pricing page was not opened. No rate is copied. The page says the invoice and the meter records are the source of truth, and that cost records can be delayed. Foundry has no dedicated page in the Azure pricing calculator because it is composed of optional services.

Provisioned throughput hourly billing was not opened in full. It is unverified here. This starter has no meter for it. A rate card cannot price it by inventing a unit the code does not know.

Fine-tuning charges are described on that cost page as training, hosting, and inference. This starter does not price training or hosting. It prices input and output tokens only when the rate card has those meters.

## How a Foundry row is priced

The platform value is `microsoft_foundry`. The model deployment name has to match the rate line when the line names one. Input tokens and output tokens are each priced once. If `tokens` and `foundry_usage` disagree, the meter is null and the two quantities are not added. Copilot Credits on the same row are not priced. They are a Copilot Studio unit on the pages opened for this experiment, not a Foundry meter.

## Prompt Shields and identity

Prompt Shields were not opened for Experiment 31. Anything this folder might say about defaults or preview status would be unverified. The local pattern match is not a shield result.

Microsoft Entra identity for Foundry Agent Service was not opened. It is unverified. A UK region list was not on the cost page. UK region availability for a later deployment is unverified.

## What would still be true in a later host

The Python report would still be the arithmetic. `rates_validated` would still start false. A person would still validate the rates and the forecast before anyone treated a figure as a charge. The host would not be a reason to enable a write, a send, or a subscription change.
