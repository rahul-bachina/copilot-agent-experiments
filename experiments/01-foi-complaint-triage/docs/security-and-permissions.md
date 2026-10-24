# Security and Permissions Guide

**FOI Complaint Triage Agent — Experiment 01**

This document explains the agent's permissions manifest (`agent-manifest.yaml`) for governance, information security, and data protection audiences. It maps each section to relevant Microsoft security controls and explains how the agent is governed.

> **Related documentation:**
> - [`agent-manifest.yaml`](../agent-manifest.yaml) — Machine-readable permissions manifest
> - [`README.md`](../README.md) — Technical architecture and usage
> - [Algorithmic Transparency Recording Standard](https://www.gov.uk/government/collections/algorithmic-transparency-recording-standard-hub)

---

## Contents

1. [Executive Summary](#executive-summary)
2. [Agent Identity and Purpose](#agent-identity-and-purpose)
3. [Autonomy Level](#autonomy-level)
4. [Data Access Controls](#data-access-controls)
5. [Tools and Actions](#tools-and-actions)
6. [Human Approval Points](#human-approval-points)
7. [UK GDPR Compliance](#uk-gdpr-compliance)
8. [Prompt Injection Handling](#prompt-injection-handling)
9. [Risk Assessment](#risk-assessment)
10. [Logging and Audit](#logging-and-audit)
11. [Kill Switch](#kill-switch)
12. [Review Schedule](#review-schedule)
13. [Microsoft Control Mapping](#microsoft-control-mapping)

---

## Executive Summary

The FOI Complaint Triage Agent assists UK public sector staff in analysing Freedom of Information requests, complaints, and related submissions. It operates at **Autonomy Level A1**: the agent provides analysis and recommendations, but **humans approve everything**. The agent never sends communications, writes to external systems, or makes decisions autonomously.

**Key governance points:**

| Aspect | Summary |
|--------|---------|
| **Autonomy** | A1 — Human approves all actions |
| **Data access** | Read submission text only; no access to case systems, HR, or requester history |
| **Writes/Sends** | Disabled — agent cannot write to systems or send communications |
| **Personal data** | May process; transient only; UK GDPR Article 6(1)(e) public task |
| **Special category data** | May encounter; Article 9(2)(g) substantial public interest |
| **Human review** | Mandatory for all classifications, routing, and escalations |
| **Kill switch** | Multiple methods; immediate effect |
| **Review cycle** | 6 months |

---

## Agent Identity and Purpose

**Manifest section:** `agent`

| Field | Value |
|-------|-------|
| ID | `exp-01-foi-triage` |
| Name | FOI Complaint Triage Agent |
| Version | 1.0.0 |
| Owner | Information Rights Team |

**Purpose:** The agent takes free-text FOI/EIR/SAR/complaint submissions and produces structured triage output including:
- Classification (FOI, EIR, SAR, complaint, mixed)
- Extracted questions with source quotes
- Routing suggestions
- Safeguarding flags
- Cost limit assessment
- Draft clarification letters (for human review and editing)

The agent is a **decision support tool**, not a decision-making system.

---

## Autonomy Level

**Manifest section:** `autonomy`

This agent operates at **Autonomy Level A1: Human Approves Everything**.

### What this means

| The agent CAN | The agent CANNOT |
|---------------|------------------|
| Analyse submission text | Send emails or messages |
| Classify request types | Write to databases or case systems |
| Flag safeguarding concerns | Approve or reject requests |
| Suggest routing | Make final decisions |
| Draft clarification letters | Auto-reject based on content or origin |
| Detect bulk submission signals | Take any autonomous action |

### Explicit constraints

From the manifest:
- Agent NEVER sends emails, messages, or any external communications
- Agent NEVER writes to databases, case management systems, or external storage
- Agent NEVER approves, rejects, or closes requests
- Agent NEVER makes final decisions — humans always decide
- Agent NEVER auto-rejects requests based on content, origin, or perceived AI generation

---

## Data Access Controls

**Manifest section:** `data_access`

### Data the agent MAY read

| Resource | Scope | Justification |
|----------|-------|---------------|
| Submission text | Single submission at a time, as provided by staff | Core function: analyse text to produce triage output |
| System prompt and configuration | Static configuration files | Required for agent operation |

Submission text may contain:
- Requester names and contact details
- Subject matter of requests
- Personal data (if included in submission)
- Special category data (health, political opinions in complaints)

**Retention:** Transient processing only — the agent does not persist submission data.

### Data the agent must NEVER access

| Resource | Reason |
|----------|--------|
| Case management systems | Agent provides analysis only; staff access systems directly |
| HR records | Not required for triage function |
| Financial systems | Not required for triage function |
| Email systems | Agent does not send communications |
| Requester identity databases | Triage based on content, not identity |
| Previous request history by requester | Each request assessed on own merits; no profiling |

### Microsoft controls

| Control | Purpose |
|---------|---------|
| **Microsoft Entra Agent ID** | Unique identity for the agent; enables access control and audit |
| **Conditional Access** | Restrict which users/devices can invoke the agent |
| **Power Platform DLP policies** | Prevent connectors from accessing prohibited data sources |

---

## Tools and Actions

**Manifest section:** `tools`

### Allowed tools

| Tool | Provider | Access | Human approval |
|------|----------|--------|----------------|
| Text analysis (LLM inference) | Microsoft Foundry (Azure OpenAI) | Read | Output requires human review |
| JSON schema validation | Local Python | Read | N/A |

### Writes: DISABLED

The agent does not write to any external systems. All output is returned to the staff member's interface for review.

### Sends: DISABLED

The agent never sends emails, messages, or any communications. Draft clarification letters are provided as text for staff to review, edit, and send through normal channels.

### Microsoft controls

| Control | Purpose |
|---------|---------|
| **Power Platform DLP policies** | Enforce connector restrictions |
| **Azure Key Vault** | Secure storage of API credentials |

---

## Human Approval Points

**Manifest section:** `human_approval`

All agent output is advisory. Human staff must review and approve before any action is taken.

### Mandatory approval points

| Action | Approver | Rationale |
|--------|----------|-----------|
| Accept triage classification | FOI/Complaints Officer | Human must confirm request type |
| Act on routing suggestion | FOI/Complaints Officer | Human decides actual routing |
| Escalate safeguarding concern | Officer or Safeguarding Lead | Critical decisions require human judgement |
| Send clarification letter | FOI/Complaints Officer | Agent drafts only; human sends |
| Apply cost limit assessment | FOI/Complaints Officer | Cost decisions have legal implications |

### No approval required

| Action | Rationale |
|--------|-----------|
| View triage output | Staff can view analysis without approval |
| Re-run triage on same submission | No external effect |

---

## UK GDPR Compliance

**Manifest section:** `uk_gdpr`

### Lawful basis

| Basis | Article | Description |
|-------|---------|-------------|
| Primary | 6(1)(e) Public task | Processing necessary for task in public interest; FOI/EIR/SAR handling is statutory duty |
| Secondary | 6(1)(c) Legal obligation | Public authorities legally obliged to respond within statutory timeframes |

### Special category data

The agent may encounter special category data in submissions (e.g., health data in complaints about NHS services, political opinions).

| Aspect | Detail |
|--------|--------|
| Lawful basis | Article 9(2)(g) — Substantial public interest |
| DPA 2018 condition | Schedule 1, Part 2, Paragraph 6 — Statutory and government purposes |
| Safeguards | Processing limited to classification; no decisions on special category data; human review mandatory; data not persisted |

### Data minimisation

- Agent processes only submission text provided
- No additional data retrieval about requester
- Output contains only necessary classification and routing information

### Retention

| Agent retention | None — transient processing only |
|-----------------|----------------------------------|
| Note | Organisation's case management system handles retention per their schedule |

### Data residency

| Requirement | UK region (Azure UK South or UK West) |
|-------------|--------------------------------------|

### Microsoft controls

| Control | Purpose |
|---------|---------|
| **Microsoft Purview** | Data governance, classification, and compliance |
| **Azure region selection** | Ensure UK data residency |

---

## Prompt Injection Handling

**Manifest section:** `prompt_injection`

Submissions may contain adversarial content attempting to manipulate agent behaviour.

### Controls

| Control | Implementation |
|---------|----------------|
| System prompt hardening | Clear separation of instructions from user content |
| Output schema enforcement | Azure OpenAI structured outputs with strict mode |
| Content filtering | Microsoft Foundry prompt shields (Azure AI Content Safety) |
| Human review | All output reviewed by trained staff |
| No external actions | Even if manipulated, agent cannot take external action (A1 autonomy) |

### Residual risk

Prompt injection could cause incorrect classification or misleading output. This is mitigated by mandatory human review and the absence of autonomous actions.

### Microsoft controls

| Control | Purpose |
|---------|---------|
| **Microsoft Foundry prompt shields** | Detect and filter prompt injection attempts via Azure AI Content Safety |

---

## Risk Assessment

**Manifest section:** `risk_assessment`

### Methodology

Likelihood × Impact matrix (Low/Medium/High)

### Risk register summary

| ID | Risk | Inherent | Controls | Residual | Owner |
|----|------|----------|----------|----------|-------|
| R1 | Incorrect classification delays response | Medium | Human review, confidence levels, rationale | Low | FOI Team Lead |
| R2 | Missed safeguarding concern | High | Conservative flagging, prominent UI, staff training | Low | Safeguarding Lead |
| R3 | Prompt injection causes misleading output | Medium | Prompt hardening, content filtering, human review | Low | InfoSec |
| R4 | Bias in classification or routing | Medium | Evaluation testing, human review, no identity-based decisions | Low | FOI Team Lead |
| R5 | Data breach via Azure OpenAI | Medium | DPA, UK residency, no training on data, Key Vault | Low | InfoSec |
| R6 | Service unavailability | Low | Fallback to manual triage, Azure SLA | Low | IT Ops |
| R7 | Unauthorised access to outputs | Medium | Entra ID auth, RBAC, audit logging, Conditional Access | Low | InfoSec |

See `agent-manifest.yaml` for full risk details including specific controls.

---

## Logging and Audit

**Manifest section:** `logging_and_audit`

### Logged events

| Event | Data logged |
|-------|-------------|
| Agent invocation | Timestamp, User ID, Session ID, input size (not content) |
| Triage output generated | Triage ID, classification, flags, processing mode |
| Safeguarding flag raised | Triage ID, flag type, timestamp, reviewing officer |
| Error or failure | Error type, timestamp, user ID, sanitised message |

### Log destinations

| Primary | Application Insights |
|---------|---------------------|
| Secondary | Organisation SIEM |

### Audit trail

- All triage outputs linked to originating user
- Configuration changes logged
- Access to logs restricted to authorised personnel

### Microsoft controls

| Control | Purpose |
|---------|---------|
| **Application Insights** | Telemetry, logging, and diagnostics |
| **Microsoft Purview** | Audit trail and compliance reporting |

---

## Kill Switch

**Manifest section:** `kill_switch`

Multiple methods exist to immediately disable the agent if issues are detected.

| Method | Action | Time to effect | Who can activate |
|--------|--------|----------------|------------------|
| Disable Copilot Studio agent | Set agent to 'Off' | Immediate | Copilot Studio admins |
| Revoke API key | Disable in Azure Key Vault | Immediate | Key Vault admins |
| Conditional Access block | Apply blocking policy | Within minutes | Entra ID admins |
| Power Platform DLP policy | Block connector | Within minutes | Power Platform admins |

### Escalation contacts

*(Update with actual contacts on deployment)*

| Role | Contact |
|------|---------|
| IT Service Desk | servicedesk@example.gov.uk |
| Information Security | security@example.gov.uk |
| Data Protection Officer | dpo@example.gov.uk |

---

## Review Schedule

**Manifest section:** `review`

| Last review | 2026-10-24 |
|-------------|------------|
| Next review | 2027-04-24 |
| Frequency | 6 months |
| Reviewer | Information Governance Board |

### Review triggers

- Significant change to agent functionality
- Security incident involving the agent
- Change in regulatory requirements
- Safeguarding concern related to agent output
- Significant change in usage patterns

---

## Microsoft Control Mapping

This section maps manifest requirements to Microsoft security controls.

### Generally available controls

| Manifest requirement | Microsoft control | Purpose |
|---------------------|-------------------|---------|
| Agent identity | **Microsoft Entra Agent ID** | Unique identity for agents; enables RBAC and audit |
| Access control | **Conditional Access** | Restrict who can invoke the agent and from where |
| Data loss prevention | **Power Platform DLP policies** | Prevent data flowing to unauthorised connectors |
| Prompt injection defence | **Microsoft Foundry prompt shields** (Azure AI Content Safety) | Detect and filter injection attempts |
| Credential storage | **Azure Key Vault** | Secure API key storage with access policies |
| Data governance | **Microsoft Purview** | Classification, lineage, compliance |
| Logging | **Application Insights** | Telemetry, diagnostics, custom events |

### Announced capabilities (availability unverified)

The following capabilities were announced by Microsoft but their general availability status should be verified before relying on them in production:

| Capability | Description | Status |
|------------|-------------|--------|
| **Dynamic Permissions** | Runtime adjustment of agent permissions based on context | Announced; availability unverified |
| **Dynamic Agent Risk** | Real-time risk scoring for agent actions | Announced; availability unverified |
| **Dynamic Conditional Access** | Context-aware access policies for agents | Announced; availability unverified |

> **Note:** Do not configure production controls based on these announced capabilities until their general availability is confirmed. This documentation will be updated when status changes.

### Reference

This work is inspired by Microsoft's blog post 'Agents are your newest insiders' (19 October 2026), which outlines the need for organisations to govern AI agents with the same rigour as human insiders.

---

## Assumptions

The following items are marked as assumptions in the manifest and require verification during deployment:

| ID | Assumption | Verify on deployment |
|----|------------|---------------------|
| A1 | Production uses Azure UK region for data residency | ✓ |
| A2 | Organisation has retention policy for case records | ✓ |
| A3 | Safeguarding concerns reviewed within 1 hour | ✓ |
| A4 | Application Insights used for logging | ✓ |
| A5 | Contact details for kill switch escalation | ✓ |
| A6 | Review by Information Governance Board | ✓ |

---

## Document history

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-10-24 | — | Initial version |
