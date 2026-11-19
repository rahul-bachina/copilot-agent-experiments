# Microsoft Fabric

Catalogue row H010 names Microsoft Fabric and Microsoft 365. The runnable core in this folder is Python. It does not deploy a Fabric item.

[What is Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview) was opened on 19 November 2026. The page describes Fabric as a software-as-a-service analytics platform. It says workloads share OneLake, a logical data lake. It names Data Engineering, Data Factory, Data Warehouse, Real-Time Intelligence, and Power BI among the workloads. It says Fabric IQ is in preview. It says Fabric integrates with Microsoft 365, including Excel and Teams, and with Microsoft Foundry. It says Microsoft Purview provides information protection, data loss prevention, audit, and risk and compliance capabilities for supported Fabric data. The page did not show a last-updated line in the extract. That date is unverified.

What this starter does not do, and does not claim:

- It does not create a workspace, a lakehouse, a notebook, a pipeline, a semantic model, or a Power BI report.
- It does not call a Fabric API, a Spark job, or Copilot in Fabric. Those calls were not tested. Whether this package imports unchanged inside a Fabric notebook is unverified.
- It does not use Fabric IQ. The overview marks that workload as preview.
- It does not configure Purview. The sentence above is what the overview said. A configured label or policy was not verified.
- It does not move the evidence into OneLake. A later deployment could store the JSON the core already produced, including the suppressed team view, in a lakehouse the organisation controls. That deployment is not this repository. The suppression has to happen before the file is stored. Storing the raw evidence in OneLake would be a new purpose the controller has to decide. Article 5(3), read on 19 November 2026, says processing is not lawful by virtue only of being compatible with the purposes for which the personal data was collected.

Microsoft 365, on the same page, is a place the organisation might already hold the CV extract or the learning record. This starter does not call Graph, SharePoint, or a mailbox. A mailbox item in the pack is skipped.

The team view is the part a Fabric report could show later: counts, with small cells empty, and no names. The report would not be an anonymised dataset. `output_is_anonymised` stays false. The ICO anonymisation guidance was not opened.
