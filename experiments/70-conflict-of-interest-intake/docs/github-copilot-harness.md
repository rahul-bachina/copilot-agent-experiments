# Microsoft Copilot harness

Packaged here in the layout the common brief calls the GitHub Copilot harness. The overview opened on 20 November 2026 does not use those words. See [harness-comparison.md](harness-comparison.md).

The skills are:

- [draft-conflict-declaration](../skills/draft-conflict-declaration/SKILL.md) calls `draft_declaration()`.
- [confirm-declaration](../skills/confirm-declaration/SKILL.md) calls `confirm_declaration()` for the declarant and the declaration hash.
- [record-disposition](../skills/record-disposition/SKILL.md) calls `record_disposition()` for an ethics or procurement officer.
- [route-to-ethics](../skills/route-to-ethics/SKILL.md) calls `record_route_seen()` and does not stage the declaration.

Each skill says when to use it. This starter does not assign a weight to a skill. Where the harness selects from a description, the description in the skill file is what was written. That selection was not exercised in a tenant.

Memory, file creation, and the sandbox are described on the harness overview. This starter does not create a Word, Excel, PowerPoint, or PDF file. It does not rely on harness memory for the confirm step. The confirm object is a separate JSON object. A sentence remembered from the declaration is not that object.

The page says agents and workflows on this harness use Copilot Credits. It states no price. Treat a price as unverified.

Do not add a tool that clears, excludes, approves, or sends. Those functions raise in the Python core.
