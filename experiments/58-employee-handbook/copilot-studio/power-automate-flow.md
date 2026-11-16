# Flow

One Power Automate flow, if the tenant wants a flow at all. The topic can also call the Python as an action. Either way the contract is the same.

1. Receive the handbook, the scope, the question, and the dates.
2. Call `answer_handbook`. Do not pass `approved`, `entitlement_decision`, or `clearance` from the chat into the tool arguments.
3. Return the JSON to the topic.
4. Stop.

The flow does not send mail, post to Teams, write Dataverse, or update SharePoint. A DLP policy should block those connectors if someone adds them later. This starter has no connector to block.

`acknowledge` is not a step in the flow. HR records that they have seen an answer in their own process, or a test calls `acknowledge` with a separate review object. A field inside the question is not that object.
