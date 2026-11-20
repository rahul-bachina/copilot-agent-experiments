# Microsoft Foundry

Catalogue row L002 names Microsoft Foundry and Azure first. This note is the Azure option. No Foundry resource is deployed from this repository. A live model has not been scored.

The Python core produces the briefing. A Foundry deployment, if the organisation adds one, may turn that JSON into a short note. The note may use only fields already in the JSON. It must not decide that a change applies, fill a date that the JSON says is `not stated`, or drop a legal hold.

Quotes, hashes, negation, and `record_owner_seen()` stay in `src/briefing.py`. The core does not call the network. `network_called` and `live_site_fetched` stay false.

Prompt shields, Key Vault, and a UK region are deployment choices. They were not opened on 20 November 2026. Treat that product behaviour as unverified. A production deployment should use UK South or UK West. This repository cannot enforce the region.

Do not point the deployment at a live regulator site. The snapshots in `fixtures/` are the source.
