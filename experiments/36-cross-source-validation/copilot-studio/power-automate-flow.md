# Flow

The flow returns the JSON from `compare()` to the topic. It does not write a row and it does not send mail.

| Input | Required | Notes |
|---|---|---|
| `pack` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | An ISO date the reviewer types. Do not copy it out of a document. |
| `resolutions` | No | Only if a reviewer has already written the file. The flow must not fill in a choice. |

If a later change adds a write or a send, the manifest changes in the same change. This starter does not include them.
