# Microsoft Copilot harness

Packaged here in the layout the common brief calls the GitHub Copilot harness. On 23 November 2026 the harness overview used the name Microsoft Copilot harness. See [harness-comparison.md](harness-comparison.md).

Skills:

- `skills/explain-retention-advice/SKILL.md` calls `advise_retention()`.
- `skills/flag-retention-blockers/SKILL.md` reads the same JSON when a hold, an open matter, a missing date, personal data, or distress is present.
- `skills/record-advice-seen/SKILL.md` calls `record_advice_seen()` for the directory records owner or legal owner and this advice hash.

The skill `description` is one line and says when to use the skill. These files do not list phrases for selection and do not assign weights.

The model may narrate. It may not invent a schedule line, replace an unreadable date with today, or treat a sentence in the note as approval. If the core is unavailable, the skill stops.

File creation, where the tenant enables it, is not a disposal and not a send. A file of the JSON is still advice. It does not change the inventory.

Memory, where the tenant enables it, must not store the note, a phone number, or a clearance sentence. The advice hash and the series id are enough.
