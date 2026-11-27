# Experiment 84: Energy and Water Customer Agent

Catalogue ID **UK12**. Autonomy **A1**. The assistant answers an account or billing question from a pinned synthetic knowledge base, and it may propose a meter-reading submission, a payment-plan request, or a Priority Services Register referral. The customer confirms each proposal against the agent-held copy and its hash. The confirmation does not submit the action. Affordability, debt, disconnection, prepayment, and vulnerability go to a human advisor. The agent does not change a tariff, agree a payment plan, write off debt, install or switch a prepayment meter, or make a decision.

This starter reuses the injection list from [Experiment 02](../02-consumer-duty-complaint-intake/). It does not call `intake()` and it does not apply the DISP clock. Energy and water complaints are not DISP complaints. The handover record uses the same fields as [Experiment 13](../13-council-contact-front-door/). It does not call that starter's council triage, which would mis-route a bill. Identifier counts come from [Experiment 08](../08-uk-pii-redaction-gateway/). The matched values are not stored.

Status: **Available** as a local starter. No tenant is configured. Reedmarsh Energy and Reedmarsh Water are invented. They are not a claim that one firm holds both licences.

## Problem

A customer asks what a bill shows, or asks the assistant to take a meter reading, request a payment plan, or refer them to the Priority Services Register. The same message can also say they cannot afford the bill, that they rely on medical equipment, or that they want to complain. A note on the account can tell the assistant to change the tariff or to treat the action as already confirmed.

## Who it helps

A customer who wants a plain answer from the pinned knowledge, and a clear statement that they are talking to an AI, with a person available on the same turn. A human advisor who takes affordability, debt, disconnection, prepayment, vulnerability, and complaints. The organisation gets a record that a proposal was confirmed against the exact held text and its hash, and a fairness count that does not publish a cell of fewer than five people.

## What it does

On every turn the answer says the customer is talking to an AI and that a human advisor is available. A request for a person is handed over immediately.

A question that matches one pinned article is answered with that article. The energy or water sector on the pinned account selects the article. A complaint is answered with the pinned escalation text for that sector and is handed to a person. It is not a routine queue. A complaint that also contains distress, a subject access request, or another sensitive cue is still a handover.

A meter reading, a payment-plan request, or a Priority Services Register referral can be proposed when the message asks for that action and no vulnerability, affordability, debt, disconnection, or prepayment cue is present. The customer confirms on a separate object. The hash covers the proposal, the flags, the marking, the legal hold, the retention labels, and the required acknowledgements. Eight kinds of edit after that point are refused, including a caller who changes the text and supplies a new hash.

Fairness events use synthetic group codes. A count below 5 is not published, and neither is a difference, a percentage, or a total that would reveal it. The threshold of 5 is a starter rule. It is not anonymisation.

## Non-goals

- It does not change a tariff, agree a payment plan, write off debt, install or switch a prepayment meter, disconnect a supply, or add someone to the Priority Services Register.
- It does not decide a complaint, an affordability question, or a vulnerability question.
- It does not follow an instruction in a message or an account note, including a sentence that says the action is already confirmed.
- It does not treat a caller-supplied knowledge base, policy, directory, or account as authoritative.
- It does not apply the DISP clock. Experiment 02 is used for injection phrases only.
- It does not call council triage from Experiment 13.
- It does not drop a protective marking, a legal hold, or a retention label.
- It does not coerce an unreadable amount, reading, or date to zero or to another value.
- It does not call a live model. The smoke test is deterministic.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/customer.py --request examples/sample_request.json --as-of 2026-11-27
.venv/bin/python -m pytest tests/ -q
.venv/bin/python eval/evaluate.py
```

The core is the Python standard library plus the packages in `requirements.txt` for the tests. Experiments 02 and 08 must sit beside this folder. No network call is made.

## Honest limitations

- The knowledge and the complaint text are the pinned fixtures. A question that matches none of them is not answered from a model.
- The paraphrase set is a fixture. The smoke recall is on those rewordings, not on live text. A cue that uses none of the stems is not flagged.
- A distress or vulnerability stem is routed even when the sentence denies it. A policy title such as "the safeguarding policy" is not treated as a personal cue.
- Treating an article or a snapshot as stale when the gap is greater than 90 days is a starter rule. It is not a statutory period. The boundary day itself is not stale.
- The small-number threshold of 5 is a starter control. The ICO anonymisation guidance was not opened. The output is not described as anonymised.
- The eight-week Energy Ombudsman wording is from the Ofgem complaints page opened on 27 November 2026. The Gas and Electricity (Consumer Complaints Handling Standards) Regulations 2008, as opened, define a specified time period and do not contain the words "eight weeks". The Energy Ombudsman website was not opened. `ccw.org.uk` was not opened.
- Electricity Condition 28 was not extracted. Gas Condition 28.1 was read. This starter does not install a meter. No water Priority Services Register licence condition number was found. None is stated.
- The Ofgem ethical AI PDF and the 2019 Standards of Conduct guidance PDF were not read line by line. They are unverified. UK GDPR Articles 6, 9, and 22A to 22D were not opened. No lawful basis is asserted.
- The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.
- Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, Purview, Application Insights, and Dynamics 365 Contact Centre were not opened on 27 November 2026. No Dynamics environment is configured.
- The harness overview opened on 27 November 2026 names a Microsoft Copilot harness. It does not use the words GitHub Copilot harness. The page says that harness retries and finds alternative paths. This starter does not enable that. The common-brief sentence that this harness is not the GitHub Copilot service was not on that page. That sentence is unverified.
- A recorded confirmation does not submit the reading, agree the plan, or add a register entry. There is no production write.

## Licence

MIT. See the repository `LICENSE`.

## Layout

```text
experiments/84-energy-water-customer-agent/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── src/customer.py
├── fixtures/
├── eval/
├── skills/
├── copilot-studio/
└── docs/
```
