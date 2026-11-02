# Power Automate flow

A flow that calls the local evaluator and returns JSON to the topic. It does not write a skill, a topic, Dataverse, or a mailbox.

This note is a design for the standard harness. It is not a deployed flow. No environment was connected while this file was written.

## Trigger

The Copilot Studio topic calls the flow with:

- `bundle_json`, the skills and the labelled utterances the maintainer pasted
- `as_of`, a date the maintainer typed

The flow does not accept `approve`, `apply`, `edit_skills`, or `deploy`.

## Actions

1. Run the Python command `src/report.py` with `--bundle` and `--as-of` only. A hosted flow would call the same function. This repository does not ship that host.
2. Return the JSON to the topic.
3. Stop.

There is no action that updates a file, sends mail, or starts a deployment.

## Human step, outside the flow

The topic asks the maintainer whether they validate the routing tests. The flow does not receive that answer. `maintainer_validated` stays false. The maintainer validates routing tests in their own review, then edits a skill in their own files, or does not.

## If the command exits 2

The flags that edit, apply, validate, or deploy were passed. The flow returns the error text and does not retry with those flags removed in order to force a success. It stops.
