"""Interactive HTML page: a standalone file and a variant without the document skeleton (for hosts
such as Claude artifacts, which add <html>/<head>/<body> themselves). Besides the tree, the page carries the
family map (geomap.py) as its "Map" view."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .dates import TODAY, safe_date
from .geo import Geo
from .geomap import component
from .i18n import fill, language, tr
from .model import Tree
from .schema import LIFE_EVENTS, event_label, event_type_label, language_names

TEMPLATES = Path(__file__).parent / "templates"


def html_data(tree: Tree, public: bool) -> dict:
    persons = {}
    for pid, p in tree.persons.items():
        hidden = public and tree.living(pid)
        fam = tree.parents_family(pid)
        rec = {
            "name": tr("Living person") if hidden else tree.name(pid), "sex": p.get("sex", "U"),
            "by": None if hidden else tree.birth_year(p), "life": [] if hidden else tree.life_lines(p),
            "parents": [x for x in ((fam or {}).get("husband"), (fam or {}).get("wife")) if x],
            "families": [], "facts": [], "hints": [], "living": tree.living(pid),
        }
        married = p.get("married_surnames") or []
        rec["card"] = {"name": tr("Living person") if hidden else f"{p.get('given') or '?'} {(married or [p.get('surname') or '?'])[-1]}",
                       "maiden": tr("née {surname}", surname=p["surname"]) if married and p.get("surname") and not hidden else "",
                       "conf": p.get("confidence") or ""}
        for fid in tree.spouse_in.get(pid, []):
            f = tree.families[fid]
            spouse = f.get("wife") if f.get("husband") == pid else f.get("husband")
            m = tree.ev(f, "marriage")
            rec["families"].append({"spouse": spouse, "marriage": "" if hidden else tree.event_text(m),
                                    "sources": [] if hidden else m.get("sources") or [], "children": f.get("children") or []})
        if not hidden:
            for key in LIFE_EVENTS:
                ev = tree.ev(p, key)
                if ev:
                    extra = ([tr("age {age}", age=ev["age"])] if isinstance(ev.get("age"), int) else []) + ([ev["cause"]] if ev.get("cause") else [])
                    d = safe_date(ev.get("date"))
                    rec["facts"].append({"label": event_label(key), "date": d.text() if d else "",
                                         "place": tree.place_full(ev.get("place")), "note": "; ".join(extra + [ev.get("note") or ""]).strip("; "),
                                         "sources": ev.get("sources") or []})
            for e in p.get("events") or []:
                d = safe_date(e.get("date"))
                rec["facts"].append({"label": event_type_label(e.get("type")) + (f": {e['value']}" if e.get("value") else ""),
                                     "date": d.text() if d else "", "place": tree.place_full(e.get("place")),
                                     "note": e.get("note") or "", "sources": e.get("sources") or []})
            rec.update({k: p.get(k) for k in ("variants", "occupation", "religion", "notes", "confidence") if p.get(k)})
            rec["hints"] = [{"level": h.level, "text": h.text, "details": h.details, "links": h.links} for h in tree.person_hints(pid)]
        persons[pid] = rec
    families = {}
    for fid, f in tree.families.items():
        md = tree.date(f, "marriage")
        hidden = public and any(tree.living(x) for x in (f.get("husband"), f.get("wife")) if x)
        families[fid] = {"h": f.get("husband"), "w": f.get("wife"), "c": f.get("children") or [],
                         "m": md.text() if md and not hidden else ""}
    sources = {}
    for sid, s in tree.sources.items():
        sources[sid] = {k: s.get(k) for k in ("title", "url", "repository", "signature", "type", "quality") if s.get(k)}
        if langs := language_names(s.get("language")):
            sources[sid]["language"] = ", ".join(langs)
    return {"title": tree.project.get("name") or tr("Family tree"), "generated": TODAY.isoformat(),
            "proband": tree.project.get("proband"), "persons": persons, "families": families, "sources": sources}


def _templates() -> tuple[str, str]:
    head = fill((TEMPLATES / "head.html").read_text(encoding="utf-8"))
    body = fill((TEMPLATES / "body.html").read_text(encoding="utf-8"))
    layout = fill((TEMPLATES / "layout.js").read_text(encoding="utf-8"))   # the diagram is laid out in the page
    return head, body.replace("__LAYOUT__", layout)


def standalone_template() -> str:
    head, body = _templates()
    return ('<!doctype html>\n<html lang="__LANG__">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def artifact_template() -> str:
    head, body = _templates()
    return head + "\n" + body + "\n"


def write_html(tree: Tree, path: Path, public: bool, artifact: bool = False, geo: Geo | None = None) -> None:
    template = artifact_template() if artifact else standalone_template()
    css, body = component(tree, geo) if geo else ("", "")
    values = {"LANG": language(), "TITLE": (tree.project.get("name") or tr("Family tree")).replace("<", "&lt;"),
              "DATA": json.dumps(html_data(tree, public), ensure_ascii=False).replace("</", "<\\/"),
              "MAP_CSS": css, "MAP": body}
    page = re.sub(r"__(LANG|TITLE|DATA|MAP_CSS|MAP)__", lambda m: values[m.group(1)], template)   # one pass: data stays as is
    path.write_text(page, encoding="utf-8")
