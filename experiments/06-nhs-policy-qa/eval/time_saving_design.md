# Measured time-saving evaluation

Experiment 06, catalogue ID M003. This is the design a trust or another public body would run. The numbers shipped in `time_observations.json` are synthetic fixture arithmetic so the scorer can be tested. They are not observations of staff, and they are not the NHS trial figure.

## What is not the endpoint

NHS England's announcement of 8 June 2026 says a trial of more than 30,000 staff in 90 organisations found that administrative support could save an average of 43 minutes per person per day or more. The page does not describe the measurement method. A Microsoft feature dated 21 October 2026 says participants "reported" that saving. A reported minute is not this design's endpoint, and 43 minutes is not read by `src/time_saving.py`.

A field named `minutes_saved`, `minutes_saved_self_report`, `self_reported_minutes`, `self_reported_minutes_saved`, or `hours_saved` is rejected. The row does not enter the median, even if it also has timestamps.

## Primary endpoint

Median of paired differences in elapsed seconds: time on the manual arm minus time on the agent arm.

Elapsed seconds are computed from two timestamps recorded by the test harness, not typed by the participant:

- `shown_at`, when the question was shown;
- `submitted_at`, when the participant submitted the answer they would rely on.

Both timestamps need a timezone. `submitted_at` earlier than `shown_at` is an error, not a zero.

The median is the middle value. For an even count it is the mean of the two middle values.

## Which items count

An item counts only when both of these are true:

- `agent_outcome_correct` is true (the outcome matches the gold label: answered, I don't know, stale withheld, conflict, or the right refusal);
- `citations_grounded` is true (every citation is an approved, in-date clause, or the outcome is a refusal or an "I don't know" with no citation).

Anything else is excluded and counted in `n_excluded_ungrounded`. A fast wrong answer is not a saving. A stale clause shown as current is not a saving. A clinical answer is not a saving.

## Two arms

Same questions, same approved register, same as-of date.

| Arm | What the participant does | What is timed |
| --- | --- | --- |
| Manual | Searches the policy files with no agent | `shown_at` to `submitted_at` |
| Agent | Uses the staff Q&A and submits the answer they would rely on | `shown_at` to `submitted_at` |

The agent's compute time is not the endpoint. A sub-second call can still sit inside a slow human task, and a slow call is not a benefit if the citation is wrong. The harness records the human interval. It does not ask "how many minutes did that save you?"

Order is crossed: half the participants see the manual arm first. The design does not claim that has been done in this repository.

## Secondary checks

These are reported beside the median. They are not folded into a single score.

- Proportion of items with the correct outcome.
- Stale-policy misses: a stale clause returned as an answer that may be relied on.
- Conflict misses: one side of a disagreement returned as the rule.
- Clinical misses: a clinical question that receives policy text.
- Unanswered-log completeness: every "I don't know" and stale withholding has a log entry with `persisted` false in this starter.

## What this repository runs

`eval/evaluate.py` does two separate things.

1. It runs `src/answer.py` on `synthetic_dataset.json`. That is a phrase-matcher smoke test. It is not a model score.
2. It scores `time_observations.json` with `src/time_saving.py`. Each row is marked as a synthetic fixture. The worked example has seven grounded pairs. Their differences in seconds are 90, 120, 140, 160, 180, 200, and 240. The median is 160. One self-report row and one ungrounded row are present so the scorer has to drop them. If either entered the median, 160 would move.

A real study replaces `time_observations.json` with harness logs from both arms. Until that file is real observations, the median in the smoke report is fixture arithmetic.

## Sample size

This design does not invent a required headcount. A team that runs it should say, before looking at the median, how many paired items it will collect, from which staff groups (HR, finance, procurement, IT, estates), and that clinical questions are in the set so refusals are timed as well. Exclusions are part of the result, not a footnote after a disappointing number.
