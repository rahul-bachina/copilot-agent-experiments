# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control and this note is out of date. It is written for a site owner, a DPO, and a security lead deciding whether to try the starter. It is not a completed DPIA and it is not an ATRS submission.

`permissions.yaml` is the same file as `agent-manifest.yaml`.

## Autonomy

**A1.** The site owner approves every metadata change and every publishing action. The curation stub is a later, explicit step and still does not change the site. There is no A3 path. Writes are disabled. Sends are disabled.

## What is read

**Read, in this starter.** The snapshot the site owner pastes. The as-of date. The pinned sources. Experiments 12, 08, and 49, in process, for visible text only. Experiment 44, in process, when the snapshot includes queries, and only from pages that were not queued.

An item is read only when one of the requesting user's principals is on its `readers` list. A missing list fails closed. Hidden ids, titles, and text are not returned and are not passed to those experiments.

The Python starter does not persist the snapshot. A snapshot that is not marked synthetic is refused, and the refusal does not echo the body. Identifier values are not copied. `output_is_anonymised` stays false.

## What is not done

The agent does not delete, unpublish, move, or change permissions. It does not call SharePoint or Microsoft Graph. It does not decide that Article 5(1)(d) or Article 5(1)(e) was met, or that the section 46 code was followed. It does not curate a page that looks like personal data or that carries a marking other than ordinary OFFICIAL.

## Controls that were opened

These pages were opened on 12 November 2026.

- Microsoft Graph `sitePage` v1.0 lists `title`, `publishingState`, `webUrl`, `createdBy`, and `lastModifiedDateTime`, among others. The property list does not include audience, review date, or owner. Those starter fields are configuration, not verified tenant columns.
- List sitePage names `Sites.Read.All` as least privileged and `Sites.ReadWrite.All` as higher. `Sites.Selected` is described on a different page as a site-collection scope after an explicit assignment. The list-pages page does not say `Sites.Selected` is accepted. This starter calls neither API.
- Copilot Studio's SharePoint knowledge page says the agent surfaces only content the signed-in user can access. This starter does not register a knowledge source. The same rule is implemented on the pasted snapshot.

## Controls that were not opened

These pages were not opened on 12 November 2026. Treat the product behaviour as unverified. None of these objects is created in this folder.

| Control | In this starter |
|---|---|
| Microsoft Entra Agent ID | Not registered |
| Conditional Access for agents | Not configured |
| Power Platform DLP as a configured policy | Not configured. The flow note says what a later connector must not do |
| Microsoft Foundry prompt shields | Not enabled. The core does not call a model |
| Key Vault | Not used |
| Microsoft Purview | Not connected |
| Application Insights | Not connected |

## Logging

This starter writes no log. Before live use, log who ran it, when, the site id if it matched the synthetic pattern, the outcome, the withheld count, and the later review. Do not log a page body or an identifier value.

## Kill switch

Set the agent to Off in Copilot Studio administration. Revoke any key or managed-identity role used for an optional narrative. Block any connector added later for SharePoint write, Graph write, or mail. Those steps are outside this folder. The click-path was not opened.
