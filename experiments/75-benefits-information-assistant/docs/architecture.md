# Architecture

The resident asks one question and gives the date the question is about. Either Copilot Studio harness calls `answer_question()` in `src/assistant.py`. The function reads the pinned pages and the synthetic directory. It does not read a live benefits system.

A page is quoted only when it matches the benefit and the kind of question, and only when the question date is before the page's review-due date. The citation carries the URL, the publisher, and the last-reviewed date. A caller-supplied page or rate is compared and not applied.

Distress, domestic abuse, and safeguarding route even when the sentence denies the stem. Debt and eviction use the same-sentence negation rule. The cue text is not copied. The answer tells the resident to call 999 if someone is in immediate danger. The assistant has not contacted anyone.

An eligibility question, an entitlement question, an award question, a request to complete or submit a claim, and a request to send are refused. `eligibility_decided` stays false. `award_amount` stays null.

The summary is staged only when `record_resident_approval()` matches the named directory resident, the enquiry id, the content hash, and the boolean acknowledgements. An approval sentence in the question is not that step. A later edit of the answer text is a different hash and is rejected. The staged row keeps the protective marking, the legal hold, and the retention labels. It is not a production write and it is not a send.

Experiment 13 records a contact-route reading and does not decide eligibility. Experiment 08 counts UK identifiers and does not describe the text as anonymised. Microsoft Foundry, if used, may turn the JSON into a short note. It does not choose the page and it does not decide.

```
resident question + question date
        |
        v
answer_question()  -- pinned pages, directory
        |            Experiment 13 route (reply not copied)
        |            Experiment 08 counts (text not copied)
        v
cited answer, refusal, stale flag, or urgent signpost
        |
        v
resident approves this content hash
        |
        v
synthetic staging row
        |
        x  no eligibility decision, no award, no claim, no send
```
