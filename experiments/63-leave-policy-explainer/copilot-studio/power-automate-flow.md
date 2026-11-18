# Flow

One flow. It does not book leave.

1. Receive the question, the scope reference, and the date the question is about.
2. Call `explain()` with the synthetic policy set, the baseline, the scope, the directory, and the as-of date.
3. Return the JSON to the topic.
4. Stop.

There is no branch that writes to a leave system, sends mail, or calculates pay. A seen-step, if HR uses one later, is a separate flow the agent cannot start, and it checks the explanation hash.
