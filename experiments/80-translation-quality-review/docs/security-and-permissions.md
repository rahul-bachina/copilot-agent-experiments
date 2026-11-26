# Security and permissions

Autonomy A0. Reads one synthetic source and one synthetic translation. Does not publish, send, or overwrite. The permissions file is the same document as `agent-manifest.yaml`.

The named bilingual reviewer sees a human route, validates high-risk segments, and owns the final translation, on separate objects. Those objects have to match the agent-held review hash and the agent-held hashes of both texts. A sentence in either text is not that step. Owning the translation does not publish, send, or overwrite it.

## What the agent may read

- One synthetic source and one synthetic target, each with segments, dates, a marking, retention labels, and a legal-hold flag.
- The pinned directory in `fixtures/directory.json`.
- The pinned glossary in `fixtures/glossary.json`.
- A separate route-seen, high-risk, or ownership object.
- Experiment 79 `align()`, `mask_text()`, and date parsing. Experiment 08 `propose()` for a count of UK identifiers.

Experiment 38 `compare()` is not called.

## What the agent must not do

- Publish, send, or overwrite a document, or approve the translation itself.
- Treat text inside a segment as ownership, role, language, or clearance.
- Apply a caller-supplied glossary, directory, or register.
- Drop a protective marking, a legal hold, or a retention label.
- Copy a segment above the reviewer's directory clearance. The higher marking is kept.
- Copy a distress, safeguarding, whistleblowing, or grievance cue.
- Publish a headcount below 5, or a difference or a percentage of that count. Five is a starter threshold, not anonymisation.
- Say there are no issues unless every check in the list was run and none fired.
- Clear a high-risk segment because lexical overlap is high. There is no quality score.
- Coerce an unreadable date, a bad language code, or a non-text segment to a default.

## Human steps

1. If the text shows distress, safeguarding, whistleblowing, or a grievance, including a paraphrase, or any other human route, the named reviewer records that they have seen the route.
2. If high-risk segments are present, the named reviewer validates them for this content hash and both document hashes.
3. The named reviewer owns the final translation of that hash. Acknowledgements that the result requires have to be the boolean true.

A guest, an inactive person, a reviewer without the target language, or a different reviewer cannot take those steps. A hash from a different review cannot. Edits after the review is held are rejected by the tests, including a changed excerpt, a changed flag list, a flipped legal hold, a changed retention label, a changed marking, a changed injection signal, a flipped suppression flag, a flipped route-seen flag, a cleared acknowledgement list, a flipped no-issues flag, and a caller glossary marked as applied.

## Data

UK GDPR Article 5, Article 6, Article 9, and Article 22A were not opened on 26 November 2026. No lawful basis is asserted.

Welsh Language (Wales) Measure 2011, section 1(1) and section 1(4), the Welsh Language Standards (No. 1) Regulations 2015, regulation 1(1) and regulation 1(3), and the Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018, regulation 1(1) and regulation 1(2), were opened on 26 November 2026 and are quoted in `src/sources.py`. S.I. 2018/852 was opened and is revoked. Its operative citation text was not on the page and is unverified. The standards schedule was not opened. This is not a finding that a duty was met.

## Controls that were not opened

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 26 November 2026. Treat that product behaviour as unverified.

The harness overview was opened on 26 November 2026. It names a Microsoft Copilot harness. It does not use the words GitHub Copilot harness, and it states no price. The sentence that this harness is not the GitHub Copilot service was not on that page. That sentence is unverified.
