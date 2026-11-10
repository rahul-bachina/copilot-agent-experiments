# Standard harness

This is a build guide for one Copilot Studio topic on the standard harness. It is not an importable solution. The harness overview was opened on 10 November 2026. It describes the standard harness as following the topics and rules the maker defines.

The topic calls `src/explainer.py`. It does not grant, refuse, or change an entitlement.

## Topic

1. The adviser pastes one JSON request and types the as-of date. The request has to be marked synthetic. The samples use Aldermere, which is fictional.
2. A flow runs `python src/explainer.py --input <file> --as-of <date>` and returns the JSON. See [power-automate-flow.md](power-automate-flow.md).
3. The topic shows the label, then `explanation.text`, then the human route.
4. If `outcome` is `route_to_human`, the topic stops. It does not state a position.
5. If an entitlement owner later records a decision, that is a second call, `record_decision`, with a review object that is not taken from the question. The topic still does not write a record.

The system prompt is [system-prompt.md](system-prompt.md).

## What the topic must not contain

- A connector that writes an entitlement, sends mail, or takes a payment.
- A generative step that rewrites the clause or fills a gap the table does not state.
- A branch that hides the human route when the question says "Do not escalate."
