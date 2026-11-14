# Privacy model

Genealogy data is about real people, many of them alive. This project keeps the **application**
public and every **family's data** private, and makes the boundary hard to cross by accident.

## What is private

Everything that is knowledge about a particular family: names and surnames, dates, places,
parishes and regions linked to the family, IDs of persons/families/places/sources, URLs of scans,
records and published trees or artifacts, relationships, informants, search-log entries, research
notes and open leads. It all lives in the workspace (see `familytree/workspace.py`).

## What is public

The code, the agent instructions, the data format, the fictional sample family, and general
knowledge: how a service works, how to read a record, what survived in which partition, which
archive holds which kind of records. General knowledge learned during real research is welcome —
after it has been rewritten without the people it was learned on.

## How the boundary is enforced

1. **Separate locations.** The workspace is a different directory, ideally its own private git
   repository. `workspace.py init` refuses to create it inside the application repository.
2. **.gitignore** catches workspace-shaped paths (`data/`, `output/`, `research/`, `INSTRUCTIONS.md`,
   `privacy.yaml`, `*.ged`) if they ever appear here.
3. **The privacy guard** (`scripts/guard.py`, installed into git with `guard.py install`):
   - `pre-commit` scans every file in the index — content and file name — and the author and
     committer identity;
   - `commit-msg` scans the message;
   - `pre-push` scans every commit being pushed: all files of its tree, message, author, committer.
   The list of private terms is built at run time from the workspace and kept in memory; it is
   never written into the repository. Matching ignores case and diacritics and catches inflected
   forms (a surname in the genitive, a village in the locative). Without a workspace the guard
   blocks (fail closed).
4. **CI** runs the tests and the guard's generic checks (CI has no private data).
5. **The agent instructions** (AGENTS.md §1) tell the agent where each kind of content belongs.

## The workspace privacy.yaml

```yaml
block:            # extra terms: nicknames, informants, e-mail addresses, private URLs …
  - "Aunt Hela"
allow:            # generic phrases the guard would otherwise block, e.g. an archive's name
  - "State Archive in X"
```

The allow list is private too: published, it would reveal which public words occur in the family
data. Prefer whole phrases (an institution's name) to single words.

## Limits

- The guard knows only what is in the workspace data and `block:`. Names that appear only in free-text
  research notes (e.g. candidates from an index) are not extracted automatically — add the important
  ones to `block:` and keep notes out of the repository.
- Given names are not blocked on their own (they occur in every example); rare ones can be added to
  `block:`.
- A hook can be skipped with `--no-verify`; do not. The pre-push hook is the second line of defence.
- The name of your hosting account and the e-mail address in commits are public. Choose them knowing
  that.

## Contributors without family data

Set `FAMILYTREE_GUARD_NO_PRIVATE=1` (or pass `--no-private`): only the generic checks run. Use the
sample family for everything you need data for.
