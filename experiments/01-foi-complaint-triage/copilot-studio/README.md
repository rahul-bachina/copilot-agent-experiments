# Copilot Studio Implementation Guide

This guide explains how to recreate the FOI Complaint Triage Agent in Microsoft Copilot Studio and integrate it with Power Automate.

> **Important Note**: This is a step-by-step build guide, not an importable solution. Copilot Studio agents cannot be reliably exported as standalone files for import. You will need to manually create the agent following these instructions.

## Overview

The Copilot Studio implementation provides:
- A conversational interface for staff to submit FOI requests/complaints for triage
- Integration with Azure AI Foundry via Power Automate for AI processing
- Structured output displayed in the conversation

## Architecture

```mermaid
graph LR
    A[Staff User] --> B[Copilot Studio Agent]
    B --> C[Power Automate Flow]
    C --> D[Azure AI Foundry]
    D --> C
    C --> B
    B --> A
```

## Prerequisites

- Microsoft 365 license with Copilot Studio access
- Power Automate Premium (for HTTP connector)
- Azure AI Foundry resource with GPT-4o deployment
- Azure OpenAI endpoint and API key

## Step 1: Create the Copilot Agent

1. Go to [Copilot Studio](https://copilotstudio.microsoft.com)
2. Click **Create** → **New copilot**
3. Name it "FOI Complaint Triage Assistant"
4. Set the description: "Helps staff triage incoming FOI requests, EIR requests, Subject Access Requests, and complaints"

### Configure Agent Settings

In the agent settings:
- **Primary language**: English (UK)
- **Tone**: Professional, helpful

## Step 2: Add the System Instructions

Navigate to **Settings** → **Generative AI** and add these instructions:

```
You are an assistant helping UK public sector staff triage Freedom of Information (FOI) requests, complaints, and other submissions.

Your role is to:
1. Accept submission text from the user
2. Send it to the triage flow for analysis
3. Present the structured results clearly
4. Answer follow-up questions about the triage

You ASSIST human staff - you do NOT make decisions. All final decisions are made by humans.

Key principles:
- Never suggest rejecting a request based on how it was written
- Flag safeguarding concerns for immediate human attention
- Treat all requests fairly regardless of apparent origin
- Be clear that bulk/template signals are informational only

When presenting results, highlight:
- Classification and confidence
- Any urgency or safeguarding flags (show these first if present)
- Whether clarification may be needed
- Recommended routing
```

## Step 3: Create Topics

### Topic 1: Triage Submission

Create a new topic called "Triage a submission":

**Trigger phrases**:
- "I have a new FOI request"
- "Triage this submission"
- "Analyse this request"
- "I need to triage a complaint"
- "New submission to triage"

**Topic flow**:

1. **Message**: "Please paste the full text of the FOI request, complaint, or other submission you'd like me to triage."

2. **Question node**: 
   - Variable name: `SubmissionText`
   - Entity: Open-ended text
   - Validation: Minimum 20 characters

3. **Action node**: Call Power Automate flow "FOI Triage Analysis"
   - Input: `SubmissionText`
   - Output: `TriageResult`

4. **Condition node**: Check if `TriageResult.flags.requires_immediate_human_review == true`
   - If yes: Show urgent message (see below)
   - If no: Show standard results

5. **Urgent message**:
   ```
   ⚠️ IMMEDIATE HUMAN REVIEW REQUIRED ⚠️
   
   This submission contains safeguarding or safety concerns that require urgent human attention.
   
   Reason: {TriageResult.flags.escalation_reason}
   
   Please escalate this to your supervisor or safeguarding lead immediately.
   ```

6. **Standard results message**:
   ```
   📋 TRIAGE RESULTS
   
   Classification: {TriageResult.classification.primary_type}
   Confidence: {TriageResult.classification.confidence}
   
   📌 Key Information:
   - {TriageResult.summary.one_line}
   - Urgency: {TriageResult.flags.urgency_level}
   - Asks identified: {count(TriageResult.extracted_asks)}
   
   🏢 Suggested Routing:
   - Department: {TriageResult.routing.suggested_department}
   - Team: {TriageResult.routing.suggested_team}
   
   💰 Cost Assessment:
   - Likely exceeds limit: {TriageResult.cost_limit_assessment.likely_exceeds_limit}
   - Clarification needed: {TriageResult.cost_limit_assessment.clarification_needed}
   
   Would you like me to show the draft clarification letter, the detailed asks, or explain any part of this analysis?
   ```

### Topic 2: Show Clarification Letter

**Trigger phrases**:
- "Show the clarification letter"
- "Draft letter"
- "What should I write back"

**Flow**:
1. Check if `TriageResult.cost_limit_assessment.draft_clarification_letter` exists
2. If yes: Display the letter
3. If no: "No clarification letter was generated for this submission as it appears appropriately scoped."

### Topic 3: Show Detailed Asks

**Trigger phrases**:
- "Show the asks"
- "What are they asking for"
- "List the questions"

**Flow**:
Display each item from `TriageResult.extracted_asks` with:
- Ask number
- Summary
- Source quote
- Specificity
- Scope

### Topic 4: Explain Classification

**Trigger phrases**:
- "Why is this classified as..."
- "Explain the classification"
- "Why FOI not EIR"

**Flow**:
Display:
- `TriageResult.classification.rationale`
- `TriageResult.classification.indicators`

## Step 4: Create the Power Automate Flow

See [power-automate-flow.md](power-automate-flow.md) for detailed flow design.

### Quick Overview

1. **Trigger**: "When Copilot Studio calls a flow"
2. **Input**: SubmissionText (string)
3. **HTTP action**: POST to Azure OpenAI endpoint
4. **Parse JSON**: Extract triage result
5. **Response**: Return TriageResult to Copilot

## Step 5: Connect Flow to Copilot

1. In Copilot Studio, go to **Actions** → **Add an action**
2. Select **Power Automate**
3. Choose your "FOI Triage Analysis" flow
4. Map the input/output variables

## Step 6: Test the Agent

1. Open the Test pane in Copilot Studio
2. Say "I have a new FOI request to triage"
3. Paste a sample submission
4. Verify the results display correctly

## Security Considerations

- The Power Automate flow should use a service account
- Store Azure OpenAI credentials in Azure Key Vault
- Audit log all triage requests
- Consider DLP policies for sensitive data

## Limitations

- Copilot Studio has message length limits; very long submissions may need to be truncated
- Power Automate Premium license required for HTTP connector
- Real-time processing depends on Azure OpenAI response times

## Files in This Directory

- `README.md` - This guide
- `system-prompt.md` - Full system prompt for the agent
- `power-automate-flow.md` - Detailed Power Automate flow design
- `topic-designs/` - Topic flow diagrams (for reference)

## What Is and Isn't Provided

| Artefact | Provided | Notes |
|----------|----------|-------|
| System prompt text | ✅ Yes | Copy into agent settings |
| Topic trigger phrases | ✅ Yes | Copy into topic configuration |
| Topic flow logic | ✅ Yes | Build following step-by-step guide |
| Power Automate flow logic | ✅ Yes | Build following detailed guide |
| Importable .zip solution | ❌ No | Not reliable to export/import |
| HTTP request templates | ✅ Yes | In Power Automate guide |
