# Microsoft Copilot harness

Catalogue row L002 names Microsoft Foundry and Azure first. The layout here is the skills folder the common brief calls the GitHub Copilot harness.

On 20 November 2026 the harness overview called this runtime the Microsoft Copilot harness. It described skills, memory, file creation, and a sandbox, and the prose said agents and workflows on it use Copilot Credits. The page stated no price. It did not use the words GitHub Copilot harness. Older wording that the harness is not the GitHub Copilot service was not on that page. That point is unverified.

## Skills

| Skill | When |
| --- | --- |
| `draft-change-briefing` | A compliance owner wants the quote, the dates, and the candidate policies. |
| `route-to-compliance-owner` | The core has flagged distress, a grievance, or a disclosure. |
| `record-owner-seen` | The directory compliance owner records the three hashes. |

The skill `description` is one line and says when to use the skill. These files do not list phrases for selection and do not assign weights.

## Gates

The gates are the same as the standard harness and the same as `agent-manifest.yaml`.

1. Read the briefing. No separate approval. `human_approval` stays null.
2. A distress, grievance, or disclosure route is seen as that route. The cue text is not copied.
3. The owner sets `flags_seen` to the boolean true when the notice is stale, withdrawn, superseded, or undated, or a date could not be read, or the consultation length is below the register figure.
4. The owner sets `pins_seen` to the boolean true. Section 138L was not opened. The pin is not confirmed.
5. The owner sets `sources_seen` to the boolean true when the pasted text or the caller register differs from the pin.
6. The owner records `seen` for this publication hash, this briefing hash, and this questions hash.
7. Deciding applicability, changing a policy, and sending are not tools.

A string is not coerced to true. A hash from another briefing is not reused. Changing the quote after the step fails `verify_seen()`.
