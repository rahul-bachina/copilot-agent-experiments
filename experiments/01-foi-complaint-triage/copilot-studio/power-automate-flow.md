# Power Automate Flow Design: FOI Triage Analysis

This document describes how to build the Power Automate flow that connects Copilot Studio to Azure AI Foundry for FOI triage analysis.

## Prerequisites

- Power Automate Premium license (for HTTP connector)
- Azure AI Foundry / Azure OpenAI resource
- API endpoint URL and key (store in Azure Key Vault for production)

## Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOI Triage Analysis Flow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Trigger: Copilot Studio calls flow                          │
│     └─► Input: SubmissionText (string)                          │
│                                                                  │
│  2. Initialize variables                                         │
│     └─► SystemPrompt, Endpoint, Headers                         │
│                                                                  │
│  3. HTTP: POST to Azure OpenAI                                  │
│     └─► Send chat completion request                            │
│                                                                  │
│  4. Parse JSON response                                         │
│     └─► Extract triage result                                   │
│                                                                  │
│  5. Return to Copilot Studio                                    │
│     └─► Output: TriageResult (object)                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Build Guide

### Step 1: Create the Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **Create** → **Instant cloud flow**
3. Name: "FOI Triage Analysis"
4. Trigger: **When Copilot Studio calls a flow**

### Step 2: Configure Input

Add an input parameter to the trigger:
- **Name**: SubmissionText
- **Type**: Text
- **Description**: The full text of the FOI request or complaint to triage

### Step 3: Initialize Variables

Add three **Initialize variable** actions:

**Variable 1: SystemPrompt**
```
Name: SystemPrompt
Type: String
Value: [Paste the full system prompt from ../src/prompts.py]
```

**Variable 2: Endpoint**
```
Name: AzureEndpoint
Type: String
Value: https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT/chat/completions?api-version=2024-08-01-preview
```

**Variable 3: ApiKey** (or use Key Vault reference)
```
Name: ApiKey
Type: String
Value: @{outputs('Get_secret')?['body/value']}  // If using Key Vault
```

### Step 4: HTTP Request to Azure OpenAI

Add an **HTTP** action:

**Method**: POST

**URI**: `@{variables('AzureEndpoint')}`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "api-key": "@{variables('ApiKey')}"
}
```

**Body**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "@{variables('SystemPrompt')}"
    },
    {
      "role": "user",
      "content": "Please analyse the following submission and provide structured triage output.\n\n## Submission Text\n\n@{triggerBody()?['text']}\n\n## Instructions\n\nAnalyse this submission and produce a JSON response matching the triage output schema."
    }
  ],
  "response_format": {
    "type": "json_object"
  },
  "temperature": 0.1,
  "max_tokens": 4000
}
```

### Step 5: Parse JSON Response

Add a **Parse JSON** action:

**Content**: `@{body('HTTP')?['choices'][0]?['message']?['content']}`

**Schema**:
```json
{
  "type": "object",
  "properties": {
    "triage_id": { "type": "string" },
    "timestamp": { "type": "string" },
    "extracted_asks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "ask_id": { "type": "integer" },
          "summary": { "type": "string" },
          "source_quote": { "type": "string" },
          "specificity": { "type": "string" },
          "estimated_scope": { "type": "string" }
        }
      }
    },
    "classification": {
      "type": "object",
      "properties": {
        "primary_type": { "type": "string" },
        "confidence": { "type": "string" },
        "rationale": { "type": "string" }
      }
    },
    "routing": {
      "type": "object",
      "properties": {
        "suggested_department": { "type": "string" },
        "suggested_team": { "type": "string" }
      }
    },
    "flags": {
      "type": "object",
      "properties": {
        "urgency_level": { "type": "string" },
        "safeguarding_concern": { "type": "boolean" },
        "requires_immediate_human_review": { "type": "boolean" },
        "escalation_reason": { "type": "string" }
      }
    },
    "cost_limit_assessment": {
      "type": "object",
      "properties": {
        "likely_exceeds_limit": { "type": "boolean" },
        "clarification_needed": { "type": "boolean" },
        "draft_clarification_letter": { "type": "string" }
      }
    },
    "bulk_submission_signals": {
      "type": "object",
      "properties": {
        "detected": { "type": "boolean" },
        "note": { "type": "string" }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "one_line": { "type": "string" },
        "recommended_action": { "type": "string" }
      }
    }
  }
}
```

### Step 6: Configure Output

Add output to return to Copilot Studio:

1. Go to the trigger settings
2. Add an output:
   - **Name**: TriageResult
   - **Type**: Object
   - **Value**: `@{body('Parse_JSON')}`

### Step 7: Error Handling

Add a **Scope** around the HTTP action with a parallel branch for error handling:

**On failure branch**:
1. **Compose**: Create error response
   ```json
   {
     "error": true,
     "message": "Triage analysis failed. Please try again or contact support.",
     "flags": {
       "requires_immediate_human_review": true,
       "escalation_reason": "Automated triage failed - manual review required"
     }
   }
   ```
2. **Respond to Copilot** with the error response

## Using Azure Key Vault (Recommended)

For production, store the API key in Azure Key Vault:

1. Add **Azure Key Vault** connector
2. Use **Get secret** action to retrieve the API key
3. Reference in HTTP headers: `@{outputs('Get_secret')?['body/value']}`

## Testing the Flow

1. Save the flow
2. Click **Test** → **Manually**
3. Enter sample submission text
4. Verify JSON response structure

## Connecting to Copilot Studio

1. In Copilot Studio, go to your agent
2. Click **Actions** → **Add an action** → **Power Automate**
3. Select "FOI Triage Analysis" flow
4. Map input: SubmissionText to your topic variable
5. Map output: TriageResult to store the response

## Performance Considerations

- **Timeout**: Set HTTP timeout to 120 seconds (Azure OpenAI can take time for long inputs)
- **Retry**: Configure retry policy for transient failures
- **Concurrency**: Consider flow concurrency limits for high volume

## Cost Considerations

- Azure OpenAI charges per token
- Power Automate Premium required for HTTP connector
- Consider caching for repeated identical submissions (rare in practice)

## Alternative: Direct Azure AI Foundry Agent

If your organisation uses Azure AI Foundry agents, you can:

1. Deploy the agent in Azure AI Foundry
2. Use the Azure AI connector in Power Automate
3. Call the agent directly instead of raw chat completion

This provides better observability and management through the Foundry portal.
