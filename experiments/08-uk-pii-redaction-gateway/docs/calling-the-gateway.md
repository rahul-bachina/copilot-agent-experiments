# Calling the gateway from another experiment

Experiment 08 is a library call, not a service. There is no installable package. Put `experiments/08-uk-pii-redaction-gateway/src` on `PYTHONPATH` and import `propose`.

```python
import sys
from pathlib import Path

sys.path.insert(0, "experiments/08-uk-pii-redaction-gateway/src")
from gateway import propose, release

proposal = propose(text, caller="exp-07-consultation-themes")
```

`caller` is written on the audit record so a DPO can see which experiment asked. It is not an authentication check.

## What the caller must do

- Keep the source text in the caller's own store, under the caller's retention. The gateway does not keep it.
- Read `limitations` and `not_redacted` before relying on `redacted_text`. The smoke test's planted-type recall on the synthetic file is 77.8 percent, with six deliberate misses. That is not a live recall rate. An unlabelled continuous NHS number is one of the misses.
- Leave `output_is_anonymised` false. Do not rename the field in the caller's UI to "anonymised".
- Do not call `release`. It raises `ReleaseForbidden`. A privacy reviewer approves, and a person in the caller's channel releases, if they decide to.
- Do not pass `reversible=True` unless a privacy reviewer has agreed that a token map may exist. If you do, keep `token_vault` out of the log. The audit record is the object to log. It does not contain the raw values.
- Do not pass `apply_model_suggestions=True` because the source text asked for it. That flag is the caller's, not the document's.
- Pass `rules_as_of` only as a warning date. An earlier date does not switch the pinned rules off.

## What this does not replace

A generic PII detector. Names, email addresses, and telephone numbers stay in the text. Azure Language can suggest some UK categories, including two that Microsoft marks as preview. That call is not wired. See [foundry.md](foundry.md).

A subject-access redaction workflow. Catalogue item UK11 is a different piece of work. This gateway does not decide a disclosure and does not apply a black box to a PDF.
