"""Validate the data and generate the outputs.

    python3 scripts/build.py               validate + all outputs in <workspace>/output/
    python3 scripts/build.py --check       validate only
    python3 scripts/build.py --find Kowal  find persons (duplicate check before adding someone)
    python3 scripts/build.py --public      HTML, map and GEDCOM without data of living persons
    python3 scripts/build.py --json        machine-readable result (errors with codes and fixes, next free IDs)
    python3 scripts/build.py --schema      allowed fields and values of the data files, as JSON

The source of truth is <workspace>/data/*.yaml; everything in output/ is generated — do not edit it.
The workspace is found as described in `scripts/workspace.py --help`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import i18n
from .gedcom import write_gedcom
from .geo import write_geography
from .geomap import write_map
from .html import write_html
from .i18n import tr
from .model import FIXES, Tree
from .reports import mermaid_views, write_ancestors, write_gaps
from .scans import write_scans
from .schema import schema_json
from .workspace import NOT_FOUND, find_workspace

def output_names() -> dict[str, str]:
    """File names of the outputs in the active language, keyed by their English names."""
    return {"tree.html": tr("tree.html"), "tree-artifact.html": tr("tree-artifact.html"), "tree.mmd": tr("tree.mmd"),
            "ancestors.mmd": tr("ancestors.mmd"), "tree.ged": tr("tree.ged"), "gaps.md": tr("gaps.md"),
            "ancestors.md": tr("ancestors.md"), "scans.md": tr("scans.md"), "map.html": tr("map.html"), "map-artifact.html": tr("map-artifact.html"),
            "geography.md": tr("geography.md"), "geography.json": tr("geography.json")}


def write_outputs(tree: Tree, out: Path, public: bool) -> dict[str, Path]:
    names = {k: out / v for k, v in output_names().items()}
    out.mkdir(parents=True, exist_ok=True)
    full, anc = mermaid_views(tree, public)
    names["tree.mmd"].write_text(full, encoding="utf-8")
    names["ancestors.mmd"].write_text(anc, encoding="utf-8")
    geo = tree.geo(living=not public)
    write_html(tree, names["tree.html"], public, geo=geo)
    write_html(tree, names["tree-artifact.html"], public, artifact=True, geo=geo)
    write_gedcom(tree, names["tree.ged"], public)
    write_gaps(tree, names["gaps.md"])
    write_ancestors(tree, names["ancestors.md"])
    write_scans(tree, names["scans.md"])
    write_map(tree, geo, names["map.html"])
    write_map(tree, geo, names["map-artifact.html"], artifact=True)
    write_geography(geo, names["geography.md"], names["geography.json"])
    return names


def issue_json(issue) -> dict:
    return {"code": issue.code, "record": issue.record, "message": issue.text, "fix": FIXES.get(issue.code, "")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate the family-tree data and generate outputs.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--find", metavar="TEXT", help="find persons by given name / surname / variants")
    ap.add_argument("--public", action="store_true", help="hide data of living persons in HTML and GEDCOM")
    ap.add_argument("--json", action="store_true", help="print a machine-readable result instead of text")
    ap.add_argument("--schema", action="store_true", help="print the data model as JSON and exit")
    ap.add_argument("--workspace", type=Path, help="workspace directory (see scripts/workspace.py --help)")
    ap.add_argument("--data", type=Path, help="data directory (default: <workspace>/data)")
    ap.add_argument("--out", type=Path, help="output directory (default: <workspace>/output)")
    ap.add_argument("--lang", help="language of outputs (default: project.yaml `language`, FAMILYTREE_LANG, en)")
    args = ap.parse_args(argv)

    if args.schema:
        print(json.dumps(schema_json(), ensure_ascii=False, indent=2))
        return 0
    ws = None
    if not (args.data and args.out):
        ws = find_workspace(args.workspace)
        if not ws:
            print(json.dumps({"ok": False, "error": NOT_FOUND}) if args.json else NOT_FOUND, file=sys.stderr if not args.json else sys.stdout)
            return 2
    data = args.data or ws.data
    out = args.out or ws.output

    # the language comes from project.yaml, so read it before the messages are produced
    i18n.set_language("en")
    i18n.set_language(i18n.resolve(args.lang, Tree.peek_project(data)))
    tree = Tree(data)

    if args.find:
        hits = tree.find(args.find)
        if args.json:
            print(json.dumps([{"id": pid, "name": tree.name(pid), "life": tree.life_lines(tree.persons[pid]),
                               "kekule": tree.kekule.get(pid, [])} for pid in hits], ensure_ascii=False, indent=2))
            return 0
        for pid in hits:
            nums = tree.kekule.get(pid)
            print(f"{pid}  {tree.name(pid)}  {'; '.join(tree.life_lines(tree.persons[pid]))}"
                  + (f"  {tr('[no. {numbers}]', numbers=', '.join(map(str, nums)))}" if nums else ""))
        return 0

    written: dict[str, Path] = {}
    if not tree.errors and not args.check:
        written = write_outputs(tree, out, args.public)
    ids = tree.next_ids()
    if args.json:
        print(json.dumps({
            "ok": not tree.errors, "workspace": str(ws.root) if ws else None, "data": str(data), "language": i18n.language(),
            "counts": {"persons": len(tree.persons), "ancestors": len(tree.kekule), "families": len(tree.families),
                       "places": len(tree.places), "sources": len(tree.sources)},
            "errors": [issue_json(e) for e in tree.errors], "warnings": [issue_json(w) for w in tree.warnings],
            "next_ids": ids, "outputs": {k: str(v) for k, v in written.items()}, "public": args.public,
        }, ensure_ascii=False, indent=2))
        return 1 if tree.errors else 0

    print(tr("Persons: {persons} (ancestors of the proband: {ancestors}) · families: {families} · places: {places} · sources: {sources}",
             persons=len(tree.persons), ancestors=len(tree.kekule), families=len(tree.families), places=len(tree.places),
             sources=len(tree.sources)))
    for e in tree.errors:
        print(tr("ERROR: {message}", message=e))
    for w in tree.warnings:
        print(tr("warning: {message}", message=w))
    if tree.errors:
        print("\n" + tr("{n} errors — fix the data; no outputs were generated.", n=len(tree.errors)))
        return 1
    if written:
        print(tr("Outputs in {dir}: {files}", dir=out, files=", ".join(p.name for p in written.values()))
              + (" " + tr("(public mode)") if args.public else ""))
    print(tr("Next free IDs: {ids}", ids=" ".join(ids.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
