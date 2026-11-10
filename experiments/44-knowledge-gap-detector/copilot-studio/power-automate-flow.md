# Flow

A build note, not an importable flow. No connector in this note publishes an article.

1. Trigger: the knowledge manager pastes a pack and an as-of date in the topic.
2. Condition: `synthetic` is true. Otherwise return the refusal JSON and stop.
3. Action: run `python src/gaps.py --input <pack> --as-of <date>` on a machine that already has Experiments 08, 21, and 40 beside this folder. This repository does not host that machine.
4. Parse the JSON. Show `gaps`, `findings`, and `outlines`. Do not show a field that is not in the JSON.
5. Stop.

A second flow may accept `confirm_gap`, `reject_gap`, or `defer` with `actor` `knowledge_manager` and call `record_confirmation`. If `published` is true in the result, the flow is wrong. It is false in this starter.

Do not add a Dataverse "publish knowledge article" action, a Fabric write, or a mail action to either flow. Those are not tools of this agent.
