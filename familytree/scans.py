"""Report on the local copies of the sources: what is saved in the workspace and what still has to be downloaded.

A source points to its local copy with `file` (a path relative to the workspace, normally under `research/skany/`).
Sources that are scans, photos or saved pages and have no `file` are listed as missing; an index entry is its own
copy (the transcription is in the data) and a family account has no document at all.
"""

from __future__ import annotations

import re
from pathlib import Path

from .dates import TODAY
from .i18n import tr
from .model import Tree
from .schema import SCANS_DIR

LOCAL, MISSING, INDEX, ACCOUNT = "local", "missing", "index", "account"
_SOURCE_ID = re.compile(r"S\d{4,}")
_NOT_SCANS = {".md", ".txt"}        # notes next to the scans


def cited(rec) -> set[str]:
    """Source IDs written in the `source` / `sources` fields anywhere inside a record."""
    found: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("source", "sources"):
                    found.update(x for x in (value if isinstance(value, list) else [value])
                                 if isinstance(x, str) and _SOURCE_ID.fullmatch(x))
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(rec)
    return found


def person_sources(tree: Tree) -> dict[str, set[str]]:
    """Sources behind each person: their own facts and the marriages they are a spouse in."""
    result = {pid: cited(p) & tree.sources.keys() for pid, p in tree.persons.items()}
    for f in tree.families.values():
        for role in ("husband", "wife"):
            if f.get(role) in result:
                result[f[role]] |= cited({k: v for k, v in f.items() if k != "children"}) & tree.sources.keys()
    return result


def status(tree: Tree, sid: str) -> str:
    s = tree.sources[sid]
    if tree.source_files(sid):
        return LOCAL
    if s.get("type") == "oral" or s.get("quality") == "oral":
        return ACCOUNT
    if s.get("quality") in ("index", "transcription"):
        return INDEX
    return MISSING


def orphan_files(tree: Tree) -> list[str]:
    """Files in the scans directory that no source points to."""
    attached = {p for sid in tree.sources for p in tree.source_files(sid)}
    base = tree.root / SCANS_DIR
    found = (p.relative_to(tree.root).as_posix() for p in base.rglob("*") if p.is_file() and p.suffix.lower() not in _NOT_SCANS)
    return sorted(set(found) - attached)


def _cell(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).replace("|", "/").strip()


def write_scans(tree: Tree, path: Path) -> None:
    by_person = person_sources(tree)
    by_source: dict[str, list[str]] = {sid: [] for sid in tree.sources}
    for pid, sids in by_person.items():
        for sid in sids:
            by_source[sid].append(pid)
    state = {sid: status(tree, sid) for sid in tree.sources}
    count = {k: sum(1 for v in state.values() if v == k) for k in (LOCAL, MISSING, INDEX, ACCOUNT)}
    orphans = orphan_files(tree)

    def people(sid: str, limit: int = 4) -> str:
        names = [tree.name(pid) for pid in by_source[sid]]
        return _cell(", ".join(names[:limit]) + (f" +{len(names) - limit}" if len(names) > limit else ""))

    L = [tr("# Local copies of the sources"), "",
         tr("_Generated {date} by `scripts/build.py` — do not edit by hand._", date=TODAY.isoformat()), "",
         tr("**Rule:** a source that can be checked (a scan, a photo, a page) is saved in `{dir}/` as soon as it is "
            "found and attached with its `file` field; every new search starts with the local copy.", dir=SCANS_DIR), "", tr("## Summary"), "",
         tr("- sources: {n}", n=len(tree.sources)),
         tr("- saved locally: {n}", n=count[LOCAL]),
         tr("- **missing — to be downloaded: {n}**", n=count[MISSING]),
         tr("- index entries or transcriptions (the entry is in the data): {n}", n=count[INDEX]),
         tr("- family accounts (no document): {n}", n=count[ACCOUNT]),
         tr("- files in `{dir}/` not attached to any source: {n}", dir=SCANS_DIR, n=len(orphans)), "",
         tr("## 1. Missing local copies"), ""]
    missing = [sid for sid, v in state.items() if v == MISSING]
    if missing:
        L += [tr("| Source | Title | Where | Persons |"), "|---|---|---|---|"]
        for sid in sorted(missing, key=lambda x: (tree.sources[x].get("quality") == "derivative", x)):
            s = tree.sources[sid]
            L.append(f"| `{sid}` | {_cell(s.get('title', ''))} | {_cell(s.get('url') or s.get('repository') or '')} | {people(sid)} |")
    else:
        L.append(tr("_None._"))
    L += ["", tr("## 2. Saved locally"), ""]
    local = [sid for sid, v in state.items() if v == LOCAL]
    if local:
        L += [tr("| Source | File | Persons |"), "|---|---|---|"]
        for sid in local:
            L.append(f"| `{sid}` | {'<br>'.join(f'`{p}`' for p in tree.source_files(sid))} | {people(sid)} |")
    else:
        L.append(tr("_None._"))
    L += ["", tr("## 3. Persons and their sources"), "",
          tr("| Person | Saved locally | Missing | Index / transcription | Accounts |"), "|---|---|---|---|---|"]
    for pid in tree.persons:
        sids = by_person[pid]
        cells = [sorted(s for s in sids if state[s] == k) for k in (LOCAL, MISSING, INDEX, ACCOUNT)]
        L.append(f"| `{pid}` {_cell(tree.name(pid))} | " + " | ".join(", ".join(c) or "—" for c in cells) + " |")
    L += ["", tr("## 4. Files not attached to any source"), ""]
    L += [f"- `{p}`" for p in orphans] or [tr("_None._")]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
