# Dynamics 365 and Microsoft Fabric

The catalogue stack for C005 is Dynamics 365 and Microsoft Fabric. This starter does not connect to either. Product pages for knowledge articles and for Fabric were not opened on 10 November 2026. Click-paths below are **unverified**.

## If a connector is added later

A knowledge article in Dynamics 365 Customer Service, and a table or lakehouse in Microsoft Fabric, would be production records. This manifest disables writes. A later connector must not:

- create, update, publish, or delete a knowledge article;
- change an article's state from draft to published because a gap was confirmed;
- write a search-miss fact back into a warehouse as if the gap had been accepted;
- send the outline to a customer.

The knowledge manager does those things in the organisation's own system, after reading this review, if they decide to. Confirmation in `record_confirmation` is a record that the gap was seen. `published` stays false.

## What this folder already does instead

The approved base is `fixtures/knowledge_base.json`, or a list passed for one run. Experiment 21 and Experiment 40 are in-process reads of synthetic catalogues. They are not a Fabric query and not a Dynamics 365 knowledge search.

Power Platform DLP, if the organisation later adds a connector, is the place to block publish and write connectors. That policy was not opened on 10 November 2026 and is unverified here.
