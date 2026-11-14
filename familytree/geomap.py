"""The map page: a heatmap of the family's births and deaths (or all events) on a map of Poland with
the borders of the partitions and on a map of the world. A standalone file and a variant without the
document skeleton (for hosts such as Claude artifacts). The map geometry (familytree/geodata) is
embedded, so the page loads nothing from other hosts except the fonts."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .dates import TODAY
from .geo import Geo
from .i18n import fill, language, tr
from .model import Tree

TEMPLATES = Path(__file__).parent / "templates"
GEODATA = Path(__file__).parent / "geodata"


def geometry() -> dict:
    out = {}
    for name in ("europe", "world", "overlay"):
        data = json.loads((GEODATA / f"{name}.json").read_text(encoding="utf-8"))
        data.pop("source", None)
        data.pop("note", None)
        out[name] = data
    return out


def map_data(tree: Tree, geo: Geo) -> dict:
    t = tree
    places = {}
    for plid in geo.by_place:
        lat, lon = geo.coords[plid]
        places[plid] = {"n": t.place_name(plid), "full": t.place_full(plid), "c": [lat, lon], "b": geo.basis[plid],
                        "area": geo.is_area(plid), "part": geo.partition_of(plid) or ""}
    persons = {pid: {"n": t.name(pid), "life": t.life_lines(t.persons[pid]), "k": t.kekule.get(pid, [])} for pid in geo.by_person}
    events = [{"p": e.pid, "k": e.kind, "pl": e.plid, "y": e.year, **({"e": 1} if e.estimated else {})} for e in geo.events]
    links = []
    for pid in t.kekule:
        a = geo.anchor(pid) if geo.shown(pid) else None
        for par in t.parents(pid) if a else []:
            if par in t.kekule and geo.shown(par) and (b := geo.anchor(par)) and b.plid != a.plid:
                links.append({"a": b.plid, "b": a.plid, "y": a.year if a.year is not None else b.year})
    clusters = [{"id": c.id, "label": geo.cluster_label(c), "lat": c.lat, "lon": c.lon, "r": c.radius_km, "n": len(c.events),
                 "years": geo.years_text(c.events), "places": c.places} for c in geo.clusters]
    return {"title": tree.project.get("name") or tr("Family tree"), "generated": TODAY.isoformat(), "places": places,
            "persons": persons, "events": events, "links": links, "clusters": clusters,
            "stats": {"on": len(geo.events), "off": sum(geo.unlocated.values()), "geocode": len(geo.unlocated)},
            "files": {"context": tr("geography.md")}}


def component(tree: Tree, geo: Geo) -> tuple[str, str]:
    """The map as a component of a page: its stylesheet, and its markup and script with the data filled in. The
    map page shows it alone; the tree page embeds it as its "Map" view."""
    css = (TEMPLATES / "map.css").read_text(encoding="utf-8")
    body = fill((TEMPLATES / "map_body.html").read_text(encoding="utf-8"))
    values = {"MAP_GEO": json.dumps(geometry(), separators=(",", ":")),
              "MAP_DATA": json.dumps(map_data(tree, geo), ensure_ascii=False).replace("</", "<\\/")}
    return css, re.sub(r"__(MAP_GEO|MAP_DATA)__", lambda m: values[m.group(1)], body)


def write_map(tree: Tree, geo: Geo, path: Path, artifact: bool = False) -> None:
    css, body = component(tree, geo)
    head = fill((TEMPLATES / "map_head.html").read_text(encoding="utf-8")).replace("__MAP_CSS__", css)
    if artifact:
        page = head + "\n" + body + "\n"
    else:
        page = (f'<!doctype html>\n<html lang="{language()}">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    path.write_text(page, encoding="utf-8")
