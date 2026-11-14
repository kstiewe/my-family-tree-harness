# my-family-tree-harness

An agent-operated genealogy toolkit. You tell an AI agent (Claude Code, or any agent that reads
`AGENTS.md`) what you know about your family; the agent records it in plain YAML files, validates
the data, searches online registers (Geneteka, PomGenBaza, Szukaj w Archiwach …), reports gaps
with ready-made queries, and renders an interactive tree, Mermaid diagrams and GEDCOM.

The toolkit is built for research in Polish lands (all three partitions), with guides for
regional services that grow with every contributor. The interface language is selectable
(English, Polish); code and agent instructions are in English.

**Your family data never lives in this repository.** It lives in a separate, private
*workspace*; a privacy guard blocks commits that contain names, places, IDs or URLs from it.

## Quick start

```bash
pip install pyyaml                                   # Python 3.10+
python3 scripts/guard.py install                     # git hooks with the privacy guard
python3 scripts/workspace.py init ~/family-tree --lang en --git   # your private workspace
python3 scripts/workspace.py link ~/family-tree      # remember it (writes the git-ignored .workspace)
python3 scripts/build.py                             # validate + outputs in ~/family-tree/output/
```

Then open the project in Claude Code and start telling it about your family. The SessionStart
hook gives the agent the workspace and your private instructions (`~/family-tree/INSTRUCTIONS.md`).

Try it on the fictional sample family:

```bash
cd examples/sample-family && python3 ../../scripts/build.py --out /tmp/sample-tree
```

## Layout

```
AGENTS.md            the agent's manual — the main interface of the application
CLAUDE.md            Claude Code specifics (imports AGENTS.md)
familytree/          the Python package: model, validation, reports, HTML, GEDCOM, i18n, guard
  locales/           translations (pl.py); add a language by copying it
  templates/         the HTML page
  skeleton/          what `workspace.py init` creates
scripts/             entry points: build.py, geneteka.py, workspace.py, guard.py
sources/             guides to genealogical services and regions (knowledge + browser helpers)
docs/                data format, privacy model, research guide
examples/            the fictional sample family (a complete workspace)
tests/               unittest suite on the sample family
.githooks/           pre-commit, commit-msg, pre-push → the privacy guard
```

A workspace:

```
INSTRUCTIONS.md      private agent instructions: artifact URLs, research regions, open leads
privacy.yaml         extra blocked terms, allowed generic phrases
data/                project.yaml, persons.yaml, families.yaml, places.yaml, sources.yaml
research/            log.md (every search, also negative) and research notes
output/              generated: tree.html, tree-artifact.html, tree.mmd, ancestors.mmd,
                     ancestors.md, gaps.md, tree.ged (Polish names when language: pl)
```

Keep the workspace in its own **private** git repository (or no remote at all). The workspace is
found via `--workspace`, `FAMILYTREE_WORKSPACE`, the current directory, the `.workspace` file, or
`~/.config/familytree/workspace` — see `python3 scripts/workspace.py --help`.

## Outputs

| Output | Role |
|---|---|
| `tree.html` | interactive tree in generation lanes: highlight a person's line, zoom, search, facts, sources, research hints; works offline (fonts from the web) |
| `tree-artifact.html` | the same page without the document skeleton, for hosts that add it (e.g. Claude artifacts) |
| `tree.mmd`, `ancestors.mmd` | Mermaid diagrams (whole tree, line of ancestors) |
| `ancestors.md` | list of ancestors in Kekule numbering, with gaps |
| `gaps.md` | gaps in the data with concrete research suggestions and Geneteka links |
| `tree.ged` | GEDCOM 5.5.1 for Gramps, MyHeritage, Ancestry, FamilySearch |

`--public` hides living persons in HTML and GEDCOM.

## Documentation

- [AGENTS.md](AGENTS.md) — how the agent works with the data and the user
- [docs/data-format.md](docs/data-format.md) — the YAML data model
- [docs/privacy.md](docs/privacy.md) — what is private, how the guard works, contributing safely
- [docs/research-guide.md](docs/research-guide.md) — research stages and record types by partition
- [sources/](sources/README.md) — guides to services and regions; contributions welcome

## Contributing

Improvements to the code, translations and especially to the service and region guides are
welcome. Use only the fictional sample family in examples and tests, run
`python3 -m unittest discover -s tests`, and keep the privacy guard installed. Contributors without
any family data run the guard with `FAMILYTREE_GUARD_NO_PRIVATE=1`.

## Licence

GNU General Public License v3.0 or later (see [LICENSE](LICENSE)): you may use, study, share and
modify the software; copies and derived versions must stay open source under the same licence.

Additional permission under GNU GPL version 3 section 7: the files the software generates from your
data (HTML, Markdown, Mermaid, GEDCOM), including the parts of the page template embedded in them,
may be used and distributed under terms of your choice.

---

**Po polsku w skrócie:** narzędzie do budowy drzewa genealogicznego obsługiwane przez agenta AI.
Dane rodziny leżą w osobnym, prywatnym katalogu (workspace), a strażnik prywatności blokuje
commity, które by je zawierały. Język interfejsu: `language: pl` w `data/project.yaml`.
