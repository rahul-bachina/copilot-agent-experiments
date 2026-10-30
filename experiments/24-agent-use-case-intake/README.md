# Experiment 24: Agent use-case intake

Catalogue ID **G001**. Stack **Copilot Studio and Power Platform**. Autonomy **A1**.

A business team describes a proposed agent: the problem, the users, the data, whether personal or special-category data is involved, the decisions affected, the autonomy they want, and the systems the idea would touch. This starter returns a **draft classification** for the governance team:

- a suggested autonomy level of **A0, A1, or A2**
- a risk tier for the queue
- whether a DPIA is indicated on the answers the team recorded
- whether an ATRS record is indicated for a public-sector proposal
- which catalogue pattern, or which experiment already in this repository, the idea resembles

**The governance team approves the intake classification, or changes it.** The agent does not. It does not approve or reject the use case, and it does not provision, deploy, or publish anything. The output is labelled **DRAFT FOR THE GOVERNANCE TEAM**.

Status: **Available** as a local starter. Nothing in this folder calls a model or the network.

## The problem

Teams arrive with an agent idea before anyone has said what it would be allowed to do. Governance then reconstructs the same facts from a slide: whose data, which decision, whether the team wants the agent to act on its own, and whether a DPIA or an ATRS record even belongs in the conversation.

The awkward part is keeping that first reading in one place, with the legal sentences attached to the dates they were opened, and with a person still owning the classification.

## Who it helps

**A business team** that can fill a structured form and wants a draft back, rather than a yes.

**A governance team** that has to approve or change the classification before anyone builds. The same proposal and the same as-of date produce the same JSON.

It does not help a team that wants the tool to approve the idea or to create the agent.

## What it does

`src/classify.py` reads one JSON proposal and writes one JSON document.

| Draft field | Where it comes from |
|---|---|
| Suggested autonomy | Experiment 14's decision table (`rules.score`). A request for A3 is flagged out of scope. The suggested level is never A3. |
| Risk tier | A queueing heuristic in `src/risk.py`. It is not an ICO score and not an Orange Book assessment. |
| DPIA | Experiment 19's `screen()`, passed the team's recorded yes / no / unknown answers. `dpia_required` stays null. |
| ATRS | Sentences from the GOV.UK guidance opened for this folder, plus Experiment 03's `draft_atrs` applicability note. Mandatory scope is not decided. |
| Resemblance | A recorded hint, or a single keyword hit, against experiments already in this repository. Several hits are listed and not ranked. |

Free text is not an input to those rules. Instructions in the problem statement are recorded and not followed. Payload keys that try to set the classification, the approval, or a provisioned flag are removed before the draft is built.

The sample is Northmere Borough Council, which is fictional. It is an internal draft of hazard wording. No consequential action is recorded, so Experiment 14's table suggests **A0** even though the team asked for A1. The governance team can change that. This agent does not.

## What it does not do

- It does not approve a use case, reject a use case, or record that the governance team has done either.
- It does not provision, deploy, publish, or create a Copilot Studio agent, a Power Automate flow, a Dataverse table, or a Microsoft Foundry resource.
- It does not suggest autonomy A3. A3 is out of scope for this catalogue.
- It does not decide that Article 35 requires a DPIA. A recorded "no" on the team's answers is not a finding that Article 35(1) does not apply.
- It does not decide that an organisation or a tool is inside the ATRS mandatory scope, and it does not email a record.
- It does not select a platform. Experiment 14 may be called. `platform_selected` stays null.
- It does not call Experiment 03's manifest generator. That generator needs PyYAML and jsonschema, which this experiment's tests do not install, and it cannot mark a manifest approved.
- It does not write a production record or send a message.
- It does not look up a licence, a system, or a live policy.

## Sources opened for this folder

Opened on **30 October 2026**:

| Source | What this starter uses |
|---|---|
| [UK GDPR Article 35](https://www.legislation.gov.uk/eur/2016/679/article/35) | Article 35(1) is the overarching DPIA test. Article 35(3) lists three cases where an assessment shall in particular be required. Article 35(4), as amended, says the Commission shall publish a list. This tool does not decide whether any ICO page is that list. |
| [ATRS guidance for public sector bodies](https://www.gov.uk/government/publications/guidance-for-organisations-using-the-algorithmic-transparency-recording-standard/algorithmic-transparency-recording-standard-guidance-for-public-sector-bodies) | Mandatory for government departments, and for ALBs which deliver public or frontline services or directly interact with the general public, and, within those organisations, for tools which have a significant influence on a decision-making process with public effect, or which directly interact with the general public. Recommended by the Data Standards Authority across the public sector. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | The standard harness is for rule-based agents. The GitHub Copilot harness is for reasoning-heavy, multi-step work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The page says that harness is a Copilot Studio framework, not the GitHub Copilot service, and that customer data is not sent to that service. |

Not opened for this folder, so not quoted: the ATRS scope and exemptions policy, the Copilot Studio licensing article linked from the harness overview, the ICO DPIA pages (Experiment 19 holds those pins), and Microsoft Learn pages Experiment 14 pinned on 27 October 2026. If this folder's as-of date is more than the stale threshold after a pin, the draft says not to rely on that pin.

## How to run it

Python 3.10 or newer. No Azure credentials and no network.

```bash
cd experiments/24-agent-use-case-intake
python -m pip install -r requirements.txt
python src/classify.py --input examples/sample_proposal.json --as-of 2026-10-30
python -m pytest tests/ -q
python eval/evaluate.py
```

Experiments 03, 14, and 19 must sit beside this folder. This starter does not carry a copy of them.

## Honest limitations

- The risk tier is a queue. Special-category data, criminal-offence data, a legal or similarly significant effect, a regulated decision, a significant automated decision, or a request for A3 raises it to high. Personal data, or a tool that would interact with the public, raises a low tier to medium. Unknown answers stay `not_assessed` unless a high fact was actually recorded. None of that is a DPIA.
- `dpia_likely_needed` is true only when Experiment 19's screen says the recorded answers indicate a list trigger or a recorded Article 35(1) view. It is false only when every recorded answer on that screen is no. It is null when the facts are incomplete. `dpia_required` is never set.
- `atrs_likely_needed` follows the guidance sentences above. For a government department or an in-description ALB, both the organisation answer and a tool answer have to be recorded before this draft says the tests match. For a council, a police force, or another wider public body, the draft says the standard is recommended, which is not a finding that the body is in the mandatory organisation list. A private firm is not given an ATRS recommendation. The scope policy was not opened.
- Resemblance is not a measure of similarity. A hint the team recorded is repeated. Otherwise one keyword match is reported, and two matches are left as a list.
- Experiment 14's suggested autonomy can differ from the autonomy the team asked for. That difference is the point of the draft. This agent does not resolve it.
- Article 35(10) and Article 35(11) are on the legislation page and are not applied here.
- The samples are synthetic. Northmere Borough Council is not a real authority.

## Where the rest of the starter lives

| Path | What it is |
|---|---|
| `agent-manifest.yaml` | Permissions. If this README and the manifest disagree, the manifest is the control. |
| `src/classify.py` | The only producer of a classification. |
| `docs/security-and-permissions.md` | The same boundary, written out. |
| `docs/harness-comparison.md` | Which Copilot Studio harness to use for this intake. |
| `copilot-studio/` | Standard harness: one topic, no skill. |
| `skills/` | GitHub Copilot harness skills. They call `classify` and stop. |
| `eval/` | A deterministic smoke test. Not a model score. |

MIT Licence. See [LICENSE](../../LICENSE).
