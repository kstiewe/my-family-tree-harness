"""Evidence-based confidence: a score 0–100 for every parent–child link and every fact, computed from the sources.

The model follows the Genealogical Proof Standard (GPS) and its evidence analysis; docs/confidence.md explains the
terms, the table of points and the thresholds. In short:

- a source is **original** (a record made at the time, or an image of it), **derivative** (an index entry, a
  transcription, an abstract) or **authored** (a family account, someone's tree, a publication);
- the information it gives is **primary** (from someone who knew it first-hand, at the time) or **secondary**;
- as evidence for a question it is **direct** (it answers the question alone: a baptism record names the parents)
  or **indirect** (only together with other evidence: the parents' marriage, an age that gives a year of birth).

Every citation of a source (a source ID in an event's `sources`) is one piece of evidence for one question. The
defaults come from fields that already exist (`type`, `quality`, the event that cites the source, whose event it is,
whether the transcription names the parents); optional fields of the source override them (`classification`,
`information`, `evidence`). Citations of one record count once (`RecordGroups`: the index entry and the image of one
act, two indexes of one act, two accounts of one informant). The strongest record is the anchor; independent
records add corroboration with diminishing weight; a local copy (`file`) and a transcription add a little;
conflicts and chronology warnings subtract. "confirmed" needs direct evidence from an original source with primary
information, a second independent record with direct evidence and no unresolved conflict. A manual `confidence` is
an upper cap; `confidence_override` replaces the computed score and shows its reason.

Scores, each with a breakdown ("why this score") and suggestions ("to strengthen"):

- link(child, family): the child is the child of the family's parents and the same person as in the records
  (identity: the records name the parents, ages and places agree, namesakes checked). Evidence: the child's
  birth/baptism sources, the child's death and marriage records, the parents' marriage (indirect), family accounts
  cited on the child's extra events, and the sources of the optional `parentage` field;
- facts: the birth (birth or baptism) and the death (death or burial) of a person, the marriage of a family;
- union(family): how well the couple is attested (the marriage, or a child's link) — the step to a spouse;
- path(person): the weakest link between the proband and the person; with several paths, the best one. Exception:
  the link of a living person (the union of a couple with a living spouse) does not lower the path — only a manual
  label caps it — because the family knows it first-hand and the records are not public.

`scores(tree)` computes everything once per tree. The page gets the per-link scores and computes the paths for the
proband picked there (templates/layout.js); `Confidence.paths()` does the same here for the reports.
"""

from __future__ import annotations

import heapq
import re
import weakref
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .dates import TODAY, search_range
from .i18n import tr
from .model import Tree, fold
from .schema import EVIDENCE, INFORMATION, LIFE_EVENTS, SOURCE_CLASSES

# ---- the scale

BANDS = (("confirmed", 85), ("probable", 60), ("hypothesis", 30), ("unsupported", 0))
MANUAL_CAP = {"probable": 84, "hypothesis": 59}        # a manual label is an upper cap; "confirmed" caps nothing
GATE_CAP = 84                                           # the highest score without the conditions of "confirmed"

# ---- the table of points (docs/confidence.md)

CLASS_BASE = {"original": 70, "derivative": 55, "authored": 45}
TYPE_BASE = {"online_tree": 25}                         # someone else's tree is a lead, not evidence
INFO_FACTOR = {"primary": 1.0, "secondary": 0.75}
EVIDENCE_FACTOR = {"direct": 1.0, "indirect": 0.6}
FILE_POINTS = {"original": 8, "derivative": 3, "authored": 0}
TRANSCRIPTION_POINTS = 5
CORROBORATION = (0.4, 0.2, 0.1)                         # share of the strength of the 2nd, 3rd and 4th record
CORROBORATION_CAP = 30
UNRESOLVED, RESOLVED, CHRONOLOGY, CONTRADICTION = -20, -5, -10, -10
NAMESAKES_POINTS = {"excluded": 5, "possible": -15}
PARENTS_NAMED, AGES_AGREE, SAME_PARISH = 5, 3, 3

BIRTH_TYPES = {"birth_record", "baptism_record", "civil_record", "index"}
DEATH_TYPES = {"death_record", "burial_record", "civil_record", "index"}
MARRIAGE_TYPES = {"marriage_record", "civil_record", "index"}
NARRATIVE_TYPES = {"oral", "online_tree", "publication"}
# sources that state a date outright, though seldom first-hand (secondary, direct)
STATING_TYPES = NARRATIVE_TYPES | {"family_document", "population_register", "census", "gravestone"}
PRIMARY_FOR = {"birth": BIRTH_TYPES, "death": DEATH_TYPES | {"gravestone"}, "marriage": MARRIAGE_TYPES}

_SOURCE_ID = re.compile(r"\bS\d{4,}\b")
# Cyrillic to Latin letters (Polish spelling), to find the parents' names in Russian transcriptions.
_CYRILLIC = str.maketrans({
    "а": "a", "б": "b", "в": "w", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "z", "з": "z", "и": "i", "й": "j",
    "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
    "х": "ch", "ц": "c", "ч": "cz", "ш": "sz", "щ": "szcz", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "ju",
    "я": "ja", "і": "i", "ї": "i", "є": "e", "ѣ": "e", "ґ": "g"})


def band(score: int | None) -> str | None:
    if score is None:
        return None
    return next(key for key, lo in BANDS if score >= lo)


def band_label(key: str | None) -> str:
    return {"confirmed": tr("confirmed"), "probable": tr("probable"), "hypothesis": tr("hypothesis"),
            "unsupported": tr("unsupported"), None: "—"}[key]


def score_text(score: int | None) -> str:
    return "—" if score is None else f"{score} ({band_label(band(score))})"


def classify(s: dict) -> str:
    """original / derivative / authored: the `classification` of the source, or the default from type and quality."""
    if s.get("classification") in SOURCE_CLASSES:
        return s["classification"]
    t, q = s.get("type"), s.get("quality")
    if t in NARRATIVE_TYPES or q == "oral":
        return "authored"
    if t == "index" or q in ("index", "transcription", "derivative"):
        return "derivative"
    if q in ("original", "image") or (q is None and s.get("file")):
        return "original"
    return "derivative"           # quality unknown: assume a copy was seen, not the record


def narrative(s: dict) -> bool:
    """A family account, someone's tree or a publication: a narrative that may tell the parents of a person."""
    return s.get("type") in NARRATIVE_TYPES or s.get("quality") == "oral"


def _latin(text: str) -> str:
    return fold(str(text).lower().translate(_CYRILLIC))


def _ids(value) -> list[str]:
    return [x for x in (value if isinstance(value, list) else [value] if value else []) if isinstance(x, str)]


def _informant(text: str) -> str:
    """The informant's name: the text before the first parenthesis, comma or dash."""
    return _latin(re.split(r"[(,;—–]| - ", str(text), maxsplit=1)[0]).strip()


# ---- which sources are one record

class RecordGroups:
    """Sources that are one record count once: marked with `same_record_as` / `derived_from`, the same local copy,
    the same parish (or repository), year and act cited for the same event, a derivative whose notes or
    transcription name the other source's ID, and family accounts of one informant."""

    def __init__(self, tree: Tree, cited_on: dict[str, set[str]]):
        self.parent = {sid: sid for sid in tree.sources}
        self.why: dict[frozenset, str] = {}
        sources = tree.sources
        for sid, s in sources.items():
            for other in _ids(s.get("same_record_as")) + _ids(s.get("derived_from")):
                if other in sources:
                    self.join(sid, other, tr("marked as the same record"))
        files: dict[str, str] = {}
        for sid in sources:
            for path in tree.source_files(sid):
                if path in files:
                    self.join(sid, files[path], tr("the same local copy"))
                files.setdefault(path, sid)
        acts: dict[tuple, list[str]] = defaultdict(list)
        for sid, s in sources.items():
            where = s.get("parish") or s.get("repository")
            if where and s.get("year") and str(s.get("act") or "").strip():
                acts[(str(where), str(s["year"]), str(s["act"]).strip().lower())].append(sid)
        for group in acts.values():
            for i, a in enumerate(group):
                for b in group[i + 1:]:
                    if cited_on.get(a, set()) & cited_on.get(b, set()):
                        self.join(a, b, tr("the same parish, year and act, cited for the same event"))
        for sid, s in sources.items():
            if classify(s) == "derivative":
                text = " ".join(str(s.get(k) or "") for k in ("notes", "transcription"))
                for other in _SOURCE_ID.findall(text):
                    if other in sources and other != sid:
                        self.join(sid, other, tr("the entry refers to {source}", source=other))
        informants: dict[str, str] = {}
        for sid, s in sources.items():
            if s.get("type") == "oral" and s.get("informant") and (key := _informant(s["informant"])):
                if key in informants:
                    self.join(sid, informants[key], tr("the same informant"))
                informants.setdefault(key, sid)

    def find(self, sid: str) -> str:
        while self.parent[sid] != sid:
            self.parent[sid] = self.parent[self.parent[sid]]
            sid = self.parent[sid]
        return sid

    def join(self, a: str, b: str, why: str) -> None:
        self.why.setdefault(frozenset((a, b)), why)
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)

    def reason(self, a: str, b: str) -> str:
        return self.why.get(frozenset((a, b)), tr("the same record"))


# ---- scores

@dataclass
class Line:
    """One line of "why this score": points (None for a cap or an override) and the text."""
    pts: int | None
    text: str


@dataclass
class Item:
    """The evidence of one cited source for one question."""
    sid: str
    role: str
    cls: str
    info: str
    ev: str
    strength: int
    lines: list[Line]
    desc: str
    names: list[str] | None = None      # the parents' names found in the transcription (None: no transcription)


@dataclass
class Score:
    kind: str                            # link | birth | death | marriage
    value: int
    lines: list[Line]
    tips: list[str] = field(default_factory=list)
    computed: int | None = None          # before an override
    items: list[Item] = field(default_factory=list)   # one per independent record, the anchor first

    @property
    def band(self) -> str:
        return band(self.value)

    def json(self) -> dict:
        return {"s": self.value, "w": [[ln.pts, ln.text] for ln in self.lines], "t": self.tips}


class Confidence:
    def __init__(self, tree: Tree):
        self.tree = tree
        self.cited_on = self._citations()
        self.groups = RecordGroups(tree, self.cited_on)
        self.links: dict[tuple[str, str], Score] = {}
        self.facts: dict[str, dict[str, Score]] = {}
        self.marriages: dict[str, Score] = {}
        self.union: dict[str, int] = {}
        self.node_cap: dict[str, int] = {}
        # weights of the steps of a path: the link score, or for a living child (a living spouse) the manual cap only
        self.step: dict[tuple[str, str], int] = {}
        self.union_step: dict[str, int] = {}
        for pid, p in tree.persons.items():
            if (label := p.get("confidence")) in MANUAL_CAP and not self._override(p, "link"):
                self.node_cap[pid] = MANUAL_CAP[label]
            self.facts[pid] = {k: s for k in ("birth", "death") if (s := self._fact(pid, k))}
        for fid, f in tree.families.items():
            for c in f.get("children") or []:
                if c in tree.persons:
                    self.links[(c, fid)] = self._link(c, fid)
            if m := self._marriage(fid):
                self.marriages[fid] = m
            evidence = [self.links[(c, fid)].value for c in f.get("children") or [] if (c, fid) in self.links]
            evidence += [m.value] if m else []
            self.union[fid] = max(evidence, default=0)
            family_cap = MANUAL_CAP.get(f.get("confidence"), 100)
            for c in f.get("children") or []:
                if (c, fid) in self.links:
                    s = self.links[(c, fid)]
                    living = tree.living(c) and not self._override(tree.persons[c], "link")
                    self.step[(c, fid)] = family_cap if living else s.value
                    if living:
                        s.lines.append(Line(None, tr("living person: the link rests on the family's own knowledge and "
                                                     "does not lower the path (only a manual label caps it)")))
            spouses = [x for x in (f.get("husband"), f.get("wife")) if x in tree.persons]
            living = any(tree.living(x) for x in spouses) and not self._override(f, "marriage", "marriage")
            self.union_step[fid] = family_cap if living else self.union[fid]

    # ---- reading the data

    def _citations(self) -> dict[str, set[str]]:
        out: dict[str, set[str]] = defaultdict(set)
        t = self.tree
        for pid, p in t.persons.items():
            for key in LIFE_EVENTS:
                for s in t.ev(p, key).get("sources") or []:
                    out[s].add(f"{pid}.{key}")
            for i, e in enumerate(p.get("events") or []):
                for s in (e.get("sources") or []) if isinstance(e, dict) else []:
                    out[s].add(f"{pid}.events[{i}]")
            for s in _ids((p.get("parentage") or {}).get("sources") if isinstance(p.get("parentage"), dict) else None):
                out[s].add(f"{pid}.parentage")
        for fid, f in t.families.items():
            for key in ("marriage", "divorce"):
                for s in t.ev(f, key).get("sources") or []:
                    out[s].add(f"{fid}.{key}")
        return out

    def _cited(self, rec: dict, key: str) -> list[str]:
        return [s for s in self.tree.ev(rec, key).get("sources") or [] if s in self.tree.sources]

    def link(self, pid: str) -> Score | None:
        """The link of a person to the first family that lists them as a child (the one that defines the line)."""
        fids = self.tree.child_of.get(pid)
        return self.links.get((pid, fids[0])) if fids else None

    @staticmethod
    def _override(rec: dict, about: str, default: str = "link") -> dict | None:
        value = rec.get("confidence_override")
        for o in value if isinstance(value, list) else [value] if value else []:
            if isinstance(o, dict) and isinstance(o.get("score"), int) and (o.get("about") or default) == about:
                return o
        return None

    def _stems(self, pid: str) -> set[str]:
        p = self.tree.persons[pid]
        names = [(p.get("given") or "").split()[:1]] + [str(v).split()[:1] for v in p.get("variants") or []]
        out = set()
        for parts in names:
            if parts and len(word := _latin(parts[0])) >= 3:
                out.add(word[:4] if len(word) >= 5 else word)
        return out

    def _parents_named(self, s: dict, parents: list[str]) -> list[str] | None:
        """Given names of the parents found in the transcription; None when there is no transcription."""
        text = s.get("transcription")
        if not text:
            return None
        hay = _latin(text)
        return [self.tree.persons[x].get("given") or "?" for x in parents
                if any(re.search(r"\b" + re.escape(st), hay) for st in self._stems(x))]

    # ---- one citation

    def _item(self, sid: str, question: str, role: str, parents: list[str] = ()) -> Item:
        s = self.tree.sources[sid]
        typ, cls = s.get("type"), classify(s)
        names = None
        if question == "link":
            if role != "parents-marriage":
                names = self._parents_named(s, list(parents))
            if role == "own-birth":
                info, ev = (("primary", "direct") if typ in BIRTH_TYPES else ("secondary", "direct") if typ in STATING_TYPES
                            else ("secondary", "direct" if names else "indirect"))
            elif role == "parents-marriage":
                info, ev = ("primary" if typ in MARRIAGE_TYPES else "secondary"), "indirect"
            elif role == "account":
                info, ev = "secondary", "direct"
            elif role == "parentage":              # cited for the parentage on purpose: it states the parents
                info, ev = ("primary" if typ in BIRTH_TYPES else "secondary"), "direct"
            else:
                info, ev = "secondary", ("direct" if names else "indirect")
        elif role == "age":
            info, ev = "secondary", "indirect"
        else:
            info = "primary" if typ in PRIMARY_FOR[question] else "secondary"
            ev = "direct" if typ in PRIMARY_FOR[question] | STATING_TYPES else "indirect"
        info = s["information"] if s.get("information") in INFORMATION else info
        ev = s["evidence"] if s.get("evidence") in EVIDENCE else ev
        base = TYPE_BASE[typ] if typ in TYPE_BASE and "classification" not in s else CLASS_BASE[cls]
        pts = round(base * INFO_FACTOR[info] * EVIDENCE_FACTOR[ev])
        desc = tr("{evidence}: {type} {source} ({classification}, {information})",
                  evidence=tr("direct evidence") if ev == "direct" else tr("indirect evidence"), type=type_label(typ),
                  source=sid, classification=class_label(cls),
                  information=tr("primary information") if info == "primary" else tr("secondary information"))
        where = {"own-death": tr("from the person's death"), "own-marriage": tr("from the person's marriage"),
                 "parents-marriage": tr("from the parents' marriage"), "age": tr("from the age in the record"),
                 "account": tr("cited on an event of the person"),
                 "parentage": tr("cited as evidence of the parentage")}.get(role)
        if where:
            desc += " — " + where
        if names:
            desc += "; " + tr("names the parents: {names}", names=", ".join(names))
        elif names == [] and parents:
            desc += "; " + tr("the transcription does not name the parents")
        lines = [Line(pts, desc)]
        if FILE_POINTS[cls] and self.tree.source_files(sid):
            lines.append(Line(FILE_POINTS[cls], tr("local copy of {source}", source=sid)))
        if s.get("transcription"):
            lines.append(Line(TRANSCRIPTION_POINTS, tr("transcription of {source}", source=sid)))
        return Item(sid, role, cls, info, ev, sum(ln.pts for ln in lines), lines, desc, names)

    # ---- combining the evidence

    def _combine(self, kind: str, items: list[Item], extra: list[Line], unresolved: bool,
                 caps: list[tuple[int, str]], override: dict | None) -> Score:
        lines: list[Line] = []
        by_group: dict[str, list[Item]] = defaultdict(list)
        for it in items:
            by_group[self.groups.find(it.sid)].append(it)
        reps, dups = [], []
        for its in by_group.values():
            its.sort(key=lambda i: (-i.strength, i.sid))
            reps.append(its[0])
            seen = {its[0].sid}
            for other in its[1:]:
                if other.sid not in seen:
                    seen.add(other.sid)
                    dups.append(Line(0, tr("{source} is the same record as {other} ({why}): counted once", source=other.sid,
                                           other=its[0].sid, why=self.groups.reason(other.sid, its[0].sid))))
        reps.sort(key=lambda i: (-i.strength, i.sid))
        total = 0
        if reps:
            total = reps[0].strength
            lines += reps[0].lines
        else:
            lines.append(Line(0, tr("no source cited")))
        corr = 0
        for share, it in zip(CORROBORATION, reps[1:]):
            pts = min(round(it.strength * share), CORROBORATION_CAP - corr)
            if pts <= 0:
                break
            corr += pts
            lines.append(Line(pts, tr("independent corroboration: {evidence}", evidence=it.desc)))
        if len(reps) > len(CORROBORATION) + 1:
            lines.append(Line(0, tr("more independent records: {sources}",
                                    sources=", ".join(i.sid for i in reps[len(CORROBORATION) + 1:]))))
        lines += dups + extra
        total = max(0, min(100, total + corr + sum(ln.pts for ln in extra)))
        if total >= 85:
            a = reps[0] if reps else None
            reason = ""
            if not a or (a.cls, a.info, a.ev) != ("original", "primary", "direct"):
                reason = tr("confirmed needs direct evidence from an original source with primary information")
            elif not any(i.ev == "direct" and i.cls != "authored" for i in reps[1:]):
                reason = tr("confirmed needs a second independent record with direct evidence")
            elif unresolved:
                reason = tr("confirmed needs every conflict resolved")
            if reason:
                caps = [(GATE_CAP, reason)] + caps
        for cap, reason in sorted(caps):
            if total > cap:
                total = cap
                lines.append(Line(None, tr("at most {cap}: {reason}", cap=cap, reason=reason)))
        score = Score(kind, total, lines, items=reps)
        if override:
            score.computed, score.value = total, override["score"]
            lines.append(Line(None, tr("set to {score} by confidence_override: {reason}", score=override["score"],
                                       reason=str(override.get("reason") or "").strip())))
        return score

    def _conflict_lines(self, rec: dict, aspects: set[str], rid: str) -> tuple[list[Line], bool]:
        """Explicit conflicts and chronology warnings of a record that touch one of `aspects`; True if unresolved."""
        lines, unresolved, explained = [], False, False
        for c in rec.get("conflicts") or []:
            if not isinstance(c, dict) or (c.get("about") and c["about"] not in aspects):
                continue
            note = str(c.get("note") or "").strip()
            if c.get("resolved") is True:
                lines.append(Line(RESOLVED, tr("resolved conflict: {note}", note=note)))
                explained = True
            else:
                lines.append(Line(UNRESOLVED, tr("unresolved conflict: {note}", note=note)))
                unresolved = True
        for fact, text in self.tree.chronology.get(rid, []):
            if fact in aspects:
                if explained:
                    lines.append(Line(0, tr("chronology warning, explained by a resolved conflict: {warning}", warning=text)))
                else:
                    lines.append(Line(CHRONOLOGY, tr("chronology warning: {warning}", warning=text)))
                    unresolved = True
        return lines, unresolved

    # ---- the link of a child to the parents (with the identity of the child)

    def _link(self, pid: str, fid: str) -> Score:
        t = self.tree
        p, f = t.persons[pid], t.families[fid]
        parents = [x for x in (f.get("husband"), f.get("wife")) if x in t.persons]
        items = [self._item(sid, "link", "own-birth", parents) for key in ("birth", "baptism") for sid in self._cited(p, key)]
        items += [self._item(sid, "link", "own-death", parents) for key in ("death", "burial") for sid in self._cited(p, key)
                  if t.sources[sid].get("type") in DEATH_TYPES]
        items += [self._item(sid, "link", "own-marriage", parents) for g in t.spouse_in.get(pid, [])
                  for sid in self._cited(t.families[g], "marriage") if t.sources[sid].get("type") in MARRIAGE_TYPES]
        items += [self._item(sid, "link", "parents-marriage", parents) for sid in self._cited(f, "marriage")]
        # a family account (or another narrative) cited on one of the person's extra events usually tells the parents;
        # records cited on residence or occupation events do not count for the link
        items += [self._item(sid, "link", "account", parents) for e in p.get("events") or [] if isinstance(e, dict)
                  for sid in e.get("sources") or [] if sid in t.sources and narrative(t.sources[sid])]
        parentage = p.get("parentage") if isinstance(p.get("parentage"), dict) else {}
        items += [self._item(sid, "link", "parentage", parents) for sid in _ids(parentage.get("sources")) if sid in t.sources]
        extra: list[Line] = []
        named = sorted({i.sid for i in items if i.names})
        if named:
            extra.append(Line(PARENTS_NAMED, tr("identity: {sources} name the parents", sources=", ".join(named))))
        if agree := self._ages_agree(pid):
            extra.append(Line(AGES_AGREE, tr("identity: the ages in {sources} agree with the year of birth", sources=agree)))
        if where := self._same_parish(pid, fid):
            extra.append(Line(SAME_PARISH, where))
        identity = p.get("identity") if isinstance(p.get("identity"), dict) else {}
        unresolved = False
        if identity.get("namesakes") == "excluded":
            extra.append(Line(NAMESAKES_POINTS["excluded"], tr("identity: namesakes checked and excluded")
                              + (f" ({identity['note']})" if identity.get("note") else "")))
        elif identity.get("namesakes") == "possible":
            extra.append(Line(NAMESAKES_POINTS["possible"], tr("identity: a namesake could be the person")
                              + (f" ({identity['note']})" if identity.get("note") else "")))
            unresolved = True
        if (w := t.birth_window(pid)) and w.conflict:
            extra.append(Line(CONTRADICTION, tr("identity: the evidence about the year of birth is contradictory")))
            unresolved = True
        lines, unres = self._conflict_lines(p, {"link", "identity"}, pid)
        fam_lines, fam_unres = self._conflict_lines(f, {"link"}, fid)
        extra += lines + fam_lines
        caps = []
        if (label := p.get("confidence")) in MANUAL_CAP:
            caps.append((MANUAL_CAP[label], tr("manual confidence \"{label}\" of the person", label=band_label(label))))
        if (label := f.get("confidence")) in MANUAL_CAP:
            caps.append((MANUAL_CAP[label], tr("manual confidence \"{label}\" of the family {family}", label=band_label(label),
                                                family=fid)))
        score = self._combine("link", items, extra, unresolved or unres or fam_unres, caps, self._override(p, "link"))
        score.tips = self._link_tips(pid, fid, score, unresolved or unres or fam_unres, caps)
        return score

    def _ages_agree(self, pid: str) -> str:
        """Sources whose ages agree (±1 year) with a cited, precise year of birth; "" if none or any disagrees."""
        t, p = self.tree, self.tree.persons[pid]
        birth = next((t.date(p, k) for k in ("birth", "baptism") if t.date(p, k) and t.has_sources(p, k)), None)
        if not birth or not birth.precise or birth.kind != "exact":
            return ""
        checks = []
        d, age = t.date(p, "death"), t.ev(p, "death").get("age")
        if d and d.precise and isinstance(age, int) and self._cited(p, "death"):
            checks.append((d.year - age, self._cited(p, "death")))
        for g in t.spouse_in.get(pid, []):
            fam = t.families[g]
            md, age = t.date(fam, "marriage"), t.ev(fam, "marriage").get("husband_age" if fam.get("husband") == pid else "wife_age")
            if md and md.precise and isinstance(age, int) and self._cited(fam, "marriage"):
                checks.append((md.year - age, self._cited(fam, "marriage")))
        if not checks or any(abs(year - birth.year) > 1 for year, _ in checks):
            return ""
        return ", ".join(sorted({s for _, srcs in checks for s in srcs}))

    def _same_parish(self, pid: str, fid: str) -> str:
        t = self.tree
        p, f = t.persons[pid], t.families[fid]
        par = lambda plid: (t.parish_of(plid) or {}).get("id")   # noqa: E731
        own = par(t.ev(p, "birth").get("place") or t.ev(p, "baptism").get("place"))
        if not own:
            return ""
        if par(t.ev(f, "marriage").get("place")) == own:
            return tr("identity: born in the parish where the parents married")
        for c in f.get("children") or []:
            k = t.persons.get(c)
            if c != pid and k and par(t.ev(k, "birth").get("place") or t.ev(k, "baptism").get("place")) == own:
                return tr("identity: born in the parish where the siblings were born")
        return ""

    # ---- facts

    def _fact(self, pid: str, kind: str) -> Score | None:
        t, p = self.tree, self.tree.persons[pid]
        keys = ("birth", "baptism") if kind == "birth" else ("death", "burial")
        if not any(t.ev(p, k) for k in keys):
            return None
        items = [self._item(sid, kind, k) for k in keys for sid in self._cited(p, k)]
        if kind == "birth":            # ages in other records: indirect evidence for the year of birth
            if isinstance(t.ev(p, "death").get("age"), int):
                items += [self._item(sid, "birth", "age") for sid in self._cited(p, "death")]
            for g in t.spouse_in.get(pid, []):
                fam = t.families[g]
                if isinstance(t.ev(fam, "marriage").get("husband_age" if fam.get("husband") == pid else "wife_age"), int):
                    items += [self._item(sid, "birth", "age") for sid in self._cited(fam, "marriage")]
        extra, unresolved = self._conflict_lines(p, {kind}, pid)
        if kind == "birth" and (w := t.birth_window(pid)) and w.conflict:
            extra.append(Line(CONTRADICTION, tr("the evidence about the year of birth is contradictory")))
            unresolved = True
        caps = [(MANUAL_CAP[c], tr("the event is marked \"{label}\"", label=band_label(c)))
                for k in keys if (c := t.ev(p, k).get("confidence")) in MANUAL_CAP]
        score = self._combine(kind, items, extra, unresolved, caps, self._override(p, kind))
        score.tips = self._fact_tips(pid, kind, score, unresolved, caps)
        return score

    def _marriage(self, fid: str) -> Score | None:
        t, f = self.tree, self.tree.families[fid]
        if not t.ev(f, "marriage"):
            return None
        items = [self._item(sid, "marriage", "own") for sid in self._cited(f, "marriage")]
        extra, unresolved = self._conflict_lines(f, {"marriage"}, fid)
        caps = []
        if (c := t.ev(f, "marriage").get("confidence")) in MANUAL_CAP:
            caps.append((MANUAL_CAP[c], tr("the event is marked \"{label}\"", label=band_label(c))))
        if (c := f.get("confidence")) in MANUAL_CAP:
            caps.append((MANUAL_CAP[c], tr("manual confidence \"{label}\" of the family {family}", label=band_label(c), family=fid)))
        score = self._combine("marriage", items, extra, unresolved, caps, self._override(f, "marriage", "marriage"))
        score.tips = self._fact_tips(fid, "marriage", score, unresolved, caps)
        return score

    # ---- what would strengthen a score

    def _birth_search(self, pid: str) -> tuple[str, str]:
        t = self.tree
        places = t.search_places(pid, "birth")
        w = t.birth_window(pid)
        rng = search_range(w.lo, w.hi) if w else None
        return (t.parish_desc(places[0][0]) if places else tr("parish unknown"),
                f"{rng[0]}–{rng[1]}" if rng else tr("years unknown"))

    def _common_tips(self, score: Score, unresolved: bool, caps: list[tuple[int, str]]) -> list[str]:
        tips = []
        a = score.items[0] if score.items else None
        if a and a.cls == "derivative" and (self.tree.sources[a.sid].get("type") == "index"
                                             or self.tree.sources[a.sid].get("quality") == "index"):
            tips.append(tr("View the scan of the record behind the index entry {source} and cite it as a source of its "
                           "own (quality: image).", source=a.sid))
        for it in score.items:
            if it.cls == "original" and not self.tree.source_files(it.sid):
                tips.append(tr("Save a local copy of {source} (`file`).", source=it.sid))
                break
        if unresolved:
            tips.append(tr("Resolve the conflict or the chronology warning and record the reasoning "
                           "(`conflicts`: `resolved: true`, the reasoning in `note`)."))
        for cap, reason in caps:
            if any(ln.pts is None and ln.text == tr("at most {cap}: {reason}", cap=cap, reason=reason) for ln in score.lines):
                tips.append(tr("The score is capped at {cap} ({reason}): change the label once the evidence supports more.",
                               cap=cap, reason=reason))
        return tips

    def _link_tips(self, pid: str, fid: str, score: Score, unresolved: bool, caps) -> list[str]:
        t, p = self.tree, self.tree.persons[pid]
        name = t.name(pid)
        tips = []
        if t.living(pid):
            tips.append(tr("A full copy of the civil birth certificate (USC) names the parents; living persons are never "
                           "searched online."))
        elif not any(i.role == "own-birth" and t.sources[i.sid].get("type") in BIRTH_TYPES for i in score.items):
            where, years = self._birth_search(pid)
            tips.append(tr("Find the birth or baptism record of {name}: {where}, {years}.", name=name, where=where, years=years))
        tips += self._common_tips(score, unresolved, caps)
        for it in score.items:
            if it.names is None and it.role != "parents-marriage" and self.tree.sources[it.sid].get("type") not in NARRATIVE_TYPES:
                tips.append(tr("Transcribe {source} (`transcription`): it shows whether the record names the parents.",
                               source=it.sid))
                break
        if not any(i.ev == "direct" and i.cls != "authored" for i in score.items[1:]) and not t.living(pid):
            own_marriages = [g for g in t.spouse_in.get(pid, []) if t.ev(t.families[g], "marriage")]
            if own_marriages and not any(i.role == "own-marriage" for i in score.items):
                tips.append(tr("A second independent record: the marriage record of {name} (it usually names the parents).",
                               name=name))
            elif not any(i.role == "own-death" for i in score.items):
                tips.append(tr("A second independent record: the death record of {name} (it often names the parents).",
                               name=name))
            else:
                tips.append(tr("A second independent record that names the parents: a census, a population register "
                               "or the civil copy of a record of {name}.", name=name))
        identity = p.get("identity") if isinstance(p.get("identity"), dict) else {}
        a = score.items[0] if score.items else None
        if not identity.get("namesakes") and not t.living(pid) and a and (a.cls, a.info) != ("original", "primary"):
            where, years = self._birth_search(pid)
            birth_name = " ".join(x for x in ((p.get("given") or "").split()[:1] + [p.get("surname") or ""]) if x) or name
            tips.append(tr("Check namesakes: other persons named {name} in {where}, {years}; record the result in "
                           "`identity`.", name=birth_name, where=where, years=years))
        return tips[:5]

    def _fact_tips(self, rid: str, kind: str, score: Score, unresolved: bool, caps) -> list[str]:
        t = self.tree
        tips = []
        if kind == "marriage":
            f = t.families[rid]
            couple = f"{t.name(f.get('husband'))} ⚭ {t.name(f.get('wife'))}"
            if any(t.living(x) for x in (f.get("husband"), f.get("wife")) if x):
                return []
            if not any(t.sources[i.sid].get("type") in MARRIAGE_TYPES for i in score.items):
                plid = t.ev(f, "marriage").get("place")
                md = t.date(f, "marriage")
                rng = search_range(*md.bounds) if md else None
                tips.append(tr("Find the marriage record of {name}: {where}, {years}.", name=couple,
                               where=t.parish_desc(plid) if plid in t.places else tr("usually the bride's parish"),
                               years=f"{rng[0]}–{rng[1]}" if rng else tr("years unknown")))
            tips += self._common_tips(score, unresolved, caps)
            if len(score.items) < 2:
                tips.append(tr("A second independent record of the marriage: the civil copy (duplicate) of the parish "
                               "book, or the banns."))
            return tips[:4]
        name = t.name(rid)
        if t.living(rid):
            return []
        if kind == "birth":
            if not any(i.role in ("birth", "baptism") and t.sources[i.sid].get("type") in BIRTH_TYPES for i in score.items):
                where, years = self._birth_search(rid)
                tips.append(tr("Find the birth or baptism record of {name}: {where}, {years}.", name=name, where=where,
                               years=years))
        elif not any(t.sources[i.sid].get("type") in DEATH_TYPES | {"gravestone"} for i in score.items):
            places = t.search_places(rid, "death")
            d = t.date(t.persons[rid], "death") or t.date(t.persons[rid], "burial")
            rng = search_range(*d.bounds) if d else t.death_range(rid)
            tips.append(tr("Find the death or burial record of {name}: {where}, {years}.", name=name,
                           where=t.parish_desc(places[0][0]) if places else tr("parish unknown"),
                           years=f"{rng[0]}–{rng[1]}" if rng else tr("years unknown")))
        tips += self._common_tips(score, unresolved, caps)
        if len(score.items) < 2:
            tips.append(tr("A second independent record of the birth: the age in the death or marriage record, or the civil "
                           "copy next to the parish book.") if kind == "birth"
                        else tr("A second independent record of the death: the burial record, the civil copy or the "
                                "gravestone."))
        return tips[:4]

    # ---- paths from the proband

    def paths(self, proband: str | None, mode: str = "all") -> dict[str, int]:
        """The weakest link on the best path from the proband to each person reached (maximin). mode "anc": only
        upwards, through the first family of each child (the line of ancestors); "all": through children, parents and
        spouses (a spouse through the union score of the family)."""
        t = self.tree
        if proband not in t.persons:
            return {}
        adj: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for fid, f in t.families.items():
            ps = [x for x in (f.get("husband"), f.get("wife")) if x in t.persons]
            for c in f.get("children") or []:
                if (c, fid) not in self.links or (mode == "anc" and t.child_of[c][0] != fid):
                    continue
                w = self.step[(c, fid)]
                for x in ps:
                    adj[c].append((x, w))
                    if mode != "anc":
                        adj[x].append((c, w))
            if mode != "anc" and len(ps) == 2:
                adj[ps[0]].append((ps[1], self.union_step[fid]))
                adj[ps[1]].append((ps[0], self.union_step[fid]))
        best, heap = {proband: 100}, [(-100, proband)]
        while heap:
            s, u = heapq.heappop(heap)
            if -s < best[u]:
                continue
            for v, w in adj[u]:
                cand = min(-s, w, self.node_cap.get(v, 100))
                if cand > best.get(v, -1):
                    best[v] = cand
                    heapq.heappush(heap, (-cand, v))
        return best

    def summary(self) -> dict:
        """Counts for `build.py --json`: bands of the links, the facts and the ancestors' paths, the weakest links."""
        t = self.tree
        pb = t.project.get("proband")
        anc = self.paths(pb, "anc") if pb in t.persons else {}
        full = self.paths(pb, "all") if pb in t.persons else {}
        count = lambda values: {key: sum(1 for v in values if band(v) == key) for key, _ in BANDS}   # noqa: E731
        weakest = [{"id": pid, "kekule": t.kekule.get(pid, []), "link": s.value, "band": s.band, "path": anc.get(pid),
                    "tip": s.tips[0] if s.tips else ""} for pid, s in self.weakest_links()[:15]]
        persons = {}
        for pid in t.persons:
            rec = {"link": self.link(pid).value if self.link(pid) else None, "path": full.get(pid)}
            rec.update({k: s.value for k, s in self.facts[pid].items()})
            persons[pid] = rec
        return {
            "thresholds": {key: lo for key, lo in BANDS},
            "links": count([s.value for s in self.links.values()]),
            "facts": count([s.value for fs in self.facts.values() for s in fs.values()] + [s.value for s in self.marriages.values()]),
            "ancestors_by_path": count([v for k, v in anc.items() if k != pb]),
            "weakest_links": weakest, "persons": persons,
            "families": {fid: {"marriage": self.marriages[fid].value if fid in self.marriages else None, "union": self.union[fid]}
                         for fid in t.families},
        }

    def weakest_links(self) -> list[tuple[str, Score]]:
        """Links of the proband's ancestors, the weakest step of the paths first (links of living persons, which do
        not lower the path, last); among equal scores the one more ancestors hang on."""
        t = self.tree
        out = [(pid, s) for pid in t.kekule if (s := self.link(pid))]
        return sorted(out, key=lambda x: (self.step[(x[0], t.child_of[x[0]][0])], x[1].value,
                                          -len(self.ancestors_above(x[0])), min(t.kekule[x[0]])))

    def ancestors_above(self, pid: str) -> set[str]:
        seen, stack = set(), list(self.tree.parents(pid))
        while stack:
            a = stack.pop()
            if a not in seen:
                seen.add(a)
                stack.extend(self.tree.parents(a))
        return seen


_cache: "weakref.WeakKeyDictionary[Tree, Confidence]" = weakref.WeakKeyDictionary()


def scores(tree: Tree) -> Confidence:
    """The confidence of a tree, computed once."""
    if tree not in _cache:
        _cache[tree] = Confidence(tree)
    return _cache[tree]


def type_label(kind: str | None) -> str:
    return {"birth_record": tr("birth record"), "baptism_record": tr("baptism record"), "marriage_record": tr("marriage record"),
            "death_record": tr("death record"), "burial_record": tr("burial record"), "civil_record": tr("civil register record"),
            "index": tr("index entry"), "census": tr("census"), "population_register": tr("population register"),
            "family_document": tr("family document"), "photo": tr("photo"), "gravestone": tr("gravestone"),
            "oral": tr("family account"), "online_tree": tr("online tree"), "publication": tr("publication")
            }.get(kind or "", tr("source"))


def class_label(cls: str) -> str:
    return {"original": tr("original source"), "derivative": tr("derivative source"), "authored": tr("authored source")}[cls]


def bands_json() -> list[list]:
    """The named thresholds for the page: [[key, lowest score, label], …], the highest first."""
    return [[key, lo, band_label(key)] for key, lo in BANDS]


# ---- the report

def _why(score: Score, indent: str = "  ") -> list[str]:
    out = []
    for ln in score.lines:
        pts = "" if ln.pts is None else f"{ln.pts:+d} " if ln.pts else "±0 "
        out.append(f"{indent}- {pts}{ln.text}")
    return out


def write_confidence(tree: Tree, path: Path) -> None:
    cf = scores(tree)
    t = tree
    pb = t.project.get("proband")
    anc = cf.paths(pb, "anc") if pb in t.persons else {}
    L = [tr("# Confidence of the tree"), "",
         tr("_Generated {date} by `scripts/build.py` — do not edit by hand._", date=TODAY.isoformat()), "",
         tr("Scores 0–100 computed from the evidence (docs/confidence.md): **confirmed** ≥ 85 · **probable** 60–84 · "
            "**hypothesis** 30–59 · **unsupported** < 30. The *link* of a person is the evidence that they are the child "
            "of their parents and the person in the records; the *path* is the weakest link between the proband and "
            "the person. A manual `confidence` caps a score; `confidence_override` replaces it."), "",
         tr("**Exception to the weakest link:** the link of a living person (and the union of a couple with a living "
            "spouse) keeps its own score but does not lower the path — the family knows it first-hand and the records "
            "are not public; only a manual label caps it."), "",
         tr("## Summary"), ""]
    bands = [key for key, _ in BANDS]

    def counts(values) -> str:
        return " · ".join(f"{band_label(k)}: {sum(1 for v in values if band(v) == k)}" for k in bands)

    L.append(tr("- links parent–child: {n} ({counts})", n=len(cf.links), counts=counts([s.value for s in cf.links.values()])))
    facts = [s.value for fs in cf.facts.values() for s in fs.values()] + [s.value for s in cf.marriages.values()]
    L.append(tr("- facts (birth, death, marriage): {n} ({counts})", n=len(facts), counts=counts(facts)))
    if anc:
        L.append(tr("- ancestors of the proband by path: {n} ({counts})", n=len(anc) - 1,
                    counts=counts([v for k, v in anc.items() if k != pb])))
    L += ["", tr("## Ancestors per generation (path from the proband)"), ""]
    if not anc:
        L.append(tr("_Set `proband` in data/project.yaml to determine the line of ancestors._"))
    else:
        L += ["| " + " | ".join([tr("Gen."), tr("Ancestors")] + [band_label(k) for k in bands]) + " |",
              "|" + "---|" * (2 + len(bands))]
        gens: dict[int, list[int]] = defaultdict(list)
        for pid, nums in t.kekule.items():
            if pid != pb:
                gens[min(nums).bit_length()].append(anc.get(pid, 0))
        for g in sorted(gens):
            vals = gens[g]
            L.append(f"| {g} | {len(vals)}/{2 ** (g - 1)} | " + " | ".join(str(sum(1 for v in vals if band(v) == k)) for k in bands) + " |")
    L += ["", tr("## Weakest links on the line of ancestors"), "",
          tr("_The lowest-scored links first; a weak link lowers the path of every ancestor above it._"), ""]
    weakest = [(pid, s) for pid, s in cf.weakest_links() if s.value < 85][:25]
    for pid, s in weakest:
        life = "; ".join(t.life_lines(t.persons[pid]))
        L.append(f"### {', '.join(map(str, t.kekule[pid]))} · {t.name(pid)}" + (f" · {life}" if life else "") + f" · `{pid}`")
        above = max((anc[x] for x in t.parents(pid) if x in anc), default=None)
        L += ["", tr("- link to the parents: **{score}** · path from the proband to the parents: {path} · ancestors above: {n}",
                     score=score_text(s.value), path=score_text(above), n=len(cf.ancestors_above(pid))),
              tr("- why:")] + _why(s)
        if s.tips:
            L += [tr("- to strengthen:")] + [f"  - {tip}" for tip in s.tips]
        L.append("")
    if not weakest:
        L += [tr("_None._"), ""]
    L += [tr("## Facts of the ancestors below probable"), ""]
    rows = []
    for pid in sorted(t.kekule, key=lambda x: min(t.kekule[x])):
        for kind, s in cf.facts[pid].items():
            if s.value < 60:
                rows.append((pid, {"birth": tr("birth"), "death": tr("death")}[kind], s))
    for fid in t.ancestral_families():
        if (s := cf.marriages.get(fid)) and s.value < 60:
            f = t.families[fid]
            rows.append((f.get("husband") or f.get("wife"), tr("marriage"), s))
    for pid, label, s in rows:
        L.append(f"- {', '.join(map(str, t.kekule.get(pid, [])))} · {t.name(pid)} · {label}: **{score_text(s.value)}**"
                 + (f" — {s.tips[0]}" if s.tips else ""))
    if not rows:
        L.append(tr("_None._"))
    L += ["", tr("## Manual labels that disagree with the evidence"), "",
          tr("_A manual label above the computed band is not backed by the cited sources; one below it may be outdated._"), ""]
    disagree = []
    for pid, p in t.persons.items():
        if (label := p.get("confidence")) in ("confirmed", "probable", "hypothesis") and (s := cf.link(pid)):
            computed = s.computed if s.computed is not None else s.value
            if band(computed) != label:
                disagree.append(tr("- `{id}` {name}: manual \"{label}\", computed link {score}", id=pid, name=t.name(pid),
                                   label=band_label(label), score=score_text(computed)))
    L += disagree or [tr("_None._")]
    L += ["", tr("## Other persons (not ancestors)"), ""]
    others = [s.value for (c, fid), s in cf.links.items() if c not in t.kekule]
    L.append(tr("- links parent–child: {n} ({counts})", n=len(others), counts=counts(others)))
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
