---
name: draft-permissions-manifest
description: Draft an agent-manifest.yaml from one inventory record and validate it against schemas/agent-manifest.schema.json. Use when a governance owner wants a permissions draft. Never mark it approved.
catalogue_id: G010
harness: copilot-studio-github-copilot
autonomy: A1
metadata:
  version: "0.1.0"
  status: draft
  approved: false
tools:
  - name: generate_manifest
    entrypoint: src/generate_manifest.py
    effect: read
    writes_production: false
    sends: false
    arguments_refused:
      - "--approve"
approval_gate: >
  A schema-valid file is still a draft. The governance owner approves any
  use of it in a tenant. This skill has no approve argument that succeeds.
---

# Draft a permissions manifest

Run `src/generate_manifest.py` with `--inventory` and `--as-of`. Do not pass `--approve`. If a person asks for that flag, tell them the command exits without writing.

If validation fails, show the errors and do not describe the file as ready. If the inventory autonomy is A3, the tool drafts nothing. Say that A3 is not permitted. Do not downgrade it quietly and present the result as if the row had asked for A1.

The written file, when validation passes, has `draft_control.approved` set to false. High-risk actions are disabled even if the inventory asked for them. Say that a person would have to edit the manifest themselves, and that this skill will not do it.

Do not copy the file into a production repository as an approved control. Do not send it.
