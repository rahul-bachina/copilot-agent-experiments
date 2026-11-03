# Which harness

This note is about running Experiment 29. It is not a decision about which harness an agent under test should use.

Both harnesses call `src/report.py`. The manifest, the fixtures, and the tests are the same. The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework. It is not the GitHub Copilot service. That sentence is on the harness overview opened on 3 November 2026.

| | Standard harness | GitHub Copilot harness |
|---|---|---|
| Shape | One topic. The evaluation owner supplies a bundle and an as-of date. The topic returns JSON and stops. | Three skills: load the passages, score the claims, show the draft. |
| When it fits | The report is the same every time and the path is short. The overview says the standard harness follows the topics and rules the maker defines. | The evaluation owner asks follow-up questions about one claim, one stale flag, or the separate counts. The overview says this harness can take a goal and break it into steps, and that it supports skills and memory. |
| Files | `copilot-studio/` | `skills/` and `docs/github-copilot-harness.md` |
| Billing | Not copied. The licensing page linked from the overview was not opened on 3 November 2026. | The overview says agents and workflows on this harness use Copilot Credits. No quantity is copied. The billing page was not opened. |
| What neither harness does | Approve a threshold, record a release, call Microsoft Foundry, write, or send. | The same. |

The Customer Conversation harness is described on the overview for customer voice and chat. It is not built here.

Memory is a capability the overview states for the GitHub Copilot harness. An administrator control to turn memory off was not on the page. The skills say not to store passages, answers, or the report.

A comparison page that describes maturity, latency, and a Bash container was not opened for this experiment, so those claims are not copied. The overview does not mark the GitHub Copilot harness as preview.

Microsoft Foundry is a separate option, described in `docs/foundry.md`. Neither harness calls it.
