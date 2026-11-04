# Which harness

This note is about running Experiment 33. It is not a decision about which harness a caseworking system should use.

Both harnesses call `src/summarise.py`. The manifest, the fixtures, and the tests are the same. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. That sentence is on the harness overview opened on 4 November 2026.

| | Standard harness | GitHub Copilot harness |
|---|---|---|
| Shape | One topic. The decision-maker supplies a synthetic bundle, the fact keys, and an as-of date. The topic returns JSON and stops. | Three skills: extract a cited reading, check proposed pinpoints, list gaps and contradictions. |
| When it fits | The reading is the same every time and the path is short. The overview says the standard harness follows the topics and rules the maker defines. | The decision-maker asks a follow-up about one sentence, one failed citation, or a gap. The overview says this harness can take a goal and break it into steps, and that it supports skills and memory. |
| Files | `copilot-studio/` | `skills/` and `docs/github-copilot-harness.md` |
| Billing | Not copied. The licensing page linked from the overview was not opened on 4 November 2026. | The overview says agents and workflows on this harness use Copilot Credits. No quantity is copied. The billing page was not opened. |
| What neither harness does | Recommend an outcome, make a disclosure decision, make a credibility finding, accept the summary, call Microsoft Foundry, write, or send. | The same. |

Generative orchestration on the GitHub Copilot harness selects from the skill description. This starter does not assign routing weights and does not use classic-orchestration trigger phrases.

The Customer Conversation harness is described on the overview for customer voice and chat. It is not built here. A case bundle does not belong on a public chat.

Memory is a capability the overview states for the GitHub Copilot harness. An administrator control to turn memory off was not on the page. The skills say not to store bundle text, sentences, or the draft.

A comparison page that describes maturity, latency, and a Bash container was not opened for this experiment, so those claims are not copied. The overview does not mark the GitHub Copilot harness as preview.

Microsoft Foundry is a separate option, described in `docs/foundry.md`. Neither harness calls it.
