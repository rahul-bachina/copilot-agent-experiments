# Architecture

The HR lead pastes one pack. Python returns one JSON document. A person decides what, if anything, the organisation does next.

```
HR lead
  -> Copilot Studio (standard harness or GitHub Copilot harness)
    -> src/review.py
      -> src/sources.py   pinned pages, opened 27 October 2026
      -> src/injection.py instructions recorded, not followed
  -> draft JSON, decision fields null
  -> HR lead, outside the agent
```

No model is called. No page is downloaded. The same pack and the same as-of date produce the same JSON.

## Why the dates are in code

Whether section 20 is in force is a comparison with 30 October 2026, the date in SI 2026/1065 regulation 3. A language model will sometimes describe a duty as already applying because a guidance page talks about preparation. The sample date in this repository is 27 October 2026. On that day the opened text of Equality Act 2010 section 40A still says "reasonable steps".

Acas examples are prompts. They are not regulations under the new section 40B. The core keeps `specified_steps_regulations_made` false. A pack in which every prompt is evidenced is still not a compliance conclusion.

## What a tenant would add, and what this starter does not

| Piece | In this repository | Later, if an employer wants it |
|---|---|---|
| Checklist | `src/review.py` | The same function, hosted where the employer already runs Python |
| Standard harness | Build guide in `copilot-studio/` | One topic. No importable solution |
| GitHub Copilot harness | Skills in `skills/` | Upload path to be confirmed in the tenant |
| Microsoft Foundry | Narrative note only | Optional brief over the JSON. UK region. Not trained on reports |
| Power Automate | Flow described, not shipped | Returns JSON. Does not write Dataverse |
| SharePoint or the HR system | Not connected | A person files the draft, if they file it |

Training attestations are a person stepping through the employer's own process. This starter does not record one. A write is disabled in the manifest.

## Human approval

The highlighted step is the HR lead. The agent stops when the JSON is returned. Publishing a policy, completing risk ratings, replying to a worker, and any disciplinary step are outside the agent even after someone accepts the draft.

The diagram is [architecture_diagram.png](architecture_diagram.png).
