# Microsoft Foundry

The task for this experiment names Microsoft Foundry beside the Copilot Studio GitHub Copilot harness. The planning catalogue row records the stack code CS-GH + AZ. This note uses the name Microsoft Foundry. It does not use the retired product name.

This folder does not call Foundry. `foundry_called` stays false. `model_called` stays false. There is no endpoint, no key, and no project connection in the code.

## What a later host could use it for

A deployment might show the JSON to a reviewer inside a Foundry project, or ask a model to restate the fixed explanation sentence in plainer words. The class would still have to come from `src/normalise.py`. A model must not be given the job of choosing the class or choosing the source. That split is the point of the deterministic layer.

Nothing in this repository wires that host. UK region availability for Microsoft Foundry was not verified for this experiment.

## What was not opened

Prompt shields, Document Intelligence, and a groundedness evaluator were not opened for this experiment. They are unverified here. This starter does not need Document Intelligence: the reviewer pastes text that is already split into lines. A model call would be a new data flow. The manifest would have to change in the same change, and a data protection officer would confirm a lawful basis first.

## What this starter already refuses

Even if a later host adds a model, the Python functions `choose_source`, `edit_record`, `contact_party`, and `lookup_register` raise. A prompt cannot switch them on.
