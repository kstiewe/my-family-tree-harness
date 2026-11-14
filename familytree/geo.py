"""Geography of the tree: where the family's events happened, clusters of places, migration trails
along the lines of ancestors and heuristic hints for finding missing ancestors.

The map page (geomap.py) and the geography context for agents (geography.md / geography.json) are
built from it. A place is located by its own `coords`, or by the `coords` of its parish when it has
none. Clusters, trails and hints only suggest where to search — they are never evidence.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .dates import TODAY, safe_date
from .i18n import tr
from .schema import PARTITIONS, place_kind

if TYPE_CHECKING:
    from .model import Tree

CLUSTER_KM = 20.0      # a place joins a cluster whose centre is closer than this
NEAR_KM = 25.0         # radius of "neighbouring" parishes and places around a reference point
MOVE_KM = 10.0         # a change of place shorter than this is not a move
KINDS = ("birth", "death", "marriage", "residence", "other")
RESIDENCE_TYPES = {"residence", "census", "emigration"}
AREA_KINDS = {"region", "commune", "county", "country"}       # places that are areas, not points
COMPASS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def valid_coords(c) -> bool:
    return (isinstance(c, list) and len(c) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in c)
            and -90 <= c[0] <= 90 and -180 <= c[1] <= 180)


def distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(min(1.0, h)))


def compass(a: tuple[float, float], b: tuple[float, float]) -> str:
    """Direction from a to b as one of COMPASS."""
    p1, p2, dl = math.radians(a[0]), math.radians(b[0]), math.radians(b[1] - a[1])
    deg = math.degrees(math.atan2(math.sin(dl) * math.cos(p2),
                                  math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)))
    return COMPASS[round(((deg + 360) % 360) / 45) % 8]


def compass_label(code: str) -> str:
    return tr({"N": "N", "NE": "NE", "E": "E", "SE": "SE", "S": "S", "SW": "SW", "W": "W", "NW": "NW"}[code])


def kind_label(kind: str) -> str:
    return tr({"birth": "birth", "death": "death", "marriage": "marriage", "residence": "residence",
               "other": "other event"}[kind])


@dataclass
class Event:
    pid: str
    kind: str                    # one of KINDS
    plid: str
    year: int | None
    estimated: bool = False      # the year is an estimate (the data has no date)
    fid: str | None = None       # the family of a marriage


@dataclass
class Cluster:
    id: str
    lat: float
    lon: float
    radius_km: float
    places: list[str]            # most events first
    events: list[Event]

    @property
    def center(self) -> tuple[float, float]:
        return (self.lat, self.lon)


class Geo:
    def __init__(self, tree: Tree, living: bool = True):
        """living=False leaves living persons out (public outputs, hints shown in the tree)."""
        self.tree = tree
        self.living = living
        self.coords: dict[str, tuple[float, float]] = {}
        self.basis: dict[str, str] = {}           # "place" (own coords) or "parish" (the parish's)
        for plid, pl in tree.places.items():
            par = tree.parish_of(plid)
            if valid_coords(pl.get("coords")):
                self.coords[plid], self.basis[plid] = tuple(pl["coords"]), "place"
            elif par and par is not pl and valid_coords(par.get("coords")):
                self.coords[plid], self.basis[plid] = tuple(par["coords"]), "parish"
        self.events: list[Event] = []
        self.unlocated: Counter[str] = Counter()   # place → events that cannot be put on the map
        self._collect()
        self.by_person: dict[str, list[Event]] = {}
        self.by_place: dict[str, list[Event]] = {}
        for e in self.events:
            self.by_person.setdefault(e.pid, []).append(e)
            self.by_place.setdefault(e.plid, []).append(e)
        self.clusters = self._clusters()
        self.cluster_of = {plid: c for c in self.clusters for plid in c.places}

    # ---- events

    def shown(self, pid: str | None) -> bool:
        return bool(pid) and pid in self.tree.persons and (self.living or not self.tree.living(pid))

    def is_area(self, plid: str) -> bool:
        return place_kind(self.tree.places.get(plid) or {}) in AREA_KINDS

    def _add(self, pid: str, kind: str, plid: str | None, date, estimate: int | None = None, fid: str | None = None) -> None:
        if not plid or plid not in self.tree.places:
            return
        if plid not in self.coords:
            self.unlocated[plid] += 1
            return
        d = safe_date(date)
        year = d.year if d else estimate
        self.events.append(Event(pid, kind, plid, year, estimated=not d and estimate is not None, fid=fid))

    def _collect(self) -> None:
        t = self.tree
        for pid, p in t.persons.items():
            if not self.shown(pid):
                continue
            for kind, keys in (("birth", ("birth", "baptism")), ("death", ("death", "burial"))):
                evs = [t.ev(p, k) for k in keys]
                where = next((e for e in evs if e.get("place")), None)
                if not where:
                    continue
                date = where.get("date") or next((e.get("date") for e in evs if e.get("date")), None)
                estimate = None
                if kind == "birth" and not date and (w := t.birth_window(pid)) and w.lo and w.hi:
                    estimate = (w.lo + w.hi) // 2
                self._add(pid, kind, where["place"], date, estimate)
            for e in p.get("events") or []:
                if isinstance(e, dict):
                    self._add(pid, "residence" if e.get("type") in RESIDENCE_TYPES else "other", e.get("place"), e.get("date"))
        for fid, f in t.families.items():
            m = t.ev(f, "marriage")
            for role in ("husband", "wife"):
                if self.shown(f.get(role)):
                    self._add(f[role], "marriage", m.get("place"), m.get("date"), fid=fid)

    # ---- clusters

    def _clusters(self) -> list[Cluster]:
        weight = Counter(e.plid for e in self.events if not self.is_area(e.plid))
        order = sorted(weight, key=lambda plid: (-weight[plid], plid))
        seeds: list[tuple[float, float]] = []
        for plid in order:                         # leader clustering: the busiest places become centres
            if not any(distance_km(self.coords[plid], s) < CLUSTER_KM for s in seeds):
                seeds.append(self.coords[plid])
        groups: dict[int, list[str]] = {}
        for plid in order:
            i = min(range(len(seeds)), key=lambda k: distance_km(self.coords[plid], seeds[k]))
            groups.setdefault(i, []).append(plid)
        out = []
        for members in groups.values():
            w = sum(weight[p] for p in members)
            lat = sum(self.coords[p][0] * weight[p] for p in members) / w
            lon = sum(self.coords[p][1] * weight[p] for p in members) / w
            radius = max(distance_km((lat, lon), self.coords[p]) for p in members)
            events = [e for p in members for e in self.by_place[p]]
            out.append(Cluster("", round(lat, 4), round(lon, 4), round(radius, 1), members, events))
        out.sort(key=lambda c: (-len(c.events), c.places[0]))
        for i, c in enumerate(out, 1):
            c.id = f"C{i}"
        return out

    def cluster_label(self, c: Cluster) -> str:
        name = self.tree.place_name(c.places[0])
        return name if len(c.places) == 1 else tr("{place} and surroundings", place=name)

    @staticmethod
    def years(events: list[Event]) -> tuple[int, int] | None:
        ys = [e.year for e in events if e.year is not None]
        return (min(ys), max(ys)) if ys else None

    def years_text(self, events: list[Event]) -> str:
        y = self.years(events)
        return "" if not y else str(y[0]) if y[0] == y[1] else f"{y[0]}–{y[1]}"

    # ---- persons along the lines of ancestors

    def anchor(self, pid: str) -> Event | None:
        """The place that stands for a person on a trail: birth, else marriage, residence, death."""
        evs = self.by_person.get(pid, [])
        for kind in ("birth", "marriage", "residence", "death", "other"):
            hits = [e for e in evs if e.kind == kind and not self.is_area(e.plid)]
            if hits:
                return min(hits, key=lambda e: (e.year is None, e.year or 0))
        return None

    def trails(self) -> list[dict]:
        t = self.tree
        by_num = {n: pid for pid, ns in t.kekule.items() for n in ns}
        tops = sorted((pid for pid in t.kekule if self.shown(pid) and not t.parents(pid)), key=lambda pid: min(t.kekule[pid]))
        out = []
        for top in tops:
            n, steps = min(t.kekule[top]), []
            while n >= 1:
                pid = by_num[n]
                if self.shown(pid) and (a := self.anchor(pid)):
                    steps.append((n, pid, a))
                n //= 2
            if len(steps) < 2:
                continue
            key = tuple(pid for _, pid, _ in steps)
            if same := next((x for x in out if x["_key"] == key), None):
                same["tops"].append({"id": top, "kekule": min(t.kekule[top]), "name": t.name(top)})
                continue
            legs = []
            for (n1, p1, a1), (n2, p2, a2) in zip(steps, steps[1:]):
                c1, c2 = self.coords[a1.plid], self.coords[a2.plid]
                legs.append({"from": p1, "to": p2, "km": round(distance_km(c1, c2)), "direction": compass(c1, c2)})
            first, last = self.coords[steps[0][2].plid], self.coords[steps[-1][2].plid]
            out.append({"_key": key, "tops": [{"id": top, "kekule": min(t.kekule[top]), "name": t.name(top)}],
                        "steps": [self._step(n, pid, a) for n, pid, a in steps],
                        "legs": legs, "total_km": sum(leg["km"] for leg in legs), "net_km": round(distance_km(first, last)),
                        "net_direction": compass(first, last) if first != last else ""})
        for x in out:
            del x["_key"]
        return out

    def _step(self, n: int, pid: str, a: Event) -> dict:
        lat, lon = self.coords[a.plid]
        return {"kekule": n, "id": pid, "name": self.tree.name(pid), "event": a.kind, "place": a.plid,
                "place_name": self.tree.place_name(a.plid), "year": a.year, "estimated": a.estimated, "lat": lat, "lon": lon}

    def moves(self) -> list[dict]:
        """Changes of place of at least MOVE_KM: from parent to child along the lines of ancestors,
        and within one ancestor's life (birth → death)."""
        t, out, seen = self.tree, [], set()
        for pid, nums in t.kekule.items():
            if not self.shown(pid) or not (a := self.anchor(pid)):
                continue
            for par in t.parents(pid):
                if par in t.kekule and self.shown(par) and (b := self.anchor(par)) and (par, pid) not in seen:
                    seen.add((par, pid))
                    out.append(self._move("generation", par, b, pid, a))
            births = [e for e in self.by_person[pid] if e.kind == "birth"]
            deaths = [e for e in self.by_person[pid] if e.kind == "death"]
            if births and deaths:
                out.append(self._move("life", pid, births[0], pid, deaths[0]))
        return sorted((m for m in out if m["km"] >= MOVE_KM), key=lambda m: -m["km"])

    def _move(self, kind: str, p1: str, e1: Event, p2: str, e2: Event) -> dict:
        c1, c2 = self.coords[e1.plid], self.coords[e2.plid]
        return {"kind": kind, "from_person": p1, "from_place": e1.plid, "from_year": e1.year,
                "to_person": p2, "to_place": e2.plid, "to_year": e2.year,
                "km": round(distance_km(c1, c2)), "direction": compass(c1, c2)}

    # ---- neighbourhoods and hints

    def reference(self, pid: str, purpose: str) -> tuple[str, str] | None:
        """The first located place that tells where to search for a person's birth or death:
        their own, the places the gap report suggests, then the closest relatives' places."""
        t, p = self.tree, self.tree.persons[pid]
        keys = ("birth", "baptism") if purpose == "birth" else ("death", "burial")
        cands = [(t.ev(p, k).get("place"), tr("place of birth") if purpose == "birth" else tr("place of death")) for k in keys]
        cands += t.search_places(pid, purpose)
        if purpose == "birth":
            fam = t.parents_family(pid)
            for sib in (fam or {}).get("children") or []:
                if sib != pid:
                    s = t.persons[sib]
                    cands.append((t.ev(s, "birth").get("place") or t.ev(s, "baptism").get("place"), tr("place of birth of a sibling")))
            for fid in t.spouse_in.get(pid, []):
                f = t.families[fid]
                sp = f.get("wife") if f.get("husband") == pid else f.get("husband")
                if sp in t.persons and (a := self.anchor(sp)):
                    cands.append((a.plid, tr("place of the spouse")))
            for par in t.parents(pid):
                if a := self.anchor(par):
                    cands.append((a.plid, tr("place of a parent")))
        for plid, label in cands:
            if plid and plid in self.coords and not self.is_area(plid):
                return plid, label
        return None

    def located(self, pid: str, purpose: str) -> bool:
        return any(e.kind == purpose for e in self.by_person.get(pid, []))

    def parishes_near(self, plid: str, km: float = NEAR_KM) -> list[tuple[str, float, str]]:
        """Parishes in places.yaml within km of a place (its own parish left out), nearest first."""
        here, own = self.coords[plid], (self.tree.parish_of(plid) or {}).get("id")
        out = []
        for pid_, pl in self.tree.places.items():
            if place_kind(pl) == "parish" and pid_ != own and pid_ in self.coords and self.basis[pid_] == "place":
                d = distance_km(here, self.coords[pid_])
                if d <= km:
                    out.append((pid_, d, compass(here, self.coords[pid_])))
        return sorted(out, key=lambda x: x[1])

    def places_near(self, plid: str, km: float = NEAR_KM) -> list[tuple[str, float, str]]:
        """Family places (with events) within km of a place, nearest first."""
        here = self.coords[plid]
        out = [(other, distance_km(here, self.coords[other]), compass(here, self.coords[other]))
               for other in self.by_place if other != plid and not self.is_area(other)]
        return sorted((x for x in out if x[1] <= km), key=lambda x: x[1])

    def nearest_clusters(self, plid: str, n: int = 3) -> list[tuple[Cluster, float, str]]:
        here = self.coords[plid]
        out = [(c, distance_km(here, c.center), compass(here, c.center)) for c in self.clusters]
        return sorted(out, key=lambda x: x[1])[:n]

    def descendants(self, pid: str) -> set[str]:
        t, out, stack = self.tree, set(), [pid]
        while stack:
            for fid in t.spouse_in.get(stack.pop(), []):
                for c in t.families[fid].get("children") or []:
                    if c not in out:
                        out.add(c)
                        stack.append(c)
        return out

    def surname_places(self, pid: str, plid: str | None, n: int = 5) -> list[tuple[str, int, float | None]]:
        """Places where other persons born with the same surname (Kowalski = Kowalska) have events,
        the person's own descendants left out: where else the name occurs in the data."""
        key = surname_key(self.tree.persons[pid].get("surname"))
        if not key:
            return []
        skip = self.descendants(pid) | {pid}
        hits: Counter[str] = Counter()
        for other, evs in self.by_person.items():
            if other not in skip and surname_key(self.tree.persons[other].get("surname")) == key:
                hits.update(e.plid for e in evs if not self.is_area(e.plid))
        here = self.coords.get(plid or "")
        rows = [(x, k, distance_km(here, self.coords[x]) if here else None) for x, k in hits.items()]
        return sorted(rows, key=lambda r: (r[2] if r[2] is not None else 0, -r[1]))[:n]

    def near_text(self, rows: list[tuple[str, float, str]], limit: int = 5) -> str:
        return ", ".join(tr("{place} ({km} km {direction})", place=self.tree.place_name(x), km=max(1, round(d)),
                            direction=compass_label(c)) for x, d, c in rows[:limit])

    def hint_lines(self, pid: str, purpose: str) -> list[str]:
        """At most two lines for the person's hints in the gap report and the tree: neighbouring
        parishes and the nearest other family cluster around the best reference place."""
        if not self.shown(pid):
            return []
        need = not self.located(pid, purpose) or (purpose == "birth" and len(self.tree.parents(pid)) < 2)
        ref = self.reference(pid, purpose) if need else None
        if not ref:
            return []
        plid, label = ref
        name = self.tree.place_name(plid)
        pars = self.parishes_near(plid)
        lines = [tr("Map: parishes within {km} km of {place} ({basis}) — check their books too: {list}", km=round(NEAR_KM),
                    place=name, basis=label, list=self.near_text(pars)) if pars
                 else tr("Map: no other parish within {km} km of {place} is in places.yaml — look up the neighbouring "
                         "parishes and add them with coords.", km=round(NEAR_KM), place=name)]
        own = self.cluster_of.get(plid)
        other = [(c, d, k) for c, d, k in self.nearest_clusters(plid, 4) if c is not own]
        if other:
            c, d, k = other[0]
            lines.append(tr("Nearest other family cluster: {cluster}, {km} km {direction} (events: {n}, {years}).",
                            cluster=self.cluster_label(c), km=max(1, round(d)), direction=compass_label(k),
                            n=len(c.events), years=self.years_text(c.events) or "?"))
        return lines

    def research_hints(self) -> list[dict]:
        """For each deceased ancestor: what is missing geographically and where to look first."""
        t, out = self.tree, []
        for pid in sorted(t.kekule, key=lambda x: min(t.kekule[x])):
            if t.living(pid) or not self.shown(pid):
                continue
            needs = []
            if not self.located(pid, "birth"):
                needs.append("birth_place")
            if len(t.parents(pid)) < 2:
                needs.append("parents")
            if not self.located(pid, "death"):
                needs.append("death_place")
            if not needs:
                continue
            purpose = "birth" if needs[0] in ("birth_place", "parents") else "death"
            ref = self.reference(pid, purpose) or self.reference(pid, "death" if purpose == "birth" else "birth")
            w = t.birth_window(pid)
            row = {"id": pid, "kekule": t.kekule[pid], "name": t.name(pid), "needs": needs,
                   "birth_estimate": w.text() if w else None, "reference": None}
            if ref:
                plid, label = ref
                lat, lon = self.coords[plid]
                row["reference"] = {"place": plid, "name": t.place_name(plid), "why": label, "lat": lat, "lon": lon,
                                    "coords_from": self.basis[plid], "geneteka_region": t.region_of(plid)}
                row["parishes_nearby"] = [{"place": x, "name": t.place_name(x), "km": round(d, 1), "direction": c}
                                          for x, d, c in self.parishes_near(plid)]
                row["family_places_nearby"] = [{"place": x, "name": t.place_name(x), "km": round(d, 1), "direction": c,
                                                "events": len(self.by_place[x])} for x, d, c in self.places_near(plid)[:8]]
                row["nearest_clusters"] = [{"cluster": c.id, "label": self.cluster_label(c), "km": round(d, 1), "direction": k}
                                           for c, d, k in self.nearest_clusters(plid)]
            row["same_surname_places"] = [{"place": x, "name": t.place_name(x), "events": k,
                                           "km": None if d is None else round(d, 1)}
                                          for x, k, d in self.surname_places(pid, ref[0] if ref else None)]
            out.append(row)
        return out

    def to_geocode(self) -> list[dict]:
        t = self.tree
        return [{"place": plid, "name": t.place_name(plid), "events": n,
                 "parish": (t.parish_of(plid) or {}).get("id") if t.parish_of(plid) is not t.places[plid] else None}
                for plid, n in sorted(self.unlocated.items(), key=lambda x: (-x[1], x[0]))]

    def unplaced_ancestors(self) -> list[str]:
        return [pid for pid in sorted(self.tree.kekule, key=lambda x: min(self.tree.kekule[x]))
                if self.shown(pid) and not self.by_person.get(pid)]

    def partition_of(self, plid: str) -> str | None:
        t = self.tree
        value = (t.places.get(plid) or {}).get("partition") or (t.parish_of(plid) or {}).get("partition")
        return PARTITIONS.get(value) if value else None

    def partition_key(self, plid: str) -> str:
        """The partition of a place, "abroad" for a place outside Poland, "unknown" when not recorded."""
        country = (self.tree.places.get(plid) or {}).get("country") or (self.tree.parish_of(plid) or {}).get("country")
        return self.partition_of(plid) or ("abroad" if country and country != "PL" else "unknown")

    # ---- outputs for agents

    def cluster_json(self, c: Cluster) -> dict:
        t = self.tree
        pids = sorted({e.pid for e in c.events})
        surnames = Counter(t.persons[p].get("surname") for p in pids if t.persons[p].get("surname"))
        y = self.years(c.events)
        return {"id": c.id, "label": self.cluster_label(c), "lat": c.lat, "lon": c.lon, "radius_km": c.radius_km,
                "events": len(c.events), "by_kind": dict(Counter(e.kind for e in c.events)),
                "years": list(y) if y else None,
                "places": [{"place": p, "name": t.place_name(p), "events": len(self.by_place[p]),
                            "coords_from": self.basis[p]} for p in c.places],
                "persons": pids, "ancestors": [{"id": p, "kekule": t.kekule[p], "name": t.name(p)} for p in pids if p in t.kekule],
                "surnames": dict(surnames.most_common()),
                "partitions": sorted({x for p in c.places if (x := self.partition_of(p))})}

    def context_json(self) -> dict:
        t = self.tree
        return {
            "generated": TODAY.isoformat(), "living_persons_included": self.living,
            "parameters": {"cluster_km": CLUSTER_KM, "near_km": NEAR_KM, "move_km": MOVE_KM},
            "summary": {"events_on_map": len(self.events), "events_without_coords": sum(self.unlocated.values()),
                        "places_with_coords": sum(1 for b in self.basis.values() if b == "place"),
                        "places_with_parish_coords": sum(1 for b in self.basis.values() if b == "parish"),
                        "places_without_coords": len(t.places) - len(self.coords), "clusters": len(self.clusters),
                        "by_kind": dict(Counter(e.kind for e in self.events)),
                        "by_partition": dict(Counter(self.partition_key(e.plid) for e in self.events))},
            "clusters": [self.cluster_json(c) for c in self.clusters],
            "trails": self.trails(), "moves": self.moves(), "hints": self.research_hints(),
            "to_geocode": self.to_geocode(), "ancestors_without_any_place": self.unplaced_ancestors(),
        }

    def context_md(self, data: dict) -> str:
        t = self.tree
        s = data["summary"]
        L = [tr("# Geography of the family"), "",
             tr("_Generated {date} by `scripts/build.py` — do not edit by hand._", date=TODAY.isoformat()), "",
             tr("Context for research: where the family's events happened, clusters of places, migration trails along "
                "the lines of ancestors and where to look for the missing ones. Distances are straight lines; a place "
                "without coordinates takes those of its parish. Everything here is a heuristic for choosing where to "
                "search — never evidence. The same data as JSON: geography.json; on a map: map.html."), "",
             tr("## Summary"), "",
             tr("- events on the map: {n} (without coordinates: {missing})", n=s["events_on_map"], missing=s["events_without_coords"]),
             tr("- places with coordinates: {own}, with the parish's coordinates: {parish}, without: {none}",
                own=s["places_with_coords"], parish=s["places_with_parish_coords"], none=s["places_without_coords"]),
             tr("- clusters (places within {km} km of a centre): {n}", km=round(CLUSTER_KM), n=s["clusters"])]
        if s["by_kind"]:
            L.append(tr("- events by kind: {list}", list=", ".join(f"{kind_label(k)} {n}" for k, n in s["by_kind"].items())))
        if s["by_partition"]:
            L.append(tr("- events by partition: {list}", list=", ".join(f"{partition_label(k)} {n}" for k, n in s["by_partition"].items())))
        L += ["", tr("## Clusters"), ""]
        for c in data["clusters"]:
            L += [f"### {c['id']} · {c['label']} · " + tr("events: {n}", n=c["events"])
                  + (f" · {c['years'][0]}–{c['years'][1]}" if c["years"] else ""), ""]
            L.append(tr("- centre {lat}, {lon}; radius {km} km", lat=c["lat"], lon=c["lon"], km=c["radius_km"]))
            L.append(tr("- places: {list}", list=", ".join(f"{p['name']} `{p['place']}` ({p['events']})" for p in c["places"])))
            L.append(tr("- events: {list}", list=", ".join(f"{kind_label(k)} {n}" for k, n in c["by_kind"].items())))
            if c["ancestors"]:
                L.append(tr("- ancestors: {list}", list=", ".join(f"{', '.join(map(str, a['kekule']))} {a['name']}" for a in c["ancestors"])))
            if c["surnames"]:
                L.append(tr("- surnames: {list}", list=", ".join(f"{k} ({n})" for k, n in c["surnames"].items())))
            if c["partitions"]:
                L.append(tr("- partition: {list}", list=", ".join(partition_label(x) for x in c["partitions"])))
            L.append("")
        if not data["clusters"]:
            L += [tr("_No events with coordinates yet — add `coords` to the places in places.yaml._"), ""]
        L += [tr("## Migration trails along the lines of ancestors"), "",
              tr("_From the oldest known ancestors of each line down to the proband; each person stands at the place of "
                 "birth (else marriage, residence, death); (est.) = estimated year._"), ""]
        for trail in data["trails"]:
            parts = []
            for i, st in enumerate(trail["steps"]):
                if i:
                    leg = trail["legs"][i - 1]
                    parts.append(f"→ {leg['km']} km {compass_label(leg['direction'])} →" if leg["km"] >= 1 else "→")
                year = f" {st['year']}" + (" " + tr("(est.)") if st["estimated"] else "") if st["year"] else ""
                parts.append(f"{st['place_name']}{year} [{st['kekule']}]")
            net = (tr("; overall {km} km {direction}", km=trail["net_km"], direction=compass_label(trail["net_direction"]))
                   if trail["net_direction"] else "")
            tops = ", ".join(f"{x['name']} (" + tr("no. {n}", n=x["kekule"]) + ")" for x in trail["tops"])
            L.append(f"- **{tops}**: " + " ".join(parts) + net)
        if not data["trails"]:
            L.append(tr("_None._"))
        L += ["", tr("## Largest moves"), "",
              tr("_Changes of place of at least {km} km — where a line moved, the next generation's records are in "
                 "another parish (or archive)._", km=round(MOVE_KM)), ""]
        for m in data["moves"][:15]:
            who = t.name(m["to_person"]) if m["kind"] == "life" else f"{t.name(m['from_person'])} → {t.name(m['to_person'])}"
            what = tr("birth → death") if m["kind"] == "life" else tr("parent → child")
            L.append(tr("- {km} km {direction}: {a} ({ya}) → {b} ({yb}) — {who}, {what}", km=m["km"],
                        direction=compass_label(m["direction"]), a=t.place_name(m["from_place"]), ya=m["from_year"] or "?",
                        b=t.place_name(m["to_place"]), yb=m["to_year"] or "?", who=who, what=what))
        if not data["moves"]:
            L.append(tr("_None._"))
        L += ["", tr("## Where to look for missing ancestors"), "",
              tr("_For each deceased ancestor without a located birth or death or without parents. The reference place is "
                 "the closest located clue; neighbouring parishes are only those already in places.yaml — the diocese's "
                 "list of parishes or `scripts/geneteka.py --parishes` gives the others._"), ""]
        needs = {"birth_place": tr("place of birth"), "parents": tr("parents"), "death_place": tr("place of death")}
        for h in data["hints"]:
            L += [f"### {', '.join(map(str, h['kekule']))} · {h['name']} · `{h['id']}`", ""]
            L.append(tr("- missing: {list}", list=", ".join(needs[n] for n in h["needs"]))
                     + (" · " + tr("estimated birth: {years}", years=h["birth_estimate"]) if h["birth_estimate"] else ""))
            ref = h["reference"]
            if not ref:
                L.append(tr("- no located clue: add coordinates to the places of this person and of the closest relatives"))
            else:
                L.append(tr("- reference place: {place} `{id}` — {why}", place=ref["name"], id=ref["place"], why=ref["why"])
                         + (" " + tr("(coordinates of the parish)") if ref["coords_from"] == "parish" else "")
                         + (f" · Geneteka `{ref['geneteka_region']}`" if ref["geneteka_region"] else ""))
                if h["parishes_nearby"]:
                    L.append(tr("- parishes within {km} km: {list}", km=round(NEAR_KM), list=", ".join(
                        f"{x['name']} `{x['place']}` ({round(x['km'])} km {compass_label(x['direction'])})" for x in h["parishes_nearby"])))
                if h["family_places_nearby"]:
                    L.append(tr("- family places within {km} km: {list}", km=round(NEAR_KM), list=", ".join(
                        f"{x['name']} ({round(x['km'])} km {compass_label(x['direction'])}, {x['events']})" for x in h["family_places_nearby"])))
                if h["nearest_clusters"]:
                    L.append(tr("- nearest clusters: {list}", list=", ".join(
                        f"{x['cluster']} {x['label']} ({round(x['km'])} km)" for x in h["nearest_clusters"])))
            if h["same_surname_places"]:
                L.append(tr("- the same surname elsewhere in the data: {list}", list=", ".join(
                    f"{x['name']} ({x['events']}" + (f", {round(x['km'])} km" if x["km"] is not None else "") + ")"
                    for x in h["same_surname_places"])))
            L.append("")
        if not data["hints"]:
            L += [tr("_None._"), ""]
        L += [tr("## Places to geocode"), "",
              tr("_Places used by events that the map cannot show: add `coords` (and the source of the coordinates in "
                 "`notes`), or the parish when it has coordinates._"), ""]
        L += [tr("- `{id}` {name} — events: {n}", id=g["place"], name=g["name"], n=g["events"])
              + ("" if g["parish"] else " · " + tr("parish unknown")) for g in data["to_geocode"]] or [tr("_None._")]
        if data["ancestors_without_any_place"]:
            L += ["", tr("**Ancestors without any place on the map:** {list}", list=", ".join(
                f"{t.name(p)} `{p}`" for p in data["ancestors_without_any_place"]))]
        return "\n".join(L) + "\n"

    def gap_lines(self) -> list[str]:
        """The geography section of the gap report."""
        L = [tr("- events on the map: {n} (without coordinates: {missing})", n=len(self.events), missing=sum(self.unlocated.values()))]
        for c in self.clusters[:5]:
            L.append(tr("- cluster {id} {label}: events: {n}, {years}", id=c.id, label=self.cluster_label(c), n=len(c.events),
                        years=self.years_text(c.events) or "?"))
        geocode = self.to_geocode()
        if geocode:
            L.append(tr("- places to geocode (most events first): {list}", list=", ".join(
                f"{g['name']} `{g['place']}` ({g['events']})" for g in geocode[:10])))
        L.append(tr("- clusters, migration trails and hints per ancestor: {file}; the map: {map}",
                    file=tr("geography.md"), map=tr("map.html")))
        return L


def surname_key(surname: str | None) -> str:
    """A surname folded so that the male and female forms match (Kowalski, Kowalska; Nowak, Nowakówna)."""
    from .model import fold
    s = fold(surname or "").strip()
    for fem, masc in (("cka", "cki"), ("dzka", "dzki"), ("ska", "ski"), ("owna", "")):
        if s.endswith(fem) and len(s) > len(fem) + 2:
            return s[: -len(fem)] + masc
    return s


def partition_label(value: str) -> str:
    return tr({"russian": "Russian partition", "prussian": "Prussian partition", "austrian": "Austrian partition",
               "abroad": "outside Poland", "unknown": "partition not recorded"}[value])


def write_geography(geo: Geo, md: Path, js: Path) -> None:
    data = geo.context_json()
    js.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    md.write_text(geo.context_md(data), encoding="utf-8")
