# Architecture

`triage()` in `src/triage.py` is the only path that classifies an exception. Copilot Studio, on either harness, calls that function and stops. A model is not in the path. Experiment 12 inventories the file. Experiment 08 proposes UK identifier spans from inside that intake. This experiment does not copy either implementation.

```
AP reviewer
    |
    | one synthetic case, as-of date
    v
Copilot Studio (standard topic, or GitHub Copilot harness skills)
    |
    v
triage()                         ---- no network, no model
    |
    +-- Experiment 12 intake()   ---- hash, keyword class, injection, dates
            |
            +-- Experiment 08 propose()
    |
    v
draft JSON
    exceptions, evidence, resolution code
    prompt-payment arithmetic
    VAT field checklist
    all payment flags false
    |
    v
AP reviewer reads the draft
    |
    +-- if bank_detail_change: Bank-detail verifier acknowledges the route
    |       (does not change the bank record)
    v
AP reviewer approves, returns, or rejects the resolution
    |
    v
a person, outside this agent, in the finance system
    nothing here posts, holds, pays, or updates a bank account
```

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py`. Matplotlib is used only for that script. It is not a runtime dependency.

## What is deterministic

| Step | Where |
|---|---|
| File inventory, hash, keyword class, document date | Experiment 12 |
| UK identifier proposal | Experiment 08, called by Experiment 12 |
| Labelled invoice fields | `triage()`, visible lines only |
| Exception class and resolution code | `triage()`, closed lists |
| 30-day arithmetic | `triage()`, dates the caller typed, not dates hidden in the invoice |
| VAT field checklist | `triage()`, against the pinned notice sections |
| Prompt-injection record | `src/ap_injection.py`, plus Experiment 12's own scan |

## What is not a tool

Posting, approving, holding, and paying an invoice. Changing supplier bank details. Sending a question. Writing a finance record. Deciding that regulation 113 of the Public Contracts Regulations 2015 still applies. It does not, on the legislation.gov.uk page retrieved 28 October 2026.

## Human approval

| Point | Who | What the code does |
|---|---|---|
| Approve, return, or reject the resolution | AP reviewer | `record_ap_reviewer_decision` checks the role. The agent must not call it. Approval does not post or pay. |
| Bank-detail route | Bank-detail verifier | Required before that approval when the flag is set. It does not verify the account and does not change it. |
| Stale source pin or document date | AP reviewer | Approval is refused until a person passes `acknowledge_stale`. |
| Unread file or bad checksum | AP reviewer | Approval is refused. |
| Anything in the finance system | A person outside this agent | No tool. |
