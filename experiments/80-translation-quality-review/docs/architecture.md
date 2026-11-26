# Architecture

A bilingual reviewer supplies one synthetic source, one synthetic translation, their directory reference, and the date the question is about. `prepare_review()` aligns the segments with Experiment 79 `align()`. It does not copy that aligner. Contact details are masked with Experiment 79 `mask_text`. UK identifiers are counted with Experiment 08 `propose()`. The redacted text from Experiment 08 is not copied.

The result lists every check, the flags, the high-risk segments, the protective marking, the legal hold, and the retention labels. Those fields sit inside the content hash. The source body and the target body each have a document hash. The hashes are held in memory for the process.

High-risk segments are routed to the reviewer regardless of lexical overlap. `quality_score` stays null. A low-confidence alignment is reported and is not treated as a translation score.

If the outcome is a human route, `record_route_seen()` records that the named reviewer has seen it. If high-risk segments are present, `record_high_risk_validated()` records that the same reviewer has validated them. `record_translation_owned()` records that the reviewer owns that exact hash. None of those steps publishes, sends, or overwrites a document. A sentence in either text is not a step.

The standard harness and the Microsoft Copilot harness both call this core. Microsoft Foundry, if used, may only narrate fields that are already in the JSON.

## What is not a tool

Publishing, sending, overwriting, and approving the translation raise `ReviewForbidden`. A caller-supplied glossary is compared with the pinned glossary and is not applied. A directory in the request is not the pinned directory.
