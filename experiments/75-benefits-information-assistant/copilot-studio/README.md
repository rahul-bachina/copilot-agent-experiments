# Standard harness

This is a topic guide for the Copilot Studio standard harness. It is not an importable solution. No connector is enabled.

The topics call the same Python core as the skills. See [../docs/harness-comparison.md](../docs/harness-comparison.md). On 24 November 2026 the harness overview said the standard harness follows the topics and rules the maker defines. The licensing page it points to was not opened. No price is stated here.

## Topics

1. **Benefits information.** The resident asks a general question. The topic calls `answer_question` with the question and the date the question is about. It shows the JSON. It does not add an amount.
2. **Urgent route.** If `outcome` is `urgent_human`, the topic shows the signpost already in the JSON, including the 999 line, and offers a person. It does not place a call.
3. **Resident approval.** The topic shows the summary and the content hash. The resident confirms in the deterministic approval step. A sentence in the question is not that confirmation. The topic then calls `record_resident_approval`.
4. **Stop.** Eligibility, an award, a claim, and sending have no topic that succeeds. The topic tells the resident a person decides, and it offers the adviser route.

The maker should not add a generative answer node that can overrule the JSON.
