# Power Automate flow

A build note. Not an importable flow.

| Input | What it is |
| --- | --- |
| `request` | The JSON the reviewer pasted. `synthetic` must be true. |
| `as_of` | The ISO date the question is about. Not today, unless that is the date they asked about. |

The flow calls the same Python core, or a later hosted copy of `extract_form`, and returns the JSON to the topic.

It does not create a Dataverse row. It does not send mail. It does not call a bank. It does not call Document Intelligence. A team that later wants a production write adds that step as a separate, reviewer-confirmed change, and updates the manifest first. This starter does not include it.

`record_reviewer_approval` is the only write, and it writes the synthetic store inside the process. The flow does not call it unless the topic has collected the separate approval object.

Power Platform DLP should block connectors this flow does not need. This note does not create the policy.
