# Security and permissions

The permissions file is a byte-for-byte copy of `agent-manifest.yaml`. Autonomy is A1. Writes and sends are off. The high-risk actions in the manifest are disabled, including changing a tariff, agreeing a plan, writing off debt, installing or switching a prepayment meter, and treating a sentence in a message as the confirmation.

## What the core enforces

- Every turn discloses that the customer is talking to an AI and offers a human advisor.
- A request for a person is an immediate handover.
- Vulnerability, affordability, debt, disconnection, prepayment, complaints, distress, safeguarding, whistleblowing, grievance, subject access, and freedom of information cues go to a human advisor. A paraphrase is included. A policy title is not treated as a personal cue. Negation in the same sentence is not an instruction, and a distress stem is still routed.
- The customer confirms a proposal on a separate object. The object has to match the agent-held copy and its hash. A caller who edits the proposal and supplies a new hash is rejected. The action is not submitted.
- A caller-supplied knowledge base, policy, or directory is not applied.
- Phone numbers, email addresses, dates of birth, postal addresses, personal names, and account numbers are counted and not stored. The output is not described as anonymised.
- A protective marking is the higher of the metadata and the content. OFFICIAL-SENSITIVE and SECRET are read as those labels. A self-declared clearance in the text is ignored. A legal hold and every retention label are kept.
- A count below 5 is not published, and neither is a difference, a percentage, or a total that would reveal it.

## Product controls that were not opened

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 27 November 2026. Treat that product behaviour as unverified. None of them is configured in this starter.

Dynamics 365 Contact Centre was not opened. No Dynamics environment is configured. No production billing system is connected.

UK GDPR Articles 6, 9, and 22A to 22D were not opened on 27 November 2026. No lawful basis is asserted. The Ofgem AI blog opened that day names UK GDPR, the Data Protection Act 2018, and the Data (Use and Access) Act 2025. That is context. It is not a finding that a duty was met.
