# Flow note

Catalogue row L010 names M365 and Work IQ. This note is a build guide for a flow a maker might put behind the standard-harness topic. It is not an importable solution, and this starter enables no connector. Work IQ is not called.

1. Receive the meeting id, the secretary reference, and the question date.
2. Run `assemble_pack` on the synthetic request. Return the JSON to the topic.
3. Stop. Do not write to SharePoint, do not send mail, and do not post to a board portal.
4. A later step may call `record_secretary_approval` only when the topic passes the approval object. That step writes the in-memory synthetic store inside the Python process. It does not circulate the pack.

A flow that adds a send action is outside this starter.
