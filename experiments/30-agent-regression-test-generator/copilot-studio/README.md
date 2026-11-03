# Copilot Studio standard harness

Experiment 30 on the standard harness is one topic. The maintainer points at a synthetic bundle. The topic calls `src/generate.py`. It shows the JSON. It stops.

The standard harness follows topics and rules the maker defines. That is the harness overview, opened on 3 November 2026. There is no skill on this path. The GitHub Copilot harness build is `docs/github-copilot-harness.md`. It is a Copilot Studio authoring framework, not the GitHub Copilot service.

## Topic

Name: Draft regression cases.

Trigger for this topic, if the agent uses classic orchestration: the maintainer asks to draft regression cases for one bundle.

If the agent uses generative orchestration, the topic description is the selector. The page "Orchestrate agent behavior with generative AI", opened on 3 November 2026, says generative orchestration selects topics based on the description of their purpose, and that the page describes the standard harness. Do not add a routing weight. Do not tell the maker that a trigger phrase is what generative orchestration matches.

Suggested description: Draft regression cases from one synthetic manifest, skill files, a tool contract, and failure or change notes. Use when the maintainer wants a proposed-changes pack and pull-request text. Do not merge, push, or edit the agent under test.

## Nodes

1. Ask for the bundle path and the as-of date. Both are required. Do not browse a tenant.
2. Run `python src/generate.py --bundle <path> --as-of <date>` on a machine the organisation controls. Capture stdout.
3. If the exit code is 2, show the error and stop. Do not retry with `--merge`, `--push`, `--approve`, `--apply`, or `--open-pr`.
4. Show the label, the summary, and the case table from the JSON. Do not recompute the counts.
5. Stop. Say that a maintainer approves the tests and any pull request outside this topic.

## What this topic does not call

- A merge, a push, or a pull-request API.
- A write into the agent under test.
- Microsoft Foundry.
- A model score.

The permissions manifest stays the control. Writes are disabled. Sends are disabled.

## Knowledge

Do not paste a live agent definition into knowledge. The sample bundle is synthetic. Halebridge Borough Council is fictional.
