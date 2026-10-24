# Agent Autonomy Levels

This document defines the autonomy levels used in agent manifests across this repository.

## Overview

Autonomy levels describe how much independent action an AI agent can take without human approval. This repository permits only levels **A0**, **A1**, and **A2**. Level A3 (fully autonomous) is **not permitted** in this catalogue.

## Level definitions

| Level | Name | Description |
|-------|------|-------------|
| **A0** | Read-only analysis | Agent performs analysis and returns results. No capability to take actions, even with approval. |
| **A1** | Human approves all | Agent can suggest actions, but a human must approve every action before it executes. |
| **A2** | Human approves high-risk | Agent can take low-risk actions autonomously; high-risk actions require human approval. |
| **A3** | Fully autonomous | Agent acts independently without human approval. **Not permitted in this repository.** |

## Detailed definitions

### A0: Read-only analysis

The agent:
- Accepts input and produces analysis or recommendations
- Returns output to a human for review
- Has no capability to take external actions
- Cannot write to systems, send communications, or modify records

**Example use case:** An agent that analyses text and returns a classification, but cannot act on it.

### A1: Human approves all

The agent:
- Can suggest any action within its permitted scope
- **All** actions require explicit human approval before execution
- Human reviews each action individually
- Agent cannot proceed without approval

**Example use case:** An agent that drafts emails for a human to review and send, or suggests case routing for a human to confirm.

### A2: Human approves high-risk

The agent:
- Can take **low-risk** actions autonomously (e.g., logging, internal queries)
- **High-risk** actions require human approval

High-risk actions in this repository are defined as:
1. **Approve/reject** — Approving or rejecting requests, applications, claims
2. **Regulated decisions** — Decisions subject to regulatory requirements (e.g., Consumer Duty, FOI responses, benefits determinations)
3. **Production record changes** — Creating, updating, or deleting records in production systems
4. **External sends** — Sending emails, messages, letters, or other external communications
5. **Spend/transact** — Spending money, authorising payments, executing financial transactions

Each high-risk action must have a named human approver in the agent manifest.

**Example use case:** An agent that can query internal systems and log activities autonomously, but requires manager approval to send customer communications.

### A3: Fully autonomous (NOT PERMITTED)

An A3 agent would:
- Act independently without human approval
- Make decisions and execute actions autonomously
- Potentially take high-risk actions without oversight

**This level is not permitted in this repository** because:
- UK public sector and regulated private-sector contexts require human oversight
- Consumer Duty, GDPR, FOI, and other regulations require accountability
- Autonomous agents present unacceptable risk for the use cases in this catalogue

## Choosing an autonomy level

| If the agent... | Use level |
|-----------------|-----------|
| Only analyses and returns results | A0 |
| Suggests actions for human execution | A1 |
| Takes some actions, humans approve others | A2 |
| Acts fully independently | Not permitted |

## Schema enforcement

The agent manifest schema (`schemas/agent-manifest.schema.json`) enforces:
- Autonomy level must be `A0`, `A1`, or `A2`
- `A3` is rejected by the schema
- For A2 agents, each high-risk action must be either disabled or have explicit human approval with a named approver

## References

- [Agent Manifest Schema](../schemas/agent-manifest.schema.json)
- [CONTRIBUTING.md](../CONTRIBUTING.md)

---

*Last updated: 2026-10-24*
