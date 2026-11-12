# GitHub Copilot harness

This is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 12 November 2026 says that, and says agents on this harness use Copilot Credits. It states no price.

The skills in `skills/` tell the harness when to call the core. They do not assign a weight that selects a skill. How a tenant selects a skill from a description was not exercised. A separate page on generative orchestration was not opened. That selection is unverified.

## Skills

| Skill | When |
|---|---|
| `preview-channel-scope` | The user has named channels and a period, and no digest has been confirmed. |
| `produce-channel-digest` | The user has confirmed those channel ids and that period on a separate object. |
| `withhold-sensitive-message` | A message was withheld, or the user asks for a view of a named person. |

Each skill stops when the JSON is shown. None of them posts.

## Memory and files

The overview says this harness supports memory and can create Word, Excel, PowerPoint, and PDF files. An administrator control to turn memory off was not on that page. Do not write the export or the digest into agent memory. Do not create a file that posts or that copies a withheld message. This starter does not use the file feature.

## Tools

The only tools are `preview_scope`, `confirm_scope`, and `produce_digest`. They are read-only. `post_message`, `reply_message`, `react_message`, `mention_user`, and `forward_message` raise `DigestForbidden`. The harness must not be given a Teams connector action that sends. The connector's action list was not opened. Action names on that connector are unverified. The prohibition is the effect, not a product name.
