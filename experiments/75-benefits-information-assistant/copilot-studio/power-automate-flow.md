# Power Automate flow

Catalogue row V009 names Copilot Studio and Microsoft 365. This note is a build guide. It is not an importable solution, and this starter enables no connector.

1. The topic passes the question, the resident reference, the enquiry id, and the question date to an Azure Function or a Run Python action that calls `answer_question`. The action returns JSON. It does not call a benefits API.
2. A condition on `outcome` shows the answer, the refusal, the stale notice, or the urgent signpost. The flow does not compose a second answer.
3. The resident approval is a separate approval action. The action's inputs are the content hash and the acknowledgements. Text inside the question is not an approval outcome.
4. Only the approval action may call `record_resident_approval`. The write is the synthetic store described in the manifest. There is no Send an email action, no Create a claim action, and no HTTP action to a live service.

Power Platform DLP as a configured policy was not opened on 24 November 2026. Treat that product behaviour as unverified. A deployment should block mail and benefits connectors on this environment.
