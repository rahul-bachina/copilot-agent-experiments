# Flow note

The flow's only job is to return JSON to the topic. It runs `prepare_pack` or, on a later step, `record_review`. It does not create a Dataverse row, it does not send mail, and it does not post to a publisher.

A firm that later wants a working-paper store adds that write as a separate, person-confirmed step, and updates the manifest first. This starter does not include it.

Do not add the Office 365 Outlook connector, a Teams post action, a Dynamics 365 update, or an HTTP action to a survey platform. Power Platform DLP, if the tenant uses it, should block those connectors for this flow. The DLP product page was not opened on 11 November 2026. That control is unverified here.

`record_review` accepts only `confirm_sample_frame_and_limitations` and `reject_pack` in the tool schema. A flow step that maps a chat utterance onto `publish_pack` or `contact_customer` is a mistake. The Python refuses those decisions anyway. `published` stays false.
