# Architecture

Sensitive Data Redaction Agent, Experiment 08. Catalogue ID O005.

A caller passes one text. Python proposes spans for UK identifiers. A privacy reviewer approves the proposal before anyone releases it. The agent does not release it, and the proposal says it is not anonymised.

![Architecture diagram titled UK identifier PII gateway. A caller passes one text. Deterministic detectors propose spans. A privacy reviewer approves before any human release. The agent has no release or send.](architecture_diagram.png)

```mermaid
flowchart LR
    subgraph caller [Caller]
        A[Another experiment or a reviewer]
    end

    subgraph gateway [Gateway]
        B[One text]
        C[Deterministic detectors]
        D[Optional model suggestion, off by default]
        E[Proposal and DPO audit log]
    end

    subgraph decision [Decision]
        F[Privacy reviewer approves the redacted output]
    end

    subgraph blocked [Not available to the agent]
        G[Release or send]
        H[Claim the text is anonymised]
        I[Store a token vault]
    end

    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    E --> F
    F -.-> G
    F -.-> H
    F -.-> I
```

The dotted lines are not tools. Approval does not enable them.

## What runs where

| Step | Where it runs | Model allowed? |
| --- | --- | --- |
| NHS modulus 11, NINO prefix class, IBAN rearrangement | `src/identifiers.py` | No |
| Span detection | `src/detectors.py` | No |
| Proposal, audit record, release refusal | `src/gateway.py` | No |
| Extra spans for names or free text | A caller-supplied adapter. Default `NullModel` | Only if the caller opts in. Still a suggestion |
| Approval | A person, role Privacy reviewer | No |
| Release | The caller's own channel, after approval | No. Not this agent |

Both Copilot Studio harnesses call `propose()` and stop at the same gates. The standard harness is one topic. The GitHub Copilot harness adds an explanation skill. Neither one is a generic PII agent: names, email addresses, and telephone numbers are out of scope unless a model suggestion is applied, and a suggestion is still not anonymisation.

## What the audit record keeps

A hash of the input, the character count, the caller id, the pinned rules date, and one row per finding with offsets, detector, and checksum. Not the matched characters. A reversible map is a different object, returned only when asked for, and not written to the audit record. This starter persists neither.

## Human approval

The highlighted step on the briefing page is the privacy reviewer's approval. Viewing a proposal and re-running detection do not need a separate approval. Release stays outside the agent after approval. `release()` raises `ReleaseForbidden`.
