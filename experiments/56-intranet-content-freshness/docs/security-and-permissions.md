# Security and permissions

`agent-manifest.yaml` and `permissions.yaml` are the same document. Writes are disabled. Sends are disabled. Every high-risk action is disabled, including edit, publish, unpublish, delete, reassign, and message staff.

## Who can approve

The approver is the content owner named on the inventory (`content_owner_id`). The actor role has to be "Content owner" and the actor id has to match. Page text cannot set that id. `human_approval`, `confirmed`, and `selection` keys planted on the inventory are stripped.

`record_approval` is the only step that sets `human_approval`. Its `via` value is `record_approval`. If the human queue is not empty, `queue_reviewed` has to be boolean true before other tasks can be approved. If a source pin is older than 180 days, `stale_seen` has to be true and the quotes are omitted. The 180-day window is configuration, not a statutory period.

`create_approved_tasks` records a JSON stub only for task ids on that approval. `POST /planner/tasks` is not sent. `planId` is null. The Power Automate action "Start and wait for an approval" is not sent. `executed` stays false.

## What is withheld

A page with no readers, or with readers that do not overlap the requesting user, is a count. The title and the body are not copied. A bad page id is a count.

Markings are read from metadata, from the body after instruction removal, and from HTML comments after instruction removal. A compound or conflicting label takes the higher marking. OFFICIAL-SENSITIVE is above OFFICIAL. SECRET is above OFFICIAL-SENSITIVE. TOP SECRET is above SECRET. An unrecognised label fails closed. A sentence such as "my clearance is TOP SECRET" is an injection signal. It is not a marking and it is not a clearance.

A legal hold on the fixture stays true. A retention label is copied. Neither is a decision to dispose. A safeguarding cue is queued and the extract is not copied.

Contact fields are masked only when a pattern matches. A field that does not match is withheld, not copied raw. `output_is_anonymised` stays false. `accuracy_met` stays false. The agent does not erase or rectify.

## Neighbours

Experiment 50 proposes duplicate ids for ordinary pages. Archive and merge proposals are not followed. Experiment 55 runs only when the caller supplied a linked index and a separate location selection, including a query. This starter does not invent a query. File titles and snippets from the finder are not copied. A linked file id that the finder did not return is `linked_file_not_in_matches`, not a fresh file. Experiment 49 and Experiment 08 run on ordinary pages only. SECRET, safeguarding, and oversize text are not sent to them. If a neighbour folder is missing, the core raises `FreshnessForbidden` rather than inventing a substitute.

## Not opened on 16 November 2026

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview beyond pages not opened for this experiment, and Application Insights. The sitePage list-pages permission table was not re-opened. Article 6, Article 9, and Article 84B were not opened. Regulation 7 of SI 2018/952 was not opened. Do not treat those as verified here.
