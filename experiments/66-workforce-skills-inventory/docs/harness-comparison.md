# Harness comparison

Both harnesses call `src/inventory.py`. The employee decision, the HR validation, and the route are the same objects. Neither harness writes to an HR system.

Pages opened on 19 November 2026:

- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview). The page names three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The standard harness follows the topics and rules the maker defines. The Microsoft Copilot harness is described for reasoning-heavy work. It can take a goal and break it into steps, supports skills and memory, creates and edits Word, Excel, PowerPoint, and PDF files, and runs each task in a sandbox. Agents on that harness use Copilot Credits. The page states no price. It does not use the words "GitHub Copilot harness". Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date.
- The linked billing and licensing pages named on that overview were not opened. Any price, inclusion, or credit quantity is unverified here.

This folder packages skills under `skills/` because the common brief asks for a GitHub Copilot harness layout. That packaging is a choice in this repository. It is not a sentence on the overview page.

## Which harness suits which deployment

**Standard harness.** A skills inventory with a fixed path: read the pack, return proposals, stop, then a later topic records the employee's decision or HR's validation from a separate object. The maker defines the topics. Predictable steps suit that harness. See `copilot-studio/`.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** A longer conversation where the employee corrects one skill, asks what the band means, and then asks for a learning plan from skills they have already confirmed. Skills, memory, and file creation are what the overview describes. This starter does not create a file. The Python core still decides the proposals and the hashes. See `docs/github-copilot-harness.md`.

**Customer Conversation harness.** The overview describes it for customer voice and chat. A workforce inventory is not that scenario. This starter does not use it.

## What is the same

The manifest, the fixtures, the tests, and `propose_inventory()` are the same. `employee_confirmed` stays false until `record_employee_decision()` succeeds for that inventory hash and that skill hash. A sentence in the evidence is not that call.

## Cost

The overview says the Microsoft Copilot harness uses Copilot Credits and states no price. It points to a separate licensing page for the standard harness. That page was not opened. This readme does not quote a price. Building either harness in a tenant can consume credits or a licence. Confirm that with the tenant before anyone relies on it.
