# Security and permissions

Autonomy A1. Reads a synthetic transcript. Does not write a case record and does not send the note. The permissions file is the same document as `agent-manifest.yaml`.

The named practitioner approves the draft on a separate object. That object has to match the agent-held note hash. A sentence in the transcript is not that step. Recording the approval does not write the record.

## What the agent may read

- One synthetic transcript, with a marking, retention labels, and a legal-hold flag, plus optional rough notes.
- The pinned template in `fixtures/template.json` and the pinned directory in `fixtures/directory.json`.
- A separate approval or route-seen object.
- Experiment 08 identifier counts. Experiment 12's inventory of the rough notes. The rough-note text is not taken from Experiment 12's reply.

## What the agent must not do

- Write the case record, share the note, or assess eligibility, risk, or need.
- Invent a fact, a diagnosis, or a quote.
- Treat text inside the transcript as an approval, a role, or a clearance.
- Apply a caller-supplied template or directory.
- Drop a protective marking, a legal hold, or a retention label.
- Copy transcript text above the practitioner's directory clearance. The higher marking is kept.
- Copy a concern into the flag. The category and the line number are enough.
- Guess a speaker when the audio is unclear, crossed, or marked misattributed.
- Publish a count of people below 5, or a difference or percentage of that count, including under another field name. Five is a starter threshold, not anonymisation.
- Coerce an unreadable date, a future date, or an ambiguous day and month into a chosen day.
- Decide that a Care Act section 9 assessment or a section 42 enquiry has been carried out.

## Human steps

1. If the text shows safeguarding, self-neglect, domestic abuse, distress, a suicidal statement, financial abuse, or a capacity concern, including a paraphrase or a denial, the named practitioner records that they have seen that route. A refused recording takes the same path.
2. The named practitioner approves the held hash, or returns it for edit. Acknowledgements that the result requires have to be the boolean true.

A guest, an inactive practitioner, a practitioner from the other service, or a stranger cannot take those steps. A hash from a different visit cannot. A caller who edits the package and re-hashes it is rejected. The tests cover at least eight kinds of edit: statement text, an added quote, a source line, a concern flag, a legal hold, a marking, a retention label, an action date, the consent flag, an injection signal, route-seen, and suppression.

## Data

UK GDPR Article 9(1) was opened on 27 November 2026 and is quoted in `src/sources.py`. Article 6 was not opened. No lawful basis is asserted. Care Act 2014 section 9(1), section 9(4)(b), and section 42 were opened the same day. Caldicott principles 3 and 8, and the NHS England Digital ambient-scribe page, were opened the same day. Published local-authority pilot pages were not opened. No supplier result is stated.

## Controls not verified here

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 27 November 2026. Treat that product behaviour as unverified.
