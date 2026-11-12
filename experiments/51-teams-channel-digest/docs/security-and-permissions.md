# Security and permissions

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

`permissions.yaml` is the same document. It validates against `schemas/agent-manifest.schema.json`.

## Autonomy

A0. The requesting user confirms the channels and the period before any digest. `human_approval` stays null. Confirming the scope does not approve a post and does not approve monitoring.

## What is read

One synthetic export. The user's accessible channel ids. A separate confirmation. Experiments 08, 41, and 29, in process, and only after confirmation. The pinned source list. Nothing else.

Message text from a channel the user cannot access is not read. An unavailable channel is not read. The scope preview does not copy message text.

## What is not done

No post, reply, reaction, mention, or forward. No Graph call. No write. No send. No performance judgement. No claim that Article 5 was met. No claim that a digest is held information. No claim that monitoring workers is lawful.

## Controls that were opened

On 12 November 2026:

- UK GDPR Article 5, including Article 5(1)(b), Article 5(1)(c), and Article 5(3). Article 84B was named in Article 5(1)(e) and was not opened.
- Freedom of Information Act 2000 section 1. Sections 2, 3, 9, 12, and 14 were not opened.
- ICO, "Employment practices and data protection: monitoring workers", and the child page "Specific data protection considerations for different ways or methods of monitoring workers". The hub says the guidance is under review because of the Data (Use and Access) Act.
- Microsoft Graph, list channel messages, v1.0. Delegated least privilege on that page is `ChannelMessage.Read.All`. Application least privilege is `ChannelMessage.Read.Group` with resource-specific consent. A date filter is not a supported query option.
- Copilot Studio harness overview.
- Overview of AI in Microsoft Teams. The end-user article on Copilot in chats and channels was not opened. The Channel Agent email article listed in the table was not opened.

## Controls that were not opened

Treat these names as unverified here. None of these objects is created in this folder.

| Control | In this starter |
|---|---|
| Microsoft Entra Agent ID | Not configured. The page was not opened on 12 November 2026. |
| Conditional Access for agents | Not configured. The page was not opened. |
| Power Platform DLP as a configured policy | Not configured. The page was not opened. |
| Microsoft Foundry prompt shields | Not configured. The page was not opened. |
| Key Vault | Not configured. The page was not opened. |
| Application Insights | Not configured. The page was not opened. |
| Work IQ | Named on the catalogue row. The page was not opened. Not called. |
| Purview | Not called. A sensitivity label is not applied. |

## Microsoft Graph, if a tenant connects it later

The list-channel-messages page says the delegated least-privileged permission is `ChannelMessage.Read.All`, and that higher-privileged permissions include `Group.Read.All` and `Group.ReadWrite.All`. This starter would still not use a write permission. `ChannelMessage.Read.All` lets an app read channel messages on behalf of the signed-in user. The permission table does not describe it as limited to one channel. The local access list in this starter is stricter than that permission, and it only works because the export is local.

Application `ChannelMessage.Read.All` is listed as a higher-privileged application permission, not the least privileged. The least privileged application permission on that page is `ChannelMessage.Read.Group`. This starter does not use application permissions.

Whether any of these APIs are protected APIs was not stated on the page that was read. That point is unverified.

## Logging

This starter writes no log. Before live use, log who ran it, the export id, the channel ids, the as-of date, whether the export was stale, and whether a digest was produced. Do not log message text or an identifier value.

## Kill switch

Do not run `src/digest.py`. Delete the local copy from a machine that should not draft a digest. There is no published agent to turn off. If a team later publishes one, turn that Copilot Studio agent off, remove any Foundry credential, and block a Teams send in a data loss prevention policy the organisation configures. Contacts in the manifest use `northmere.example.gov.uk`. They are placeholders. Northmere Borough Council is invented.

## UK GDPR

No lawful basis is asserted. A channel digest for the requesting user's own channels is a different purpose from monitoring workers. The ICO page on monitoring messages says a DPIA must be completed before that monitoring, and that content should be distinguished from network data. This starter reads content the user already supplied in a file. It is not that monitoring deployment. A body that wants the live pattern needs its own assessment. `dpia_decided` stays false.

Article 5(1)(b) and (c) are the principles the manifest points at. The flags that would say they were met stay false.
