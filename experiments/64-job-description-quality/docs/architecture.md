# Architecture

Experiment 64, catalogue H007, autonomy A0. One Python core, two Copilot Studio harnesses, and an optional Microsoft Foundry note. The recruiter accepts or rejects each suggestion and writes the final wording. The agent does not publish, post, or send.

```
Draft and guide
      |
      v
Either harness (topics, or skills)
      |
      v
src/review.py
   |-- Experiment 08  UK identifiers, not described as anonymised
   |-- local mask     phone, email, date of birth, address, name
   |-- Experiment 36  two salary or grade figures, no source chosen
      |
      v
Prompts, each with a reason and a suggested alternative
      |
      v
Recruiter decision, bound to the draft hash and the suggestion hash
HR seen-step, where the draft may be an occupational requirement,
positive action, or a health question
      |
      v
Recruiter's own wording, bound to the hash of that text
      |
      v
Not published, not posted, not sent
```

The rendered diagram is [architecture_diagram.png](architecture_diagram.png). Regenerate it with `python docs/generate_diagram.py` from this experiment. Matplotlib is used only by that script. It is not a runtime dependency.

## What is deterministic

Phrase checks, negation, the question date, salary parsing, markings, and the approval hashes are Python. A model is not called. The same draft, guide, directory, and question date produce the same JSON.

Experiment 08 proposes identifier redactions. Experiment 36 compares two figures. Neither module's quotes are stored. This core does not choose a source and does not describe the output as anonymised.

## What a person does

1. The recruiter reads the prompts. That read is not an approval.
2. The directory recruiter accepts or rejects each suggestion. The object names that suggestion's hash and the draft hash.
3. Where the draft may be an occupational requirement, positive action, or a pre-employment health question, a directory HR partner records that they have seen it. That seen-step does not decide the legal question.
4. A distress, vulnerability, or safeguarding cue stops the wording path. The cue is not copied.
5. The recruiter writes the final wording. The record stores it only when the hash matches that text, mandated statements that were present are still present, and the legal hold and retention labels are kept.
6. Nothing is published.

## What is not a tool

Publish. Post. Send. Score a candidate. Score an advert against a person. Rank applicants. Decide section 13, 19, 39, 60, or 159, or Schedule 9 paragraph 1. Strip a mandated statement. Drop a legal hold or a retention label.
