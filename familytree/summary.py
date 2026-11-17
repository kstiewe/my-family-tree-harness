"""\"At a glance\": the top of a person's card — who the person was, where they lived, whom they lived with, what
is worth knowing about them and the times they lived in. Everything is computed from the data; nothing is
invented. Every item points to the sources it rests on (footnote numbers) and is marked when the data calls it
probable or a hypothesis.

`person_summary(tree, pid, public)` returns a JSON-ready dict for the page (templates/body.html draws it and saves
it as an image), or None when there is nothing to show:

    {"rows": [row, …], "quote": {"t", "by", "r"}, "refs": ["S0001", …], "conf": "probable"}
    row  = {"key": "who" | "where" | "with" | "facts" | "times", "label": "…", "sep": "→" | "·",
            "items": [item, …], "tail": [item, …], "more": [line, …]}
    item = {"t": text, "y": years, "r": [footnote numbers], "c": "probable" | "hypothesis", "pl": place, "p": person}
    line = {"k": kind, "y": when, "items": [item, …], "n": note, "r": [...], "c": ..., "num": n, "km": n}

`items` (and `tail`) make the short line that is always visible, `more` the lines shown on demand. Footnote n is
refs[n - 1]. Parts without data are left out, and so is a row without items.
"""

from __future__ import annotations

import datetime as dt
import re
import weakref
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .dates import TODAY, Date, safe_date, sort_key
from .geo import distance_km, partition_label, surname_key
from .history import lived_through
from .i18n import tr, trn
from .model import Tree, fold
from .schema import language_names, place_kind

LEAVE_KM = 50          # a stay this far from the first known place of a life counts as leaving the home area
CHILDHOOD = 15         # a child who died younger than this died in childhood
CHAIN = 5              # at most this many places or occupations in a short line (the middle ones become "…")
QUOTE_LEN = (20, 180)  # the length of a sentence that can be quoted
START, END = (-10 ** 6, 0, 0), (10 ** 6, 0, 0)

# Social strata of occupations as written in Polish, German, Latin and Russian rural records, matched at the start
# of folded words (lower case, no diacritics). The ranked strata are the rungs of the rural ladder of the 18th–19th
# century; crafts, estate staff and the retired are recognised but not ranked. The first recognised word decides.
STRATA = (
    ("retired", None, r"wycuz|wymow|dozywot|altsitz|ausgeding|auszugl|altenteil|rentner|rencist|emeryt"),
    ("servant", 1, r"parob|sluzac|dziewk|fornal|knecht|magd|dienst|famul|ancill|батрак"),
    ("landless", 2, r"komorni|robotni|wyrobni|najemni|dniowk|einlieger|instmann|inste$|einwohner|tagelohn|arbeiter|"
                    r"arbeitsmann|hausling|losmann|inquilin|laborator|operari|mercenari|работник|поденщ"),
    ("smallholder", 3, r"chalupni|zagrodni|kathner|katner|kossat|budner|hausler|gartner"),
    ("farmer", 4, r"gospodar|rolni|kmie|wlosci|polrolni|posiadacz|wlasciciel|bauer|hofbesitz|grundbesitz|besitzer|"
                  r"ackerwirt|landwirt$|wirt$|eigentum|kolonist|colon|agricol|cmeth|possessor|крестьян|земледел"),
    ("craft", None, r"murarz|ciesl|kowal|kolodziej|stolarz|szewc|krawiec|mlynarz|piekarz|rzezni|bednarz|garncarz|"
                    r"tkacz|kusnierz|slusarz|maurer|zimmer|schmied|stellmacher|tischler|schuhmach|schuster|schneider|"
                    r"muller|backer|fleischer|bottcher|topfer|weber|faber|sartor|sutor|molitor|textor"),
    ("estate", None, r"wlodarz|karbow|ekonom|stangret|furman|owczarz|pasterz|pastuch|gajow|lesnicz|vogt|hofmeister|"
                     r"kutscher|schafer|hirt|forster|jager"),
)
_STRATA = [(name, rank, re.compile(rx)) for name, rank, rx in STRATA]
_YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")


def stratum(text: str) -> tuple[str | None, int | None]:
    """The social stratum of an occupation entry and its rank on the rural ladder (None when not ranked)."""
    for word in re.findall(r"\w+", fold(text)):
        for name, rank, rx in _STRATA:
            if rx.match(word):
                return name, rank
    return None, None


# ---- ages and intervals


@dataclass
class Age:
    years: int
    exact: bool                  # from two dates known to the day, or as a record states it
    months: int | None = None
    days: int | None = None
    recorded: int | None = None  # the age in the death record, when it differs from the dates by two years or more


def _day(d: Date | None) -> dt.date | None:
    return dt.date(*d.a) if d and d.kind == "exact" and d.a[1] and d.a[2] else None


def _key(d: Date | None) -> tuple[int, int, int] | None:
    return sort_key(d.a) if d else None


def age_between(a: Date | None, b: Date | None) -> Age | None:
    """The age at date b of someone born at date a; exact when both dates are known to the day."""
    if not a or not b or not a.precise or not b.precise:
        return None
    x, y = _day(a), _day(b)
    if x and y:
        if y < x:
            return None
        months = (y.year - x.year) * 12 + y.month - x.month - (y.day < x.day)
        return Age(months // 12, True, months, (y - x).days)
    return Age(b.year - a.year, False) if b.year >= a.year else None


def number(a: Age) -> str:
    """The years of an age as a number, "c. 54" when they come from years only."""
    return str(a.years) if a.exact else tr("c. {date}", date=a.years)


def age_text(a: Age) -> str:
    """An age as a phrase: "aged 54", "aged 3 months", "aged 9 days"."""
    if a.years == 0 and a.months is not None:
        return trn("aged {n} month|aged {n} months", a.months) if a.months else trn("aged {n} day|aged {n} days", a.days or 0)
    if a.years == 0:
        return tr("under a year old")
    return trn("aged {n}", a.years, n=number(a))


def after(a: Date, b: Date) -> str | None:
    """How long after date a date b came: "5 months later", "2 years later", "the same year"."""
    x, y = _day(a), _day(b)
    if x and y:
        if y < x:
            return None
        months = (y.year - x.year) * 12 + y.month - x.month - (y.day < x.day)
        if (y - x).days < 31:
            return trn("{n} day later|{n} days later", (y - x).days)
        if months < 24:
            return trn("{n} month later|{n} months later", max(months, 1))
        return trn("{n} year later|{n} years later", months // 12)
    if not (a.precise and b.precise) or b.year < a.year:
        return None
    if b.year == a.year:
        return tr("the same year")
    return trn("about {n} year later|about {n} years later", b.year - a.year)


def sentences(text: str) -> list[str]:
    """The sentences of a transcription. Its lines are joined (transcriptions keep the lines of the original); a
    full stop after a number ("14. Oktober") or after a short abbreviation ("nr.", "ur.") does not end a sentence,
    nor does one before a lower-case word; an empty line always does."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = re.sub(r"\s+", " ", para).strip()
        start = 0
        for m in re.finditer(r"[.!?…]+(?=\s+\S)", para):
            word = (re.findall(r"\w+$", para[start:m.start()]) or [""])[0]
            nxt = para[m.end():].lstrip()[:1]
            if (word.isdigit() and len(word) <= 2) or (word.isalpha() and len(word) <= 3) or nxt.islower():
                continue
            out.append(para[start:m.end()].strip())
            start = m.end()
        out.append(para[start:].strip())
    return [s.strip(" \t-–—•*\"'„”") for s in out if s.strip()]


def plain(s: str) -> str:
    """A sentence without the transcriber's remarks in brackets: "[...]" becomes "…", a remark of more than three
    letters goes ("evangelischer [reading uncertain] Religion"), a short mark such as "[?]" stays."""
    s = re.sub(r"\[\s*(\.\.\.|…)\s*\]", "…", s)
    s = re.sub(r"\s*\[[^\]]{4,}\]", "", s)
    return re.sub(r"\s+([,.;:])", r"\1", re.sub(r"\s{2,}", " ", s)).strip()


def _sex(p: dict) -> str:
    return p.get("sex") if p.get("sex") in ("M", "F") else "U"


def _texts(value) -> list[str]:
    return [str(x) for x in value] if isinstance(value, list) else [str(value)] if value else []


# ---- places of a life


@dataclass
class Record:
    """A place in a record of a life: a birth, a residence, a marriage, a child's birth, a death."""
    key: tuple[int, int, int]    # the date, or the date it inherits when it has none
    phase: int                   # 0 birth, 1 during the life, 2 death: the order of records with the same key
    order: int
    place: str
    kind: str
    date: Date | None
    sources: list[str]
    conf: str
    value: str = ""


@dataclass
class Stay:
    """Consecutive records of one place, and the weddings held meanwhile in a parish church elsewhere."""
    place: str
    dates: list[Date] = field(default_factory=list)
    kinds: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    confs: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    venues: list[Record] = field(default_factory=list)

    def add(self, r: Record) -> None:
        if r.date:
            self.dates.append(r.date)
        self.kinds.append(r.kind)
        self.sources += [s for s in r.sources if s not in self.sources]
        self.confs.append(r.conf)
        if r.value and r.value not in self.values:
            self.values.append(r.value)

    def add_venue(self, r: Record) -> None:
        self.venues.append(r)
        self.sources += [s for s in r.sources if s not in self.sources]

    @property
    def first_year(self) -> int | None:
        return min((d.year for d in self.dates), default=None)

    @property
    def conf(self) -> str:
        """Probable (or a hypothesis) only when every record of the stay says so."""
        if self.confs and all(self.confs):
            return "hypothesis" if "hypothesis" in self.confs else "probable"
        return ""


class Context:
    """What a single summary is compared against — the ages at death and the departures along the lines of
    surnames — and the places of every life, computed once per tree."""

    def __init__(self, tree: Tree, public: bool):
        self.tree, self.public = tree, public
        self.geo = tree.geo(living=not public)
        self._stays: dict[str, list[Stay]] = {}
        self._parishes: set[str] | None = None
        t = tree
        self.ages = {pid: a for pid in t.persons if not self.hidden(pid) and (a := self.lifespan(pid))}

        self.line = {pid: surname_key(p["surname"]) for pid, p in t.persons.items() if p.get("surname")}
        members: dict[str, list[str]] = defaultdict(list)
        for pid, key in self.line.items():
            members[key].append(pid)
        self.line_name, self.line_size = {}, {key: len(pids) for key, pids in members.items()}
        for key, pids in members.items():
            men = Counter(t.persons[x]["surname"] for x in pids if t.persons[x].get("sex") == "M")
            self.line_name[key] = men.most_common(1)[0][0] if men else t.persons[pids[0]]["surname"]

        self.longest: dict[str, tuple[str, int]] = {}       # person → (line, persons of the line with a known age)
        for key, pids in members.items():
            if pid := self._oldest(pids, 3):
                self.longest[pid] = (key, sum(x in self.ages for x in pids))
        oldest = self._oldest(list(t.kekule), 5)
        self.longest_ancestor = (oldest, sum(x in self.ages for x in t.kekule)) if oldest else None

        self.leaving = {pid: lv for pid in t.persons if not self.hidden(pid) and (lv := self._leaving(pid))}
        first: dict[str, int] = {}
        for pid, lv in self.leaving.items():
            key = self.line.get(pid)
            if key and lv["year"] is not None and self.line_size[key] >= 3:
                first[key] = min(first.get(key, lv["year"]), lv["year"])
        self.first_leavers = {pid for pid, lv in self.leaving.items()
                              if lv["year"] is not None and first.get(self.line.get(pid)) == lv["year"]}

    def hidden(self, pid: str | None) -> bool:
        return bool(pid) and self.public and self.tree.living(pid)

    def _oldest(self, pids: list[str], at_least: int) -> str | None:
        """The person who lived longest of `pids`, when at least `at_least` have a known age and nobody ties."""
        rows = sorted(((self.ages[x].years, x) for x in pids if x in self.ages), reverse=True)
        return rows[0][1] if len(rows) >= at_least and rows[0][0] > rows[1][0] else None

    def lifespan(self, pid: str) -> Age | None:
        t, p = self.tree, self.tree.persons[pid]
        death = t.date(p, "death") or t.date(p, "burial")
        age = age_between(t.date(p, "birth") or t.date(p, "baptism"), death)
        recorded = next((a for k in ("death", "burial") if isinstance(a := t.ev(p, k).get("age"), int)), None)
        if age and age.exact:
            if recorded is not None and abs(recorded - age.years) >= 2:
                age.recorded = recorded
            return age
        if recorded is not None and death:
            return Age(recorded, True)
        return age

    def stays(self, pid: str) -> list[Stay]:
        """The places of a person's life in order — birth, residences, marriages, births of the children, death —
        with consecutive records of one place merged. A record without a date keeps its place in the data."""
        if pid not in self._stays:
            self._stays[pid] = self._collect_stays(pid)
        return self._stays[pid]

    def _collect_stays(self, pid: str) -> list[Stay]:
        t, p = self.tree, self.tree.persons[pid]
        records: list[Record] = []

        def add(key, phase, plid, kind, d, ev, value=""):
            if plid in t.places:
                records.append(Record(key, phase, len(records), plid, kind, d, list(ev.get("sources") or []),
                                      ev.get("confidence") or "", value))

        start = START
        for k in ("birth", "baptism"):
            if (ev := t.ev(p, k)).get("place"):
                d = safe_date(ev.get("date")) or t.date(p, "birth") or t.date(p, "baptism")
                start = _key(d) or START
                add(start, 0, ev["place"], k, d, ev)
                break
        last = start
        for e in p.get("events") or []:
            kind = e.get("type") if isinstance(e, dict) else None
            if kind in ("residence", "census", "emigration") or (kind == "occupation" and e.get("place")):
                d = safe_date(e.get("date"))
                last = _key(d) or last
                add(last, 1, e.get("place"), kind, d, e, str(e.get("value") or "") if kind == "residence" else "")
        for fid in t.spouse_in.get(pid, []):
            f = t.families[fid]
            if self.hidden(f.get("husband")) or self.hidden(f.get("wife")):
                continue
            kids = []
            for c in f.get("children") or []:
                k = t.persons[c]
                if not self.hidden(c) and (d := t.date(k, "birth") or t.date(k, "baptism")):
                    kids.append((_key(d), d, t.ev(k, "birth") if t.ev(k, "birth").get("place") else t.ev(k, "baptism")))
            md = t.date(f, "marriage")
            add(_key(md) or min((k for k, _, _ in kids), default=start), 1, t.ev(f, "marriage").get("place"),
                "marriage", md, t.ev(f, "marriage"))
            for key, d, ev in kids:
                add(key, 1, ev.get("place"), "child", d, ev)
        for k in ("death", "burial"):
            if (ev := t.ev(p, k)).get("place"):
                d = safe_date(ev.get("date")) or t.date(p, "death") or t.date(p, "burial")
                add(_key(d) or END, 2, ev["place"], k, d, ev)
                break
        # A wedding in a parish church tells where the wedding was, not where the couple lived: it is told with the
        # stay of its time (or the next one), unless the life has no other place.
        venue = lambda r: r.kind == "marriage" and self.is_parish(r.place)
        lived = any(not venue(r) for r in records)
        stays: list[Stay] = []
        waiting: list[Record] = []
        for r in sorted(records, key=lambda r: (r.key, r.phase, r.order)):
            if lived and venue(r):
                if stays and stays[-1].place != r.place:
                    stays[-1].add_venue(r)
                    continue
                if not stays:
                    waiting.append(r)
                    continue
            if not stays or stays[-1].place != r.place:
                stays.append(Stay(r.place))
                for w in waiting:
                    if w.place == r.place:
                        stays[-1].add(w)
                    else:
                        stays[-1].add_venue(w)
                waiting = []
            stays[-1].add(r)
        return stays

    def km(self, a: str, b: str) -> int | None:
        """The distance between two places; None when unknown, or when one is the parish (church) of the other —
        then the records only name the parish, not a move."""
        c = self.geo.coords
        if self.same_parish(a, b) and (self.is_parish(a) or self.is_parish(b)):
            return None
        return round(distance_km(c[a], c[b])) if a in c and b in c else None

    def same_parish(self, a: str, b: str) -> bool:
        pa, pb = self.tree.parish_of(a), self.tree.parish_of(b)
        return bool(pa and pb and pa.get("id") == pb.get("id")) or a == (pb or {}).get("id") or b == (pa or {}).get("id")

    def is_parish(self, plid: str) -> bool:
        """A parish seat: typed as a parish, with a denomination, the parish of another place, or the village of the
        same name as its parish (the village Wzorcowo in the parish Wzorcowo)."""
        if self._parishes is None:
            self._parishes = {pl["parish"] for pl in self.tree.places.values() if pl.get("parish")}
        pl = self.tree.places.get(plid) or {}
        par = self.tree.places.get(pl.get("parish") or "") or {}
        return (place_kind(pl) == "parish" or bool(pl.get("denomination")) or plid in self._parishes
                or (bool(par) and fold(par.get("name") or "") == fold(pl.get("name") or "")))

    def _leaving(self, pid: str) -> dict | None:
        """The first stay far from the first known place of a life, or an emigration: leaving the home area. Told
        as the move from the place before it."""
        stays, c = self.stays(pid), self.geo.coords
        origin = next((s for s in stays if s.place in c), None)
        before = None
        for s in stays:
            far = origin and s is not origin and s.place in c and distance_km(c[origin.place], c[s.place]) >= LEAVE_KM
            if far or "emigration" in s.kinds:
                start = before or origin
                return {"from": start.place if start else None, "to": s.place, "year": s.first_year,
                        "km": self.km(start.place, s.place) if start else None}
            if s.place in c:
                before = s
        return None


_CONTEXTS: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


def context(tree: Tree, public: bool) -> Context:
    per_tree = _CONTEXTS.setdefault(tree, {})
    if public not in per_tree:
        per_tree[public] = Context(tree, public)
    return per_tree[public]


def person_summary(tree: Tree, pid: str, public: bool = False) -> dict | None:
    """The \"At a glance\" part of a person's card (see the module docstring), or None when there is nothing to
    show — always for a living person in public mode."""
    ctx = context(tree, public)
    return None if ctx.hidden(pid) else Summary(ctx, pid).build()


# ---- the summary of one person


@dataclass
class Union:
    """A marriage seen from one spouse."""
    family: dict
    spouse: str | None
    hidden: bool                 # a spouse is living (public mode): no dates or places
    date: Date | None
    children: list[str]
    key: tuple


class Summary:
    def __init__(self, ctx: Context, pid: str):
        self.ctx, self.t, self.pid = ctx, ctx.tree, pid
        self.p = self.t.persons[pid]
        self.sex = _sex(self.p)
        self.refs: list[str] = []

    def build(self) -> dict | None:
        rows = [r for r in (self.who(), self.where(), self.with_whom(), self.facts(), self.times()) if r and r["items"]]
        quote = self.quote()
        if not rows and not quote:
            return None
        out = {"rows": rows, "refs": self.refs}
        if quote:
            out["quote"] = quote
        if self.p.get("confidence") in ("probable", "hypothesis"):
            out["conf"] = self.p["confidence"]
        return out

    # ---- building blocks

    def g(self, male: str, female: str, other: str) -> str:
        """The message id for the grammatical gender of the person."""
        return {"M": male, "F": female, "U": other}[self.sex]

    def ref(self, sources) -> list[int]:
        """Footnote numbers of sources, numbered in the order they are first cited."""
        out = []
        for s in sources or []:
            if s in self.t.sources:
                if s not in self.refs:
                    self.refs.append(s)
                if (n := self.refs.index(s) + 1) not in out:
                    out.append(n)
        return out

    def item(self, text: str, when: str = "", sources=(), conf: str = "", place: str | None = None,
             person: str | None = None) -> dict:
        it = {"t": text}
        if when:
            it["y"] = when
        if r := self.ref(sources):
            it["r"] = r
        if conf in ("probable", "hypothesis"):
            it["c"] = conf
        if place in self.ctx.geo.coords:
            it["pl"] = place
        if person in self.t.persons and not self.ctx.hidden(person):
            it["p"] = person
        return it

    def line(self, kind: str, items: list[dict], when: str = "", note: str = "", sources=(), conf: str = "",
             **extra) -> dict:
        ln = {"k": kind, "items": items}
        if when:
            ln["y"] = when
        if note:
            ln["n"] = note
        if r := self.ref(sources):
            ln["r"] = r
        if conf in ("probable", "hypothesis"):
            ln["c"] = conf
        ln.update({k: v for k, v in extra.items() if v is not None})
        return ln

    @staticmethod
    def chain(items: list[dict]) -> list[dict]:
        """At most CHAIN items: the first ones, "…" and the last one."""
        return items if len(items) <= CHAIN else items[:CHAIN - 2] + [{"t": "…"}] + items[-1:]

    @staticmethod
    def span(dates: list[Date]) -> str:
        """The years of some dates: "1850", "1850–1872", "c. 1850–1872" when the first is not exact."""
        if not dates:
            return ""
        first, last = min(d.year for d in dates), max(d.year for d in dates)
        text = str(first) if first == last else f"{first}–{last}"
        return text if all(d.kind == "exact" for d in dates if d.year == first) else tr("c. {date}", date=text)

    # ---- who: occupations and standing

    def occupations(self) -> list[dict]:
        """Occupations and standing in time order: events of type occupation (each with its date and source) and the
        entries of the free-text `occupation` list, dated by a year written in them. An entry without a date keeps
        its place after the entry before it; a free-text entry already recorded as an event is left out."""
        p, out = self.p, []
        last = START
        for i, e in enumerate(p.get("events") or []):
            if isinstance(e, dict) and e.get("type") == "occupation" and e.get("value"):
                d = safe_date(e.get("date"))
                last = _key(d) or last
                out.append({"key": (last, 0, i), "text": str(e["value"]), "date": d, "years": [d.year] if d else [],
                            "sources": e.get("sources") or [], "conf": e.get("confidence") or "",
                            "place": e.get("place"), "note": str(e.get("note") or "")})
        recorded = {(self.main_key(o["text"]), y) for o in out for y in o["years"] or [None]}
        recorded_mains = {m for m, _ in recorded}
        last = START
        for i, text in enumerate(map(str, p.get("occupation") or [])):
            years = sorted({int(y) for y in _YEAR.findall(text)})
            main = self.main_key(text)
            if any((main, y) in recorded for y in years) or (not years and main in recorded_mains):
                continue
            last = (years[0], 0, 0) if years else last
            out.append({"key": (last, 1, i), "text": text, "date": None, "years": years, "sources": [],
                        "conf": "", "place": None, "note": ""})
        out.sort(key=lambda o: o["key"])
        for o in out:
            o["main"] = self.main(o["text"])
            o["conf"] = o["conf"] or ("probable" if "?" in o["text"] else "")
            o["stratum"], o["rank"] = stratum(o["text"])
        return out

    @staticmethod
    def main(text: str) -> str:
        """The occupation itself, without the explanation in brackets: "komornik (Einlieger, 1835)" → "komornik"."""
        return re.split(r"\s*[(\[]", text, maxsplit=1)[0].replace("?", "").strip(" ,;") or text.strip()

    @classmethod
    def main_key(cls, text: str) -> str:
        return fold(cls.main(text))

    def who(self) -> dict | None:
        occ = self.occupations()
        groups: list[list[dict]] = []                    # consecutive entries of the same occupation
        for o in occ:
            if groups and fold(groups[-1][0]["main"]) == fold(o["main"]):
                groups[-1].append(o)
            else:
                groups.append([o])
        items = []
        for grp in groups:
            years = sorted({y for o in grp for y in o["years"]})
            when = "" if not years else str(years[0]) if len(years) == 1 else f"{years[0]}–{years[-1]}"
            items.append(self.item(grp[0]["main"], when=when, sources=[s for o in grp for s in o["sources"]],
                                   conf=grp[0]["conf"] if all(o["conf"] for o in grp) else ""))
        more = []
        for o in occ:
            row = [self.item(o["text"], conf=o["conf"])]
            if o["place"]:
                row.append(self.item(self.t.place_name(o["place"]), place=o["place"]))
            more.append(self.line("occupation", row, when=o["date"].text() if o["date"] else ", ".join(map(str, o["years"])),
                                  note=o["note"], sources=o["sources"]))
        ranked = [o for o in occ if o["rank"] and o["years"]]          # only dated entries tell a change in time
        if len(ranked) >= 2 and ranked[0]["rank"] != ranked[-1]["rank"]:
            a, b = ranked[0], ranked[-1]
            ends = [o["main"] + (f" ({', '.join(map(str, o['years']))})" if o["years"] else "") for o in (a, b)]
            text = tr("Rise in standing: {start} → {end}" if b["rank"] > a["rank"] else "Fall in standing: {start} → {end}",
                      start=ends[0], end=ends[1])
            more.append(self.line("standing", [self.item(text, conf="probable" if a["conf"] or b["conf"] else "")]))
        if not items:                                    # the religion alone is in the card's header already
            return None
        religion = [self.item(str(self.p["religion"]))] if self.p.get("religion") else []
        return {"key": "who", "label": tr(self.g("Who he was", "Who she was", "Who they were")), "sep": "→",
                "items": self.chain(items), "tail": religion, "more": more}

    # ---- where: the places of the life

    def kinds_text(self, s: Stay) -> str:
        """What the records of a stay are: "residence, births of 3 children, death; wedding 1835 (Wzorcowo)"."""
        labels = {"birth": tr("birth"), "baptism": tr("baptism"), "residence": tr("residence"), "census": tr("census"),
                  "emigration": tr("emigration"), "marriage": tr("marriage"), "occupation": tr("occupation record"),
                  "death": tr("death"), "burial": tr("burial")}
        text = ", ".join(trn("birth of a child|births of {n} children", s.kinds.count("child")) if k == "child" else labels[k]
                         for k in dict.fromkeys(s.kinds))
        weddings = [tr("wedding {date} ({place})", date=r.date.text() if r.date else "?", place=self.t.place_name(r.place))
                    for r in s.venues]
        return "; ".join(x for x in (text, ", ".join(weddings)) if x)

    def where(self) -> dict | None:
        stays = self.ctx.stays(self.pid)
        items, more = [], []
        for i, s in enumerate(stays):
            when = self.span(s.dates)
            if i:
                prev = stays[i - 1].place
                if (km := self.ctx.km(prev, s.place)) is not None and km >= 1:
                    more.append(self.line("move", [], note=tr("{n} km", n=km), km=km))
                elif self.ctx.same_parish(prev, s.place):
                    more.append(self.line("move", [], note=tr("in the same parish")))
            name = self.t.place_name(s.place)
            label = name + (" " + ", ".join(s.values) if s.values else "")
            more.append(self.line("stay", [self.item(label, conf=s.conf, place=s.place)], when=when,
                                  note=self.kinds_text(s), sources=s.sources))
            items.append(self.item(name, when=when, conf=s.conf, place=s.place))
        if not items:
            return None
        return {"key": "where", "label": tr(self.g("Where he lived", "Where she lived", "Where they lived")), "sep": "→",
                "items": self.chain(items), "tail": [], "more": more}

    # ---- with whom: the marriages

    def unions(self) -> list[Union]:
        t, out = self.t, []
        for i, fid in enumerate(t.spouse_in.get(self.pid, [])):
            f = t.families[fid]
            hidden = self.ctx.hidden(f.get("husband")) or self.ctx.hidden(f.get("wife"))
            md = None if hidden else t.date(f, "marriage")
            kids = list(f.get("children") or [])
            first = min((k for c in kids if (k := _key(t.date(t.persons[c], "birth") or t.date(t.persons[c], "baptism")))),
                        default=END)
            spouse = f.get("wife") if f.get("husband") == self.pid else f.get("husband")
            out.append(Union(f, spouse, hidden, md, kids, (_key(md) or first, i)))
        return sorted(out, key=lambda u: u.key)

    def with_whom(self) -> dict | None:
        t, unions = self.t, self.unions()
        if not unions:
            return None
        own_death = t.date(self.p, "death") or t.date(self.p, "burial")
        items, more = [], []
        for n, u in enumerate(unions, 1):
            sp = t.persons.get(u.spouse or "")
            name = (tr("Living person") if self.ctx.hidden(u.spouse) else t.name(u.spouse)) if sp else tr("spouse unknown")
            ev = {} if u.hidden else t.ev(u.family, "marriage")
            conf = u.family.get("confidence") or ""
            items.append(self.item(name, when=str(u.date.year) if u.date else "", sources=ev.get("sources"), conf=conf,
                                   person=u.spouse))
            head = [self.item(name, conf=conf, person=u.spouse)]
            if ev.get("place"):
                head.append(self.item(t.place_name(ev["place"]), place=ev["place"]))
            more.append(self.line("marriage", head, when=u.date.text() if u.date else "", sources=ev.get("sources"),
                                  num=n if len(unions) > 1 else None))
            end, end_date, widowed = self.marriage_end(u, own_death)
            info = [x for x in (self.marriage_ages(u.family, ev, u.date), self.children_text(u.children)) if x]
            if u.date and end_date and (length := age_between(u.date, end_date)) and length.years >= 1:
                info.append(trn("lasted {n} year|lasted {n} years", length.years, n=number(length)))
            if info:
                more.append(self.line("info", [self.item(x) for x in info]))
            if end:
                more.append(end)
            witnesses = _texts(ev.get("witnesses"))
            if witnesses and not self.recent(u.date):
                more.append(self.line("note", [self.item(tr("witnesses: {names}", names="; ".join(witnesses)))],
                                      sources=ev.get("sources")))
            if n < len(unions) and end_date and (widowed or end["k"] == "divorce"):
                nxt = unions[n].date
                text = (tr(self.g("He was widowed on {date}", "She was widowed on {date}", "Widowed on {date}"),
                           date=end_date.text()) if widowed else tr("divorced on {date}", date=end_date.text()))
                if nxt and (gap := after(end_date, nxt)):
                    text += "; " + tr("remarried {after} ({date})", after=gap, date=nxt.text())
                more.append(self.line("link", [self.item(text)]))
        total = sum(len(u.children) for u in unions)
        tail = [self.item(trn("{n} child|{n} children", total))] if total else []
        return {"key": "with", "label": tr(self.g("Whom he lived with", "Whom she lived with", "Whom they lived with")),
                "sep": "·", "items": items, "tail": tail, "more": more}

    def recent(self, d: Date | None) -> bool:
        """A record less than 100 years old: its witnesses and godparents may be living (left out in public mode)."""
        return self.ctx.public and bool(d) and d.year > TODAY.year - 100

    def marriage_ages(self, f: dict, ev: dict, md: Date | None) -> str:
        t, ages = self.t, {}
        for role in ("husband", "wife"):
            if isinstance(age := ev.get(f"{role}_age"), int):
                ages[role] = str(age)
            elif md and (pid := f.get(role)) in t.persons and not self.ctx.hidden(pid):
                p = t.persons[pid]
                if a := age_between(t.date(p, "birth") or t.date(p, "baptism"), md):
                    ages[role] = number(a)
        if len(ages) == 2:
            return tr("groom {a}, bride {b}", a=ages["husband"], b=ages["wife"])
        if "husband" in ages:
            return tr("groom {a}", a=ages["husband"])
        return tr("bride {b}", b=ages["wife"]) if "wife" in ages else ""

    def children_text(self, kids: list[str]) -> str:
        if not kids:
            return ""
        text = trn("{n} child|{n} children", len(kids))
        if died := self.died_young(kids):
            text += " " + tr("({n} died in childhood)", n=len(died))
        return text

    def marriage_end(self, u: Union, own_death: Date | None) -> tuple[dict | None, Date | None, bool]:
        """How a marriage ended: (the line telling it, its date, whether this person was widowed)."""
        t = self.t
        if div := t.date(u.family, "divorce"):
            return (self.line("divorce", [self.item(tr("divorced on {date}", date=div.text()))],
                              sources=t.ev(u.family, "divorce").get("sources")), div, False)
        sp = t.persons.get(u.spouse or "")
        sd = None if not sp or self.ctx.hidden(u.spouse) else t.date(sp, "death") or t.date(sp, "burial")
        if sd and (not own_death or _key(sd) <= _key(own_death)):
            sev = t.ev(sp, "death") or t.ev(sp, "burial")
            notes = [age_text(a)] if (a := self.ctx.ages.get(u.spouse)) else []
            if sev.get("cause"):
                notes.append(tr("cause: {cause}", cause=sev["cause"]))
            text = tr(self.g("ended with the death of his wife on {date}", "ended with the death of her husband on {date}",
                             "ended with the death of the spouse on {date}"), date=sd.text())
            return self.line("end", [self.item(text)], note=", ".join(notes), sources=sev.get("sources")), sd, True
        if own_death and not u.hidden:
            text = tr(self.g("ended with his death on {date}", "ended with her death on {date}",
                             "ended with the person's death on {date}"), date=own_death.text())
            return self.line("end", [self.item(text)]), own_death, False
        return None, None, False

    def died_young(self, kids: list[str]) -> list[str]:
        return [c for c in kids if (a := self.ctx.ages.get(c)) and a.years < CHILDHOOD]

    # ---- worth knowing: facts computed from the data

    def facts(self) -> dict | None:
        t, p, out = self.t, self.p, []
        if life := self.ctx.ages.get(self.pid):
            out.append(self.lifespan_line(life))
        kids = [c for fid in t.spouse_in.get(self.pid, []) for c in t.families[fid].get("children") or []]
        if died := self.died_young(kids):                # the number of children alone is in "Whom … lived with"
            text = trn(self.g("Father of {n} child|Father of {n} children", "Mother of {n} child|Mother of {n} children",
                              "Parent of {n} child|Parent of {n} children"), len(kids))
            text += "; " + tr("{n} of them died in childhood", n=len(died))
            names = ", ".join(f"{t.persons[c].get('given') or '?'} ({age_text(self.ctx.ages[c])})" for c in died)
            sources = [s for c in died for k in ("death", "burial") for s in t.ev(t.persons[c], k).get("sources") or []]
            out.append(self.line("fact", [self.item(text)], note=names, sources=sources))
        if ages := self.ages_at_children(kids):
            out.append(ages)
        if order := self.birth_order():
            out.append(order)
        if self.pid in self.ctx.longest:
            key, n = self.ctx.longest[self.pid]
            out.append(self.line("fact", [self.item(tr(self.g(
                "He was the longest-lived of the {surname} line ({n} with a known age)",
                "She was the longest-lived of the {surname} line ({n} with a known age)",
                "The longest-lived of the {surname} line ({n} with a known age)"), surname=self.ctx.line_name[key], n=n))]))
        if self.ctx.longest_ancestor and self.ctx.longest_ancestor[0] == self.pid:
            out.append(self.line("fact", [self.item(tr(self.g(
                "He was the longest-lived of the proband's ancestors ({n} with a known age)",
                "She was the longest-lived of the proband's ancestors ({n} with a known age)",
                "The longest-lived of the proband's ancestors ({n} with a known age)"), n=self.ctx.longest_ancestor[1]))]))
        if self.pid in self.ctx.first_leavers:
            out.append(self.line("fact", [self.item(tr(self.g(
                "He was the first known of the {surname} line to leave the home area",
                "She was the first known of the {surname} line to leave the home area",
                "The first known of the {surname} line to leave the home area"),
                surname=self.ctx.line_name[self.ctx.line[self.pid]]))], note=self.leaving_text(self.ctx.leaving[self.pid])))
        for e in p.get("events") or []:
            if isinstance(e, dict) and e.get("type") in ("military", "emigration"):
                d = safe_date(e.get("date"))
                text = tr("military service") if e["type"] == "military" else tr("emigration")
                if e.get("value"):
                    text += f": {e['value']}"
                row = [self.item(text, conf=e.get("confidence") or "")]
                if e.get("place"):
                    row.append(self.item(t.place_name(e["place"]), place=e["place"]))
                out.append(self.line("fact", row, when=d.text() if d else "", note=str(e.get("note") or ""),
                                     sources=e.get("sources")))
        out += self.signatures()
        for k in ("birth", "baptism"):
            ev = t.ev(p, k)
            if (godparents := _texts(ev.get("godparents"))) and not self.recent(t.date(p, k)):
                out.append(self.line("fact", [self.item(tr("godparents: {names}", names="; ".join(godparents)))],
                                     sources=ev.get("sources")))
                break
        if p.get("variants"):
            out.append(self.line("fact", [self.item(tr("in the records also as: {names}",
                                                       names=", ".join(map(str, p["variants"]))))]))
        if langs := self.record_languages():
            out.append(self.line("fact", [self.item(tr("languages of the records: {languages}", languages=langs))]))
        if not out:
            return None
        top = [ln["items"][0] | ({"r": ln["r"]} if ln.get("r") else {}) for ln in out[:2]]
        return {"key": "facts", "label": tr("Worth knowing"), "sep": "·", "items": top, "tail": [], "more": out}

    def lifespan_line(self, life: Age) -> dict:
        t, p = self.t, self.p
        if life.years == 0 and life.months is not None:
            if life.months:
                text = trn(self.g("He died aged {n} month|He died aged {n} months",
                                  "She died aged {n} month|She died aged {n} months",
                                  "Died aged {n} month|Died aged {n} months"), life.months)
            else:
                text = trn(self.g("He died aged {n} day|He died aged {n} days", "She died aged {n} day|She died aged {n} days",
                                  "Died aged {n} day|Died aged {n} days"), life.days or 0)
        elif life.years == 0:
            text = tr(self.g("He died under a year old", "She died under a year old", "Died under a year old"))
        else:
            text = trn(self.g("He lived {n} year|He lived {n} years", "She lived {n} year|She lived {n} years",
                              "Lived {n} year|Lived {n} years"), life.years, n=number(life))
        death = t.ev(p, "death") or t.ev(p, "burial")
        notes = [trn("the death record gives {n} year|the death record gives {n} years", life.recorded)] \
            if life.recorded is not None else []
        if death.get("cause"):
            notes.append(tr("cause of death: {cause}", cause=death["cause"]))
        conf = next((c for k in ("birth", "baptism", "death", "burial")
                     if (c := t.ev(p, k).get("confidence")) in ("probable", "hypothesis")), "")
        sources = [s for k in ("birth", "baptism", "death", "burial") for s in t.ev(p, k).get("sources") or []]
        return self.line("fact", [self.item(text, conf=conf)], note=", ".join(notes), sources=sources)

    def ages_at_children(self, kids: list[str]) -> dict | None:
        t = self.t
        birth = t.date(self.p, "birth") or t.date(self.p, "baptism")
        rows = []
        for c in kids:
            k = t.persons[c]
            cd = t.date(k, "birth") or t.date(k, "baptism")
            if not self.ctx.hidden(c) and (a := age_between(birth, cd)):
                rows.append((_key(cd), a, c))
        if len(rows) < 2:
            return None
        rows.sort(key=lambda r: r[0])
        (_, first, c1), (_, last, c2) = rows[0], rows[-1]
        sources = [s for c in (c1, c2) for k in ("birth", "baptism") for s in t.ev(t.persons[c], k).get("sources") or []]
        return self.line("fact", [self.item(tr("first child at the age of {a}, the last at {b}",
                                               a=number(first), b=number(last)))], sources=sources)

    def birth_order(self) -> dict | None:
        kids = (self.t.parents_family(self.pid) or {}).get("children") or []
        if len(kids) < 2 or self.pid not in kids:
            return None
        i, n = kids.index(self.pid) + 1, len(kids)
        if i == 1:
            text = tr("the eldest of {n} known children", n=n)
        elif i == n:
            text = tr("the youngest of {n} known children", n=n)
        else:
            text = tr("child {i} of {n} known children", i=i, n=n)
        return self.line("fact", [self.item(text)])

    def leaving_text(self, lv: dict) -> str:
        t = self.t
        bits = [" → ".join(x for x in (t.place_name(lv["from"]), t.place_name(lv["to"])) if x)]
        if lv.get("km"):
            bits.append(tr("{n} km", n=lv["km"]))
        if lv.get("year"):
            bits.append(str(lv["year"]))
        return ", ".join(b for b in bits if b)

    def signatures(self) -> list[dict]:
        by: dict[str, list[dict]] = {"signed": [], "mark": []}
        for e in self.p.get("events") or []:
            if isinstance(e, dict) and e.get("type") == "signature" and e.get("value") in by:
                by[e["value"]].append(e)
        out = []
        first = lambda evs: min((_key(safe_date(e.get("date"))) or END for e in evs), default=END)
        for value, evs in sorted(by.items(), key=lambda kv: first(kv[1])):
            if not evs:
                continue
            if value == "signed":
                text = tr(self.g("He signed his name", "She signed her name", "Signed their name"))
            else:
                text = tr(self.g("He could not write and made a mark instead of a signature",
                                 "She could not write and made a mark instead of a signature",
                                 "Could not write and made a mark instead of a signature"))
            years = ", ".join(str(d.year) for e in evs if (d := safe_date(e.get("date"))))
            conf = next((e["confidence"] for e in evs if e.get("confidence")), "")
            out.append(self.line("fact", [self.item(text, conf=conf)], when=years,
                                 note="; ".join(str(e["note"]) for e in evs if e.get("note")),
                                 sources=[s for e in evs for s in e.get("sources") or []]))
        return out

    def own_sources(self) -> list[str]:
        """Sources of the person's own facts and marriages (research notes of type `other` left out)."""
        t, p, out = self.t, self.p, []
        for k in ("birth", "baptism", "death", "burial"):
            out += t.ev(p, k).get("sources") or []
        for e in p.get("events") or []:
            if isinstance(e, dict) and e.get("type") != "other":
                out += e.get("sources") or []
        for u in self.unions():
            if not u.hidden:
                out += t.ev(u.family, "marriage").get("sources") or []
        return list(dict.fromkeys(s for s in out if s in t.sources))

    def record_languages(self) -> str:
        count: Counter[str] = Counter()
        for s in self.own_sources():
            src = self.t.sources[s]
            if src.get("type") not in ("oral", "index", "online_tree", "publication"):
                count.update(language_names(src.get("language")))
        return ", ".join(f"{name} ({n})" for name, n in count.most_common())

    # ---- the times: partition and great events

    def life_years(self) -> tuple[int, int] | None:
        """The years of the life: from the birth (or a narrow estimate of it) to the death, today for a living
        person, or else the last year the records show the person alive."""
        t, p = self.t, self.p
        born = t.birth_year(p)
        if born is None and (w := t.birth_window(self.pid)) and w.lo and w.hi and w.hi - w.lo <= 10:
            born = (w.lo + w.hi) // 2
        if born is None:
            return None
        last = t.death_year(p)
        if last is None:
            last = TODAY.year if t.living(self.pid) else max((d.year for s in self.ctx.stays(self.pid) for d in s.dates),
                                                             default=None)
        return (born, last) if last is not None and last >= born else None

    def partitions(self) -> list[str]:
        """The partitions of Poland the person's places lay in during the partitions (1772–1918)."""
        out = []
        for s in self.ctx.stays(self.pid):
            years = [d.year for d in s.dates]
            if years and (max(years) < 1772 or min(years) > 1918):
                continue
            if (part := self.ctx.geo.partition_of(s.place)) and part not in out:
                out.append(part)
        return out

    def times(self) -> dict | None:
        if not (span := self.life_years()):
            return None
        born, last = span
        parts = self.partitions() if born <= 1918 and last >= 1772 else []
        events = lived_through(born, last, set(parts))
        if not events and not parts:
            return None
        more = []
        for e in events:
            ages = max(e.first - born, 0), max(e.last - born, 0)
            more.append(self.line("event", [self.item(e.name)], when=self.years_text(e.first, e.last),
                                  note=trn("aged {n}", ages[1], n=str(ages[0]) if ages[0] == ages[1] else f"{ages[0]}–{ages[1]}")))
        weighty = sorted(events, key=lambda e: (-e.weight, e.first - born < 18, e.first))[:2]
        items = [self.item(partition_label(x)) for x in parts]
        items += [self.item(e.name, when=self.years_text(e.first, e.last)) for e in sorted(weighty, key=lambda e: e.first)]
        return {"key": "times", "label": tr(self.g("The times he lived in", "The times she lived in", "The times they lived in")),
                "sep": "·", "items": items, "tail": [], "more": more}

    @staticmethod
    def years_text(a: int, b: int) -> str:
        return str(a) if a == b else f"{a}–{b}"

    # ---- a quote: a family account or the words of a record

    def quote(self) -> dict | None:
        t, p = self.t, self.p
        q = p.get("quote")
        if isinstance(q, dict) and q.get("text"):
            src = t.sources.get(q.get("source") or "") or {}
            if not (self.ctx.public and src.get("type") == "oral"):
                return {"t": str(q["text"]).strip(), "by": self.attribution(q.get("source")), "r": self.ref([q.get("source")])}
        if not (names := self.name_tokens()):
            return None
        own = self.own_sources()
        oral = [] if self.ctx.public else [s for s in own + self.parents_sources() if t.sources[s].get("type") == "oral"]
        for s in oral:
            if text := self.sentence(t.sources[s].get("transcription"), names, surname=False):
                return {"t": text, "by": self.attribution(s), "r": self.ref([s])}
        # the words of the person's own records: the death record first, then the marriage, the birth, the rest
        first = [s for k in ("death", "burial") for s in t.ev(p, k).get("sources") or []]
        first += [s for u in self.unions() if not u.hidden for s in t.ev(u.family, "marriage").get("sources") or []]
        first += [s for k in ("birth", "baptism") for s in t.ev(p, k).get("sources") or []]
        for s in dict.fromkeys([s for s in first if s in own] + own):
            if t.sources[s].get("type") not in ("oral", "index", "online_tree") and \
                    (text := self.sentence(t.sources[s].get("transcription"), names, surname=True)):
                return {"t": text, "by": self.attribution(s), "r": self.ref([s])}
        return None

    def parents_sources(self) -> list[str]:
        fam = self.t.parents_family(self.pid)
        return [s for s in self.t.ev(fam or {}, "marriage").get("sources") or [] if s in self.t.sources]

    def name_tokens(self) -> tuple[set[str], set[str]] | None:
        """Folded words of the given names and the surnames, with the variants: a variant of two or more words
        gives both; a single word is a surname when it begins like one (Kowalsky) and a given name otherwise
        (Josephus)."""
        p = self.p
        given = {w for w in fold(p.get("given") or "").split() if len(w) >= 3}
        surnames = {w for x in [p.get("surname"), *(p.get("married_surnames") or [])] if x
                    for w in fold(x).split() if len(w) >= 3}
        like = lambda w, keys: any(w[:3] == k[:3] for k in keys)
        for v in p.get("variants") or []:
            words = [w for w in fold(str(v)).split() if len(w) >= 3]
            if len(words) > 1:
                given.add(words[0])
                surnames.add(words[-1])
            elif words:
                (surnames if like(words[0], surnames) and not like(words[0], given) else given).add(words[0])
        return (given, surnames) if given else None

    @staticmethod
    def sentence(text, names: tuple[set[str], set[str]], surname: bool) -> str:
        """The first sentence of a transcription that names the person (by a given name, and with `surname` also by
        a surname; inflected forms match by their stem). A sentence too long to quote is cut to the clauses around
        the name, marked with "…"."""
        if not text:
            return ""
        given, surnames = names

        def named(s: str, keys: set[str]) -> bool:
            return any(w.startswith(k[:max(4, len(k) - 2)]) for w in re.findall(r"\w+", fold(s)) for k in keys)

        for s in map(plain, sentences(str(text))):
            if "|" in s or len(s) < QUOTE_LEN[0] or not named(s, given) or (surname and not named(s, surnames)):
                continue
            if len(s) <= QUOTE_LEN[1]:
                return s
            clauses = re.split(r"(?<=[,;:])\s+", s)
            i = next(i for i, c in enumerate(clauses) if named(c, given))
            a = b = i
            while True:                                  # grow around the name while it fits
                grown = False
                for x, y in ((a, b + 1), (a - 1, b)):
                    if 0 <= x and y < len(clauses) and len(" ".join(clauses[x:y + 1])) <= QUOTE_LEN[1] - 4:
                        a, b, grown = x, y, True
                        break
                if not grown:
                    break
            part = " ".join(clauses[a:b + 1]).rstrip(",;: ")
            if QUOTE_LEN[0] <= len(part) <= QUOTE_LEN[1]:
                return ("… " if a else "") + part + (" …" if b < len(clauses) - 1 else "")
        return ""

    def attribution(self, sid: str | None) -> str:
        """Who told it (an oral source, outside public mode) or the title of the source, shortened."""
        src = self.t.sources.get(sid or "") or {}
        text = str(src.get("title") or sid or "")
        if src.get("type") == "oral" and src.get("informant") and not self.ctx.public:
            text = re.split(r"\s+[—–]\s+|;", str(src["informant"]), maxsplit=1)[0]
        return text if len(text) <= 90 else text[:88].rstrip() + "…"
