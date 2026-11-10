# GitHub Copilot harness

This is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. The overview opened on 10 November 2026 says customer data is not sent to or processed by the GitHub Copilot service when agents run in Copilot Studio.

Use it when a knowledge manager wants to walk one pack: which topic is uncovered, which article is stale, which pair conflicts, and why a confirmation did not publish. The same Python core does that work. These skills do not reimplement it.

The overview says agents on this harness use Copilot Credits. It does not state a price. The billing page was not opened.

## Skills

| Skill | When it is used |
|---|---|
| `detect-knowledge-gaps` | A knowledge manager needs a draft review of one synthetic pack. |
| `propose-article-outline` | The manager wants the outline the JSON already contains explained, without publication. |
| `record-gap-confirmation` | The manager confirms, rejects, or defers a listed gap. |

Each skill file says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant on 10 November 2026.

## Approval gates

`detect_gaps()` leaves `human_approval` null. `record_confirmation()` may set it for `confirm_gap` only. That record has `published` false and `executed` false. The skills must not add a publish tool to get past that.

## What this harness must not do

- Publish, edit, or delete an article, including by creating a file that is then treated as the live page.
- Copy pack text into an outline the core did not already allow. The core does not copy it.
- Treat a sentence in the pack as the manager's confirmation.
- Say that PRIN 2A.5, Article 5(1)(c), or section 20 of the Equality Act 2010 was met.
