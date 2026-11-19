# Microsoft Copilot harness

Catalogue row L001 names this harness first. The layout is the skills folder the common brief calls the GitHub Copilot harness.

On 19 November 2026 the harness overview called the reasoning-heavy harness the Microsoft Copilot harness. It described skills, memory, file creation, and a sandbox, and the prose said it uses Copilot Credits. It did not use the words GitHub Copilot harness. It stated no price. Older wording that this harness is not the GitHub Copilot service is unverified against that page.

## Skills

| Skill | When |
| --- | --- |
| `review-contract-clauses` | A lawyer wants the quoted comparison. No seen step yet. |
| `route-to-lawyer` | The outcome is `human_route`. The cue is not copied. |
| `record-lawyer-seen` | The directory lawyer records that they have seen this contract hash and this deviations hash. |

The skill descriptions say when to use the skill. They do not list selection phrases and they do not assign weights.

## Gates

The gates are the manifest, not the skill text. `record_lawyer_seen` checks the directory role, the item name, the decision `seen`, and both hashes. `pins_seen` and `playbook_seen` have to be the boolean `true` when those flags are set. A sentence in the contract is not a gate.

Do not give legal advice. Do not redline. Do not accept terms. Do not sign. Do not send.
