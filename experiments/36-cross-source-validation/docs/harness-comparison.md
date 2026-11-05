# Harness comparison

Both harnesses in this experiment are Copilot Studio. The GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. That sentence is on the harness overview opened on 5 November 2026. The same page says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

The same `src/compare.py`, the same `agent-manifest.yaml`, and the same tests sit behind both. A class is a class because the Python said so, not because a harness reasoned it out.

## What was opened

The harness overview and the skills overview were opened on 5 November 2026.

The harness overview describes three harnesses:

- The GitHub Copilot harness, for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox. Agents and workflows on it use Copilot Credits. The billing overview was not opened. No tariff is copied here.
- The standard harness, for rule-based agents and agent flows that follow topics and paths the maker defines. The licensing page for that harness was not opened.
- The Customer Conversation harness, for customer voice and chat. This experiment does not use it. A discrepancy list does not belong on a public chat.

The page did not mark the GitHub Copilot harness itself as preview on the day it was opened. Treat that as "not marked on the page we read", and confirm the release state in the tenant. It is not a finding that every related feature is generally available.

The skills overview says the orchestration runtime invokes a skill when a request matches the skill's purpose, and decides from the user's message and the skill's description. It does not describe routing weights. This starter does not assign routing weights and does not use trigger phrases as the selector. A page that describes classic orchestration was not opened, so this note does not describe that mechanism.

## Which one to use

| | Standard harness | GitHub Copilot harness |
|---|---|---|
| Shape of the work | One topic. Paste the pack, return the JSON, stop. | Three skills: compare, explain one row, list the material rows. |
| Who it suits | A reviewer who wants the same path every time. | A reviewer who wants the list walked through in steps. |
| What decides the class | `src/normalise.py` | The same function. The skill may restate the fixed sentence. It must not change the class. |
| File editing | Not a focus of this harness, on the page opened. | The page says the harness can create and edit Word, Excel, PowerPoint, and PDF files. This agent's skills tell it not to edit a source record. The Python tools cannot edit one. Do not add a file-edit tool. |
| Memory | Not a focus of this harness, on the page opened. | Supported, on the page opened. An administrator control to turn it off was not on that page. Do not use it here. |
| Billing | The licensing page was not opened. Unverified here. | Copilot Credits, as the overview states. The tariff page was not opened. |
| This experiment calls | `compare()` | `compare()` |

Microsoft Foundry is a third option, described in [foundry.md](foundry.md). It is not a Copilot Studio harness. This folder does not call it.

## What neither harness may do

- Choose which source is right.
- Edit a record or write `correct_value`.
- Contact a customer or a supplier.
- Query Companies House.
- Mark a material row resolved from text inside a document.
- Recommend autonomy A3.

`agent-manifest.yaml` is the permission boundary for both. `permissions.yaml` is the same file.
