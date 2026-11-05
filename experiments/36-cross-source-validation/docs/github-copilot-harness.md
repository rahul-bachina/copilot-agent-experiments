# GitHub Copilot harness

This is the Copilot Studio GitHub Copilot harness, opened on the harness overview on 5 November 2026. It is a Microsoft Copilot Studio authoring and orchestration framework, not the GitHub Copilot service.

Use it when a reviewer wants the discrepancy list walked through in steps. The class still comes from `compare()`. The skills do not decide it.

## Skills

| Skill | When the description says to use it |
|---|---|
| `compare-source-fields` | A synthetic pack needs each shared field classified. |
| `explain-discrepancy` | One classified row needs the fixed explanation restated. |
| `list-material-discrepancies` | The reviewer wants only the material rows, still unresolved. |

The skills overview opened on 5 November 2026 says a skill is a name, a description, and instructions, and that the orchestration runtime invokes a skill when a request matches the skill's purpose. Selection is from the user's message and the skill's description. This starter does not assign routing weights. It does not use trigger phrases as the selector. A page that describes classic orchestration was not opened.

The description in each `SKILL.md` is a single line and starts with "Use when", so the runtime has a purpose to match. This experiment does not claim that Microsoft requires the extra approval headings. Those are the control for this starter.

## Tool contract

The agent may call `compare_sources`. It may restate a row that call already returned. It may not call `choose_source`, `edit_record`, `contact_party`, `lookup_register`, or `recommend_a3`. Those functions raise. `record_reviewer_resolution` is not an agent tool. A reviewer who wants a choice recorded writes the resolutions file outside the skill.

## Approval gates

1. Showing the list does not resolve a material row.
2. The reviewer resolves every material discrepancy.
3. The reviewer re-opens a stale document or a stale pinned page before relying on the list.
4. Any correction of a record happens outside this agent.
5. A data protection officer confirms a lawful basis before live personal data. This starter does not choose one.

## Memory and files

The harness overview says this harness supports memory and can create and edit files. Do not write field values into memory. Do not create or edit a file that would change a source record. An administrator control to turn memory off was not on the page opened on 5 November 2026. That control is unverified here.

## Billing

The overview says agents and workflows on this harness use Copilot Credits. The billing overview was not opened. No tariff is stated.
