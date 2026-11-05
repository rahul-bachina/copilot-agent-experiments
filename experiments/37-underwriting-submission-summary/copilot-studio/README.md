# Standard harness

A build guide for one Copilot Studio topic on the standard harness. It is not an importable solution. The GitHub Copilot harness is a different harness and is not the GitHub Copilot service. See `docs/harness-comparison.md`.

The harness overview opened on 5 November 2026 says the standard harness follows the topics and rules the maker defines. That matches this topic. There is no skill on this path.

## Topic

1. The underwriter pastes one synthetic submission as JSON and types an as-of date.
2. A flow, or a connector the firm builds, runs `python src/summarise.py` with that file and that date. The topic does not pass `--accept`, `--decline`, `--suggest-price`, `--suggest-terms`, `--contact-broker`, `--write-system`, or `--bind`.
3. The topic shows the label `DRAFT FOR THE UNDERWRITER. NOT A COVERAGE OR PRICING DECISION.` and the JSON.
4. The topic stops.

The topic does not accept or decline, suggest a price, email the broker, or write an underwriting system. Generative orchestration is not used on this path. This topic does not list trigger phrases and does not assign routing weights.

Instructions to paste, if a maker adds a prompt beside the topic, are in `system-prompt.md`. The prompt does not add a tool.

## What a maker still has to do

The firm supplies its own environment, its own identity, and its own decision not to connect the topic to a broker mailbox or an underwriting system. This folder does not contain that connection. Billing for the standard harness was not copied. The licensing page linked from the overview was not opened on 5 November 2026.
