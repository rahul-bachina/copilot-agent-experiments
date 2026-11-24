# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It validates against `schemas/agent-manifest.schema.json`, the permissions schema from Experiment 03.

Autonomy is A0. Sends are off. The only write is the synthetic staging row, after the named resident approves the content hash. Production writes are off. Eligibility, entitlement, an award, a claim, and sending are disabled high-risk actions.

Reads are the pinned pages, the pinned directory, and a separate approval object. Experiment 13 does not decide eligibility and its reply is not copied. Experiment 08 does not describe the text as anonymised. A caller-supplied page, rule, rate, role, or clearance is not the source.

## Product controls

Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights were not opened on 24 November 2026. Treat that product behaviour as unverified. A production deployment would still need them. This repository does not configure them.

## Legislation opened on 24 November 2026

UK GDPR Article 22 on legislation.gov.uk did not show the pre-substitution text. The footnote records the substitution by Data (Use and Access) Act 2025 section 80. Article 22A(1) and Article 22C(2) are quoted in `src/sources.py`. Section 80's commencement note says it was in force at Royal Assent for specified purposes, which section 142(2)(h) limits to the power to make regulations, and in force on 5 February 2026 so far as not already in force by S.I. 2026/82 regulation 2(j). Regulation 5 of that instrument was not quoted.

Equality Act 2010 section 20(3) and section 149(1) are quoted. The section 20 page said it was up to date with all changes known to be in force on or before 23 November 2026. The section 149 page said 22 November 2026. This starter does not decide that either duty was met.

No GOV.UK benefit page was quoted. No figure is stated as a current rate.
