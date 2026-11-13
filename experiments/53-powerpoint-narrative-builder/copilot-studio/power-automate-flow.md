# Flow note

A later Power Automate flow may call the Python core and return the JSON to the topic. It must not add a connector.

Do not add:

- Office 365 Outlook, or any send-mail action
- Microsoft Graph `PUT /content`, or a SharePoint create file action
- A publish-to-site custom connector
- An approval action that shares the deck when the pack contains the word share

A local `.pptx` built by `src/slides.py` can be returned to the presenter as a file they already asked for, and only after `record_presenter_approval()` has recorded approval. Returning that file is not a share. The flow must not post it to a site.

This note was not built in a tenant. The Power Automate connector list was not opened on 13 November 2026. Treat any connector name beyond this note as unverified.
