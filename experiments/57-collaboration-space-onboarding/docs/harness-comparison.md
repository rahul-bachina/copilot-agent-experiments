# Which harness

Both harnesses call `src/onboard.py`. Neither one sends a Microsoft Graph request. The comparison below uses the harness overview opened on 16 November 2026.

| | Standard harness | Microsoft Copilot harness, packaged here under the brief's GitHub Copilot harness name |
| --- | --- | --- |
| What Microsoft's page says | It follows the topics and rules the maker defines. | It is for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox. |
| Billing | The overview points to a licensing page. This note does not quote a price. | Copilot Credits. The overview states no price. |
| Where the instructions live | `copilot-studio/` | `skills/*/SKILL.md` |
| What stays in Python | Labels, least privilege, guest policy, the approval object, and the simulated Graph record. | The same. |

The page opened on 16 November 2026 does not use the words GitHub Copilot harness. Treating this package as that harness is the brief's name for the Microsoft Copilot harness. Older wording that the harness is not the GitHub Copilot service is unverified against the page opened on this date.

Microsoft Foundry is optional and is not required to run the core. See `docs/foundry.md`. No Foundry resource is deployed by this starter.
