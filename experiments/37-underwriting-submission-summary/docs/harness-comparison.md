# Which harness

This note is about running Experiment 37. It is not a decision about which harness an underwriting system should use.

Both harnesses call `src/summarise.py`. The manifest, the fixtures, and the tests are the same. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. That sentence is on the harness overview opened on 5 November 2026.

| | Standard harness | GitHub Copilot harness |
|---|---|---|
| Shape | One topic. The underwriter supplies a synthetic submission and an as-of date. The topic returns JSON and stops. | Three skills: summarise the submission, check a proposed pinpoint, list fields that are not stated. |
| When it fits | The summary is the same every time and the path is short. The overview says the standard harness follows the topics and rules the maker defines. | The underwriter asks a follow-up about one fact, one failed citation, or a gap. The overview says this harness can take a goal and break it into steps, and that it supports skills and memory. |
| Files | `copilot-studio/` | `skills/` and `docs/github-copilot-harness.md` |
| Billing | Not copied. The licensing page linked from the overview was not opened on 5 November 2026. | The overview says agents and workflows on this harness use Copilot Credits. No quantity is copied. The billing page was not opened. |
| What neither harness does | Accept or decline, suggest a price or terms, contact the broker, write an underwriting system, bind cover, call Microsoft Foundry. | The same. |

The generative-orchestration guidance opened on 5 November 2026 says the planner can invoke a topic when its described purpose matches the user's need, and also by trigger phrases. It says tool names carry more weight than descriptions. It does not describe numeric routing weights. This starter does not list trigger phrases and does not assign routing weights. Whether the GitHub Copilot harness uses that same planner was not stated on the harness overview. That link is unverified.

The Customer Conversation harness is described on the overview for customer voice and chat. It is not built here. A broker submission does not belong on a public chat.

Memory is a capability the overview states for the GitHub Copilot harness. An administrator control to turn memory off was not on the page. The skills say not to store submission text, facts, or the draft.

A comparison page that describes maturity or a Bash container was not opened for this experiment, so those claims are not copied. The overview does not mark the GitHub Copilot harness as preview.

Microsoft Foundry is a separate option, described in `docs/foundry.md`. Neither harness calls it. The catalogue row names Microsoft Foundry beside the GitHub Copilot harness. This folder does not call Foundry.
