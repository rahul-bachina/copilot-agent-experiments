# Architecture

The digest is a deterministic Python core. Copilot Studio, if a tenant adds it later, calls that core. It does not decide which sentence is a decision, and it does not post.

```
Requesting user
    |
    |  synthetic export, as-of date
    v
preview_scope  ---- no message text, no digest
    |
    |  separate confirmation of channel ids and period
    v
produce_digest
    |
    +--> only channels the user can access, and only the confirmed period
    |
    +--> Experiment 08 masks UK identifiers
    +--> hold a judgement, a private cue, or a marked message (text not copied)
    +--> cues label a sentence; a leading negation does not
    +--> Experiment 41 requires the sentence to be in the cited lines
    +--> Experiment 29 checks tokens, numbers, and dates
    |
    v
JSON digest. human_approval is null. Nothing is posted.
```

The same inputs produce the same JSON. `graph_called`, `network_called`, `model_called`, and `foundry_called` stay false.

## What a tenant would add, and what this starter does not

A tenant deployment would be a Copilot Studio agent whose only tools are the three read tools in `schema/tools.json`. The standard harness is three topics. The GitHub Copilot harness is three skills around the same calls. Both are described as build notes. Neither is an importable solution.

Microsoft Graph `GET /teams/{team-id}/channels/{channel-id}/messages` is the documented read for channel messages, opened 12 November 2026. This folder does not call it. A date filter is not a supported query option on that page, so a live connector would have to apply the period after retrieval. This starter applies the period before any digest, on the export the user supplied. Replies are a separate call or `$expand=replies`. They are not read here.

Delegated `ChannelMessage.Read.All` is the least-privileged delegated permission on that page. It is not a per-channel scope. The local `accessible_channel_ids` list is the control in this starter. Application `ChannelMessage.Read.Group` uses resource-specific consent. This starter does not request either permission.

Work IQ is on catalogue row M002. The Work IQ page was not opened. It is not called.

## Diagram

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py` where matplotlib is installed. Matplotlib is not a runtime dependency.

The highlighted step is the requesting user. They confirm the channels and the period. A withheld message stays with them. Posting stays outside the agent.
