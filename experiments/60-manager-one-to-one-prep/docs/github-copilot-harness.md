# Microsoft Copilot harness

The common brief calls this layout a GitHub Copilot harness. The page opened on 17 November 2026, [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview), calls it the Microsoft Copilot harness. It does not use the words "GitHub Copilot harness". It is not the GitHub Copilot service. That distinction, beyond the page that was opened, is unverified.

The harness is described as a runtime for reasoning-heavy multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. No price was on the page.

## Skills

| Skill | Calls | When the JSON is shown |
|---|---|---|
| `prepare-one-to-one` | `prepare()` | `human_approval` is null. The selection was made before the run. |
| `explain-human-flag` | Nothing further | A flag already on the note. The sentence is not read out. |

Neither skill assigns a trigger phrase or a routing weight. The description says when to use it.

`acknowledge()` is not a tool of the agent. A seen-step has to name the directory line manager, the meeting id, and the same source ids. A sentence in a note does not do that, and it does not rate performance.

File creation, memory, and the sandbox are platform capabilities named on the page. This agent does not ask the harness to write a file, to remember a rating, or to browse a mailbox.
