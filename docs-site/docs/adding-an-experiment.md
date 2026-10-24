# Adding a page

This page is for someone extending the catalogue. Buyers can ignore it.

The briefing site is MkDocs with the Material theme. Source is `docs-site/`. From that directory:

```bash
python -m pip install -r requirements.txt
mkdocs build --strict
```

`--strict` treats warnings as errors. A broken internal link, a missing navigation entry, or a missing architecture diagram fails the build. The same command runs on every pull request.

## Add an experiment page

1. Land the experiment under `experiments/`, with its README, `agent-manifest.yaml`, and `docs/security-and-permissions.md`. The manifest has to validate. See the root [CONTRIBUTING.md](https://github.com/rahul-bachina/copilot-agent-experiments/blob/main/CONTRIBUTING.md).
2. Add `docs-site/docs/experiments/<folder-name>.md`. Use the same heading order as the existing experiment pages:
    - The problem
    - Who it helps
    - What it does
    - What it does not do
    - How the work flows, with a text version of the flow and then a Mermaid diagram that marks the human approval
    - Architecture diagram, if the experiment has one
    - Microsoft stack
    - Security and permissions, taken from `agent-manifest.yaml` and `docs/security-and-permissions.md`
    - How to try it
    - Limitations
    - Source, linking to the folder on GitHub
3. Give every image a text alternative that says what the picture shows. Do not leave `alt` empty.
4. If the experiment has `docs/architecture_diagram.png`, add a row to `DIAGRAMS` in `docs-site/hooks.py`. The hook copies the file at build time. Do not commit a second copy of the PNG.
5. Add the page under `Experiments` in `nav` in `docs-site/mkdocs.yml`. The header people see stays at four links: Experiments, Governance, Roadmap, About.
6. Add a card on the home page, and keep the roadmap list in step with any planned name. Use one status: Available, Blueprint, Planned, or Archived. Say what is actually runnable. Autonomy level on an available card.
7. Do not invent figures, client names, testimonials, or model scores. If you quote a smoke test, say it is a smoke test and point at the file or command that produced it.
8. Use UK English. Write Microsoft Foundry. Do not write the retired product name.
9. Run `mkdocs build --strict` and open the new page.

## Status labels

| Label | Use it when |
| --- | --- |
| Available | The experiment is in the repository and the briefing can point at something a reader can run. |
| Blueprint | The design is written down and the runnable agent is not in the repository. |
| Planned | The name is on the roadmap only. No date. |
| Archived | The experiment has been withdrawn and the page is kept for the record. |

## Mermaid

Diagrams use a fenced block with the language `mermaid`. Material loads Mermaid in the browser when a page contains one. Also write the flow as a numbered list on the same page, so the steps are still there if the diagram does not render.
