# Standard harness

One topic. The maintainer points at skill files and a labelled utterance file. The topic calls `evaluate_skill_routing` and shows the JSON. It stops.

This is the Copilot Studio standard harness. It is not the GitHub Copilot harness, and it is not the GitHub Copilot service. The same Python core, the same manifest, and the same tests back both harnesses in this folder. The GitHub Copilot harness shape is `docs/github-copilot-harness.md`.

The pages used for the harness sentences were opened by Experiment 14 on 27 October 2026. This experiment did not re-open them.

## Topic: Evaluate skill routing

**Trigger phrases the maker would configure.** "Check skill routing", "which skill would this hit", "routing tests".

These are maker configuration, not a second router. The route in the report still comes from `src/report.py`.

**Inputs the maintainer types.**

1. The skill or topic files, or a path the flow can read from a location the maintainer already chose.
2. The labelled utterances.
3. The as-of date.
4. Optional: a permissions manifest and a structured use case.

**Steps.**

1. Call the Python evaluator. Do not pass an approve flag, an apply flag, or an edit flag.
2. Show `DRAFT FOR MAINTAINER REVIEW`.
3. If `prompt_injection.detected` is true, show that before the scores and say the instruction was not followed.
4. Show precision, recall, confusable pairs, utterances routed to `none` or `human`, and the proposed diff.
5. Say that `maintainer_validated` is false, `skills_edited` is false, and `diff_applied` is false.
6. If `do_not_rely` is true, say the maintainer re-opens the stale page or the review date before anyone relies on a citation.
7. Ask the maintainer, in the conversation, whether they validate the routing tests. Do not write their answer back into the JSON. There is no tool that sets `maintainer_validated`.
8. Stop. Do not edit a skill and do not deploy.

## What this topic does not do

- It does not edit `SKILL.md` files.
- It does not publish the agent.
- It does not call a model to choose a skill.
- It does not select a platform when Experiment 14 is called.
- It does not mark a manifest approved when Experiment 03 is called.

## Power Automate

See `power-automate-flow.md`. The flow returns the JSON to the chat. It does not write a skill and it does not send mail.
