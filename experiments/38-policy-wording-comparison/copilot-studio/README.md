# Copilot Studio standard harness

One topic. The wording specialist pastes a synthetic pack and the as-of date. A flow calls `compare()` and returns the JSON. The topic stops.

This is a build guide, not an importable solution. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. The standard harness is the one for a single, predictable call. The overview opened on 6 November 2026 describes the standard harness as following the topics and rules you define.

The generative-orchestration guidance opened the same day says a described purpose can select a topic, and that tool names carry more weight than descriptions. This topic does not list trigger phrases and does not assign routing weights. Whether that guidance applies to a topic the author forces with a button was not stated. That link is unverified.

## Topic

1. Ask for the pack and the as-of date. Refuse a pack that is not marked synthetic.
2. Call the Python comparison. Do not pass a favourability, recommendation, endorsement, broker, write, or coverage flag.
3. Show the label `DRAFT FOR THE WORDING SPECIALIST. NOT A COVERAGE OPINION AND NOT A RECOMMENDATION.`
4. Show the rows. A missing topic is `not stated`. Do not fill it.
5. Stop. The wording specialist validates every interpretation outside the topic.

There is no action after the draft. The instructions to paste are in [system-prompt.md](system-prompt.md).
