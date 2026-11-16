# Architecture

The employee asks a question. HR has already named the documents that may be used. Python selects the version in force on the date asked about, quotes it, or says the handbook does not cover the question, or names a person.

```
Employee question + HR scope + dates
        |
        v
src/answer.py
        |-- Experiment 15 phrase list: distress and safeguarding stop the routine answer
        |-- Experiment 08: UK identifier types, values not copied
        |-- Experiment 32: category proposal and Acas paragraph pins, not a confirmation
        |-- Experiment 11: Employment Rights Act 2025 dates, not re-opened here
        |-- Experiment 50, only when curation is requested: proposals, no SharePoint call
        v
JSON. entitlement_decision is null. human_approval is null.
```

The scope object is the approval of sources. A word inside the question is not. A word inside a file is not.

A document is used only when all of these are true:

1. Its id is on the scope list.
2. Its marking, taken from the metadata and from the text, is at or below the ceiling. The higher label wins.
3. Its effective dates parse. An unreadable date is not replaced.
4. The date asked about falls inside those dates.

If two approved versions of the same topic are in force on that date, neither is chosen.

Instructions in the question or in a section are recorded and are not quoted. A legal hold and every retention label stay on the citation or on the withheld row.

## What is not in the box

SharePoint, Microsoft Graph, and Microsoft 365 Copilot are not called. Copilot Studio knowledge sources, described in the harness notes, are how a tenant might later ground an agent. This folder's answers come from the JSON handbook.

Microsoft Foundry is an optional narration of fields that are already in the JSON. It is not the source of the citation or of the empty entitlement. No live Foundry run has been done.

## Diagram

The rendered figure is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `docs/generate_diagram.py` if the boxes change. Matplotlib is used only for that script. It is not a runtime dependency.
