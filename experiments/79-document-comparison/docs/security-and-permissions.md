# Security and permissions

Autonomy A0. Reads two synthetic versions. Does not write a document and does not send anything. The permissions file is the same document as `agent-manifest.yaml`.

The named reader confirms the two versions on a separate object. That object has to match the agent-held comparison hash and the agent-held hashes of both document bodies. A sentence in either version is not that step. Confirming the versions does not approve, edit, publish, or send the document.

## What the agent may read

- Two synthetic versions, each with clauses, dates, a marking, retention labels, and a legal-hold flag.
- The pinned directory in `fixtures/directory.json`.
- A separate confirmation, route-seen, or interpretation object.
- Experiment 12 intake, Experiment 08 identifier counts, Experiment 33 `normalise` and `resolve_span`, and Experiment 29 `extract_numbers` and `extract_dates`.

Experiment 38 `compare()` is not called.

## What the agent must not do

- Edit, approve, publish, or send a document.
- Give legal advice or say which version is better.
- Treat text inside a document as confirmation, role, or clearance.
- Apply a caller-supplied directory, taxonomy, or register.
- Drop a protective marking, a legal hold, or a retention label.
- Copy a clause above the reader's directory clearance. The higher marking is kept.
- Copy a distress, safeguarding, whistleblowing, or grievance cue.
- Publish a headcount below 5, or a difference or percentage of that count. Five is a starter threshold, not anonymisation.
- Say "no material change" unless every check in the list was run and none fired.
- Coerce an unreadable date, a bad version count, or a missing baseline to a default.

## Human steps

1. If the text shows distress, safeguarding, whistleblowing, or a grievance, including a paraphrase, the named reader records that they have seen the route.
2. The named reader confirms the two held versions and which one is the baseline. Acknowledgements that the result requires (`versions_seen`, `pins_seen`, and `dates_seen`, `sources_seen`, `markings_seen`, or `material_seen` when those flags are set) have to be the boolean true.
3. The named reader records that they own the interpretation of that hash.

A guest, an inactive person, or a different reader cannot take those steps. A hash from a different comparison cannot. Eight kinds of edit after the comparison is held are rejected by the tests: a changed excerpt, a changed baseline, a flipped legal hold, a dropped retention label, a changed marking, a changed injection signal, a cleared findings list, a flipped route-seen flag, a flipped suppression flag, and a cleared acknowledgement list.

## Data

UK GDPR Article 5(1)(c) was opened on 25 November 2026 and is quoted in `src/sources.py`: "adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed (‘data minimisation’);". Article 22A(1)(a) and the opening of Article 22A(1)(b) were opened the same day and are quoted there. Article 6 and Article 9 were not opened. No lawful basis is asserted. Article 22B, Article 22C, Article 22D, and Article 84B were not opened. S.I. 2026/82 was not opened. This is not a finding that a duty was met, and it is not a finding that a comparison is a significant decision.

Phone numbers, email addresses, dates of birth, postal addresses, personal names, and UK identifiers are counted and not stored. The output is not described as anonymised.

## Unverified product controls

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 25 November 2026. Treat that product behaviour as unverified.

The marking order is a starter rule. The Government Security Classifications Policy was not re-opened. Treating a review date on the question date as stale, including that date, is a starter rule. It is not a statutory period.
