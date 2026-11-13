# Flow note

This is not a shipped Power Automate flow. It is the boundary a later flow would have to keep.

A flow may pass the synthetic index, the query, and the selection object into `find_documents`, and return the JSON to the topic.

A flow must not:

- Call Microsoft Graph `POST /search/query`, Work IQ, or Purview from this sample.
- Add a location the selection object does not list.
- Use an application permission to read a library the user cannot read. The query API page opened on 13 November 2026 lists application Files.Read.All. Whether that permission is trimmed to one user was not stated. This sample does not use it.
- Move, delete, share, or change permissions, including with Work IQ.Act. The permissions reference describes that delegated permission as read and change. It is not requested here.
- Send mail with the result.
- Write the extract of a withheld file into a run history.

If a connector is added later, Power Platform DLP is the place an administrator blocks it. A configured DLP policy was not opened on 13 November 2026. Treat that product behaviour as unverified.
