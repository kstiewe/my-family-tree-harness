"""The tree: loading, validation, relations, date estimates and research hints."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .dates import TODAY, Date, Window, parse_date, safe_date, search_range, sort_key
from .geneteka import REGIONS, kind_label, page_url
from .geo import Geo, valid_coords
from .i18n import tr
from .schema import (CONFIDENCE, CONFLICT_KEYS, EVENT_KEYS, EVENT_TYPES, EVIDENCE, EXTRA_EVENT_KEYS, FAMILY_CONFLICT_ABOUT,
                     FAMILY_KEYS, FAMILY_OVERRIDE_ABOUT, IDENTITY_KEYS, INFORMATION, LANGUAGES, LIFE_EVENTS, MARRIAGE_KEYS,
                     NAMESAKES, NO_PARISH_NEEDED, OVERRIDE_KEYS, PARTITIONS, PERSON_CONFLICT_ABOUT, PERSON_KEYS,
                     PERSON_OVERRIDE_ABOUT, PLACE_KEYS, PROJECT_KEYS, QUOTE_KEYS, SEXES, SIGNATURES, SOURCE_CLASSES,
                     SOURCE_KEYS, SOURCE_QUALITY, SOURCE_TYPES, event_type_label, place_kind)


def fold(text: str) -> str:
    """Lower-case, without Polish diacritics (for matching names)."""
    text = text.lower().replace("ł", "l")
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


@dataclass
class Issue:
    """A validation error or warning. `code` is stable and machine-readable; `text` is translated."""
    code: str
    record: str | None
    text: str

    def __str__(self) -> str:
        return self.text


# What to do about each issue code; shown to agents in `build.py --json`.
FIXES = {
    "missing-file": "Create the file (an empty list `[]` is enough) or point --workspace at the right directory.",
    "yaml-syntax": "Fix the YAML syntax at the reported line; dates must be quoted.",
    "top-level-type": "persons/families/places/sources must be YAML lists; project.yaml must be a mapping.",
    "missing-id": "Give the record an id taken from the 'next free IDs' line.",
    "bad-id": "Use the prefix of the file (I, F, P, S) and at least four digits, e.g. I0001.",
    "duplicate-id": "Renumber one of the records with the next free ID and update every reference to it.",
    "unknown-field": "Check the spelling against `build.py --schema`; move free text to notes.",
    "bad-value": "Use one of the allowed values listed in the message.",
    "not-a-list": "Write the value as a YAML list: [a, b].",
    "not-a-mapping": "Write the event as a mapping: {date: \"…\", place: P0001, sources: [S0001]}.",
    "bad-date": "Quote the date and use one of the patterns from the message.",
    "unknown-place": "Add the place to places.yaml first or fix the ID.",
    "unknown-source": "Add the source to sources.yaml first or fix the ID.",
    "unknown-person": "Add the person to persons.yaml first or fix the ID.",
    "bad-age": "Write the age as a whole number of years.",
    "bad-proband": "Set project.yaml `proband` to an existing person ID.",
    "no-name": "Give the person at least a given name or a surname.",
    "missing-event-type": "Set `type` of the event (see extra_event_types in --schema).",
    "child-in-several-families": "Keep the child in the biological parents' family only; describe others in notes.",
    "family-without-spouses": "Set husband or wife.",
    "sex-mismatch": "Check the sex of the person or swap husband/wife.",
    "spouse-is-child": "A person cannot be a spouse and a child in the same family.",
    "duplicate-child": "List each child once.",
    "missing-name": "Give the place a name.",
    "bad-coords": "Write coordinates as [latitude, longitude], e.g. [52.53, 20.49].",
    "suspicious-coords": "Check the order: [latitude, longitude] (Poland is about [49..55, 14..24]) and the source in notes.",
    "bad-admin": "Write admin entries as {period: \"1867..1918\", value: \"…\"}.",
    "missing-title": "Give the source a title.",
    "missing-scan-file": "Save the file at that path in the workspace or fix `file` of the source.",
    "unused-source": "Cite the source in some fact's `sources`, or remove it if it was a mistake.",
    "unknown-language": "Use an ISO 639-1 code (pl, la, de, ru, uk …) of the original document.",
    "cycle": "A person is their own ancestor: check children/parents in families.yaml.",
    "chronology": "Check the dates and ages involved; mark doubtful facts with confidence and notes.",
    "assumed-living": "Set `living: false` if the person has died (even without a date), or add dates.",
    "bad-quote": "Write the quote as {text: \"one short sentence\", source: S0001}.",
    "bad-conflict": "Write each conflict as {about: birth, note: \"what disagrees\", resolved: false, sources: [S0001]}.",
    "bad-override": "Write confidence_override as {score: 0-100, reason: \"why the computed score is wrong\"}.",
    "bad-identity": "Write identity as {namesakes: excluded | possible, note: \"what was checked\"}.",
}


@dataclass
class Hint:
    level: int                       # 1 = priority, 2 = important, 3 = supplementary
    text: str
    details: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)


class Tree:
    def __init__(self, data_dir: Path):
        self.root = data_dir.parent         # the workspace; `source.file` paths are relative to it
        self.errors: list[Issue] = []
        self.warnings: list[Issue] = []
        self.project = self._load(data_dir / "project.yaml", dict) or {}
        self.persons = self._records(data_dir / "persons.yaml", "I")
        self.families = self._records(data_dir / "families.yaml", "F")
        self.places = self._records(data_dir / "places.yaml", "P")
        self.sources = self._records(data_dir / "sources.yaml", "S")
        self.child_of: dict[str, list[str]] = {}
        self.spouse_in: dict[str, list[str]] = {}
        for fid, f in self.families.items():
            for role in ("husband", "wife"):
                if f.get(role):
                    self.spouse_in.setdefault(f[role], []).append(fid)
            for c in f.get("children") or []:
                self.child_of.setdefault(c, []).append(fid)
        self._used_sources: set[str] = set()
        self._geo: dict = {}
        # chronology warnings per record and the fact they touch (birth, death, link, marriage), for the confidence
        self.chronology: dict[str, list[tuple[str, str]]] = {}
        self.validate()
        self.kekule = self._kekule() if not self.errors else {}
        if not self.errors:
            self._check_living()

    # ---- loading

    @staticmethod
    def peek_project(data_dir: Path) -> dict:
        """project.yaml without validation (to pick the language before any message is produced)."""
        try:
            with (data_dir / "project.yaml").open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except (OSError, yaml.YAMLError):
            return {}
        return data if isinstance(data, dict) else {}

    def _load(self, path: Path, expected: type):
        if not path.exists():
            self.err("missing-file", None, tr("missing file {path}", path=path))
            return None
        try:
            with path.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except yaml.YAMLError as e:
            self.err("yaml-syntax", None, tr("{file}: YAML syntax error: {error}", file=path.name, error=e))
            return None
        if data is not None and not isinstance(data, expected):
            self.err("top-level-type", None, tr("{file}: expected a list at the top level" if expected is list
                                                else "{file}: expected a mapping at the top level", file=path.name))
            return None
        return data

    def _records(self, path: Path, prefix: str) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for i, rec in enumerate(self._load(path, list) or [], 1):
            if not isinstance(rec, dict) or "id" not in rec:
                self.err("missing-id", None, tr("{file}, entry {i}: missing id field", file=path.name, i=i))
                continue
            rid = str(rec["id"])
            if not re.fullmatch(prefix + r"\d{4,}", rid):
                self.err("bad-id", rid, tr("{file}: id {id!r} should look like {prefix}0001", file=path.name, id=rid, prefix=prefix))
            if rid in out:
                self.err("duplicate-id", rid, tr("{file}: duplicate id {id}", file=path.name, id=rid))
            out[rid] = rec
        return out

    # ---- validation

    @staticmethod
    def _record_of(ctx: str | None) -> str | None:
        return re.split(r"[.\[ ]", ctx, maxsplit=1)[0] if ctx else None

    def err(self, code: str, ctx: str | None, msg: str) -> None:
        self.errors.append(Issue(code, self._record_of(ctx), msg))

    def warn(self, code: str, ctx: str | None, msg: str) -> None:
        self.warnings.append(Issue(code, self._record_of(ctx), msg))

    def _keys(self, ctx: str, rec: dict, allowed: set[str]) -> None:
        extra = sorted(set(rec) - allowed)
        if extra:
            self.warn("unknown-field", ctx, tr("{ctx}: unknown fields {fields} (typo?)", ctx=ctx, fields=", ".join(extra)))

    def _enum(self, ctx: str, value, allowed) -> None:
        if value is not None and value not in allowed:
            self.err("bad-value", ctx, tr("{ctx}: {value!r} — allowed: {allowed}", ctx=ctx, value=value, allowed=", ".join(sorted(allowed))))

    def source_files(self, sid: str) -> list[str]:
        """Paths (relative to the workspace) of the local copies of a source: `file` is one path or a list."""
        value = self.sources[sid].get("file")
        if isinstance(value, str):
            return [value]
        return [p for p in value if isinstance(p, str)] if isinstance(value, list) else []

    def _list(self, ctx: str, rec: dict, key: str) -> list:
        value = rec.get(key)
        if value is None:
            return []
        if not isinstance(value, list):
            self.err("not-a-list", ctx, tr("{ctx}.{key}: expected a list [..]", ctx=ctx, key=key))
            return []
        return value

    def _event(self, ctx: str, ev, allowed: set[str]) -> None:
        if not isinstance(ev, dict):
            self.err("not-a-mapping", ctx, tr("{ctx}: expected a mapping {{date: …, place: …}}", ctx=ctx))
            return
        self._keys(ctx, ev, allowed)
        try:
            parse_date(ev.get("date"))
        except ValueError as e:
            self.err("bad-date", ctx, f"{ctx}: {e}")
        if ev.get("place") and ev["place"] not in self.places:
            self.err("unknown-place", ctx, tr("{ctx}: unknown place {id}", ctx=ctx, id=ev["place"]))
        for s in self._list(ctx, ev, "sources"):
            if s in self.sources:
                self._used_sources.add(s)
            else:
                self.err("unknown-source", ctx, tr("{ctx}: unknown source {id}", ctx=ctx, id=s))
        for k in ("age", "husband_age", "wife_age"):
            if ev.get(k) is not None and not isinstance(ev[k], int):
                self.err("bad-age", ctx, tr("{ctx}.{key}: age must be an integer", ctx=ctx, key=k))
        self._enum(f"{ctx}.confidence", ev.get("confidence"), CONFIDENCE)
        for k in ("godparents", "witnesses"):
            if ev.get(k) is not None and not isinstance(ev[k], (str, list)):
                self.err("not-a-list", ctx, tr("{ctx}.{key}: expected a list [..]", ctx=ctx, key=k))

    def _quote(self, ctx: str, q) -> None:
        if not isinstance(q, dict) or not isinstance(q.get("text"), str):
            self.err("bad-quote", ctx, tr("{ctx}: expected {{text: \"…\", source: S0001}}", ctx=ctx))
            return
        self._keys(ctx, q, QUOTE_KEYS)
        if q.get("source") in self.sources:
            self._used_sources.add(q["source"])
        elif q.get("source"):
            self.err("unknown-source", ctx, tr("{ctx}: unknown source {id}", ctx=ctx, id=q["source"]))

    def _source_refs(self, ctx: str, value, use: bool) -> None:
        """Source IDs in a field that holds one ID or a list; `use` = they support a fact (not an unused source)."""
        for s in value if isinstance(value, list) else [value] if value is not None else []:
            if s in self.sources:
                if use:
                    self._used_sources.add(s)
            else:
                self.err("unknown-source", ctx, tr("{ctx}: unknown source {id}", ctx=ctx, id=s))

    def _conflicts(self, ctx: str, rec: dict, about: set[str]) -> None:
        for i, c in enumerate(self._list(ctx, rec, "conflicts"), 1):
            where = f"{ctx}.conflicts[{i}]"
            if not isinstance(c, dict) or not isinstance(c.get("note"), str) or not c["note"].strip():
                self.err("bad-conflict", ctx, tr("{ctx}: expected {{about: …, note: \"…\", resolved: true/false}}", ctx=where))
                continue
            self._keys(where, c, CONFLICT_KEYS)
            self._enum(f"{where}.about", c.get("about"), about)
            if c.get("resolved") is not None and not isinstance(c["resolved"], bool):
                self.err("bad-value", ctx, tr("{ctx}: {value!r} — allowed: {allowed}", ctx=f"{where}.resolved",
                                              value=c["resolved"], allowed="true, false"))
            self._source_refs(where, c.get("sources"), use=True)

    def _overrides(self, ctx: str, rec: dict, about: set[str]) -> None:
        value = rec.get("confidence_override")
        for i, o in enumerate(value if isinstance(value, list) else [value] if value is not None else [], 1):
            where = f"{ctx}.confidence_override" + (f"[{i}]" if isinstance(value, list) else "")
            score = o.get("score") if isinstance(o, dict) else None
            if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 100 \
                    or not isinstance(o.get("reason"), str) or not o["reason"].strip():
                self.err("bad-override", ctx, tr("{ctx}: expected {{score: 0–100, reason: \"…\"}}", ctx=where))
                continue
            self._keys(where, o, OVERRIDE_KEYS)
            self._enum(f"{where}.about", o.get("about"), about)

    def validate(self) -> None:
        self._keys("project.yaml", self.project, PROJECT_KEYS)
        pb = self.project.get("proband")
        if pb and pb not in self.persons:
            self.err("bad-proband", "project.yaml", tr("project.yaml: proband {id} does not exist in persons.yaml", id=pb))
        for pid, p in self.persons.items():
            self._keys(pid, p, PERSON_KEYS)
            if not (p.get("given") or p.get("surname") or p.get("married_surnames")):
                self.err("no-name", pid, tr("{id}: no given name and no surname", id=pid))
            self._enum(f"{pid}.sex", p.get("sex", "U"), SEXES)
            self._enum(f"{pid}.confidence", p.get("confidence"), CONFIDENCE)
            for key in LIFE_EVENTS:
                if key in p:
                    self._event(f"{pid}.{key}", p[key], EVENT_KEYS)
            for i, e in enumerate(self._list(pid, p, "events"), 1):
                self._event(f"{pid}.events[{i}]", e, EXTRA_EVENT_KEYS)
                if isinstance(e, dict):
                    self._enum(f"{pid}.events[{i}].type", e.get("type"), EVENT_TYPES)
                    if not e.get("type"):
                        self.err("missing-event-type", pid, tr("{ctx}: missing type field", ctx=f"{pid}.events[{i}]"))
                    if e.get("type") == "signature":
                        self._enum(f"{pid}.events[{i}].value", e.get("value"), SIGNATURES)
            if "quote" in p:
                self._quote(f"{pid}.quote", p["quote"])
            self._conflicts(pid, p, PERSON_CONFLICT_ABOUT)
            self._overrides(pid, p, PERSON_OVERRIDE_ABOUT)
            if "identity" in p:
                if not isinstance(p["identity"], dict):
                    self.err("bad-identity", pid, tr("{ctx}: expected {{namesakes: excluded | possible, note: \"…\"}}",
                                                     ctx=f"{pid}.identity"))
                else:
                    self._keys(f"{pid}.identity", p["identity"], IDENTITY_KEYS)
                    self._enum(f"{pid}.identity.namesakes", p["identity"].get("namesakes"), NAMESAKES)
            for k in ("married_surnames", "variants", "occupation", "todo"):
                self._list(pid, p, k)
            if len(self.child_of.get(pid, [])) > 1:
                self.warn("child-in-several-families", pid, tr("{id}: child in several families ({families}) — the first one defines the line",
                                                               id=pid, families=", ".join(self.child_of[pid])))
        for fid, f in self.families.items():
            self._keys(fid, f, FAMILY_KEYS)
            if not f.get("husband") and not f.get("wife"):
                self.err("family-without-spouses", fid, tr("{id}: family without spouses (set husband or wife)", id=fid))
            for role, sex in (("husband", "M"), ("wife", "F")):
                pid = f.get(role)
                if pid and pid not in self.persons:
                    self.err("unknown-person", fid, tr("{ctx}: unknown person {id}", ctx=f"{fid}.{role}", id=pid))
                elif pid and self.persons[pid].get("sex", "U") not in (sex, "U"):
                    self.warn("sex-mismatch", fid, tr("{ctx}: {id} has sex {sex}", ctx=f"{fid}.{role}", id=pid, sex=self.persons[pid].get("sex")))
            kids = self._list(fid, f, "children")
            for c in kids:
                if c not in self.persons:
                    self.err("unknown-person", fid, tr("{ctx}: unknown person {id}", ctx=f"{fid}.children", id=c))
                if c in (f.get("husband"), f.get("wife")):
                    self.err("spouse-is-child", fid, tr("{id}: {person} is both a spouse and a child", id=fid, person=c))
            if len(set(kids)) != len(kids):
                self.err("duplicate-child", fid, tr("{ctx}: repeated ID", ctx=f"{fid}.children"))
            if "marriage" in f:
                self._event(f"{fid}.marriage", f["marriage"], MARRIAGE_KEYS)
            if "divorce" in f:
                self._event(f"{fid}.divorce", f["divorce"], EVENT_KEYS)
            self._enum(f"{fid}.confidence", f.get("confidence"), CONFIDENCE)
            self._conflicts(fid, f, FAMILY_CONFLICT_ABOUT)
            self._overrides(fid, f, FAMILY_OVERRIDE_ABOUT)
        for plid, pl in self.places.items():
            self._keys(plid, pl, PLACE_KEYS)
            if not pl.get("name"):
                self.err("missing-name", plid, tr("{id}: missing name", id=plid))
            if pl.get("parish") and pl["parish"] not in self.places:
                self.err("unknown-place", plid, tr("{ctx}: unknown place {id}", ctx=f"{plid}.parish", id=pl["parish"]))
            self._enum(f"{plid}.geneteka_region", pl.get("geneteka_region"), REGIONS)
            self._enum(f"{plid}.partition", pl.get("partition"), PARTITIONS)
            c = pl.get("coords")
            if c is not None and not valid_coords(c):
                self.err("bad-coords", plid, tr("{ctx}: expected [latitude, longitude]", ctx=f"{plid}.coords"))
            elif c is not None and (pl.get("country") or "PL") == "PL" and not (45 <= c[0] <= 58 and 12 <= c[1] <= 30) \
                    and 45 <= c[1] <= 58 and 12 <= c[0] <= 30:
                self.warn("suspicious-coords", plid, tr("{ctx}: {coords} lies outside Poland — latitude and longitude swapped?",
                                                        ctx=f"{plid}.coords", coords=c))
            for i, a in enumerate(self._list(plid, pl, "admin"), 1):
                if not isinstance(a, dict) or "value" not in a:
                    self.err("bad-admin", plid, tr("{ctx}: expected {{period: …, value: …}}", ctx=f"{plid}.admin[{i}]"))
            for k in ("aliases", "records"):
                self._list(plid, pl, k)
        for sid, s in self.sources.items():
            self._keys(sid, s, SOURCE_KEYS)
            if not s.get("title"):
                self.err("missing-title", sid, tr("{id}: missing title", id=sid))
            self._enum(f"{sid}.type", s.get("type"), SOURCE_TYPES)
            self._enum(f"{sid}.quality", s.get("quality"), SOURCE_QUALITY)
            self._enum(f"{sid}.classification", s.get("classification"), SOURCE_CLASSES)
            self._enum(f"{sid}.information", s.get("information"), INFORMATION)
            self._enum(f"{sid}.evidence", s.get("evidence"), EVIDENCE)
            if s.get("same_record_as") is not None and not isinstance(s["same_record_as"], list):
                self.err("not-a-list", sid, tr("{ctx}.{key}: expected a list [..]", ctx=sid, key="same_record_as"))
            for key in ("same_record_as", "derived_from"):
                self._source_refs(f"{sid}.{key}", s.get(key), use=False)
            if s.get("parish") and s["parish"] not in self.places:
                self.err("unknown-place", sid, tr("{ctx}: unknown place {id}", ctx=f"{sid}.parish", id=s["parish"]))
            for path in self.source_files(sid):
                if not (self.root / path).is_file():
                    self.err("missing-scan-file", sid, tr("{ctx}: file {path} does not exist in the workspace",
                                                          ctx=f"{sid}.file", path=path))
            langs = s.get("language")
            for code in (langs if isinstance(langs, list) else [langs] if langs else []):
                if code not in LANGUAGES:
                    self.warn("unknown-language", sid, tr("{ctx}: unknown language code {value!r} (use ISO 639-1, e.g. pl, la, de, ru)",
                                                          ctx=f"{sid}.language", value=code))
        for sid in self.sources.keys() - self._used_sources:
            self.warn("unused-source", sid, tr("{id}: source is not attached to any fact", id=sid))
        if not self.errors:
            self._check_cycles()
            self._check_chronology()

    def _check_cycles(self) -> None:
        for pid in self.persons:
            seen, stack = set(), list(self.parents(pid))
            while stack:
                a = stack.pop()
                if a == pid:
                    self.err("cycle", pid, tr("{id}: is their own ancestor (cycle in family relations)", id=pid))
                    break
                if a not in seen:
                    seen.add(a)
                    stack.extend(self.parents(a))

    def _chrono(self, record: str, facts: tuple[str, ...], text: str) -> None:
        """A chronology warning; `facts` are the scores it lowers (birth, death, link, marriage)."""
        self.warn("chronology", record, text)
        self.chronology.setdefault(record, []).extend((fact, text) for fact in facts)

    def _check_chronology(self) -> None:
        for pid, p in self.persons.items():
            b, d = self.birth_year(p), self.death_year(p)
            if b and d and d < b:
                self._chrono(pid, ("birth", "death"), tr("{id} {name}: death ({death}) before birth ({birth})", id=pid, name=self.name(pid), death=d, birth=b))
            elif b and d and d - b > 105:
                self._chrono(pid, ("birth", "death"), tr("{id} {name}: age {age} years — check the dates", id=pid, name=self.name(pid), age=d - b))
            bd, cd = self.date(p, "birth"), self.date(p, "baptism")
            if bd and cd and bd.kind == cd.kind == "exact" and sort_key(cd.a) < sort_key(bd.a):
                self._chrono(pid, ("birth",), tr("{id} {name}: baptism before birth", id=pid, name=self.name(pid)))
        for fid, f in self.families.items():
            md = self.date(f, "marriage")
            for role, min_age in (("husband", 16), ("wife", 14)):
                p = self.persons.get(f.get(role))
                if not p or not md or not md.precise:
                    continue
                b, d = self.birth_year(p), self.death_year(p)
                if b and md.year - b < min_age:
                    self._chrono(fid, ("marriage",), tr("{id}: {name} is {age} years old at the marriage", id=fid, name=self.name(f[role]), age=md.year - b))
                if d and md.year > d:
                    self._chrono(fid, ("marriage",), tr("{id}: marriage ({year}) after the death of {name} ({death})",
                                                        id=fid, year=md.year, name=self.name(f[role]), death=d))
            for c in f.get("children") or []:
                cb = self.birth_year(self.persons[c])
                if not cb:
                    continue
                for role, lo, hi, slack in (("wife", 13, 52, 0), ("husband", 15, 80, 1)):
                    par = self.persons.get(f.get(role))
                    if not par:
                        continue
                    mother = role == "wife"
                    pb, pd = self.birth_year(par), self.death_year(par)
                    if pb and not lo <= cb - pb <= hi:
                        self._chrono(c, ("link",), tr("{id} {name}: mother's age at the birth = {age} years ({family})" if mother
                                                      else "{id} {name}: father's age at the birth = {age} years ({family})",
                                                      id=c, name=self.name(c), age=cb - pb, family=fid))
                    if pd and cb > pd + slack:
                        self._chrono(c, ("link",), tr("{id} {name}: birth ({birth}) after the mother's death ({death})" if mother
                                                      else "{id} {name}: birth ({birth}) after the father's death ({death})",
                                                      id=c, name=self.name(c), birth=cb, death=pd))

    def _check_living(self) -> None:
        for pid, p in self.persons.items():
            if p.get("living") is None and not (p.get("death") or p.get("burial")) and not self.birth_window(pid) \
                    and not any(n.bit_length() >= 4 for n in self.kekule.get(pid, [])):
                self.warn("assumed-living", pid, tr("{id} {name}: no dates and no living field — treated as living "
                                                    "(set living: false if deceased)", id=pid, name=self.name(pid)))

    # ---- relations

    def parents_family(self, pid: str) -> dict | None:
        fids = self.child_of.get(pid)
        return self.families[fids[0]] if fids else None

    def parents(self, pid: str) -> list[str]:
        f = self.parents_family(pid)
        return [x for x in (f.get("husband"), f.get("wife")) if x] if f else []

    def _kekule(self) -> dict[str, list[int]]:
        nums: dict[str, list[int]] = {}
        pb = self.project.get("proband")
        if pb not in self.persons:
            return nums
        queue = [(pb, 1)]
        while queue:
            pid, n = queue.pop(0)
            if n.bit_length() > 40:
                continue
            nums.setdefault(pid, []).append(n)
            f = self.parents_family(pid)
            if f and f.get("husband") in self.persons:
                queue.append((f["husband"], 2 * n))
            if f and f.get("wife") in self.persons:
                queue.append((f["wife"], 2 * n + 1))
        return nums

    def geo(self, living: bool = False) -> Geo:
        """Geography of the tree (cached); living=False leaves living persons out."""
        if living not in self._geo:
            self._geo[living] = Geo(self, living=living)
        return self._geo[living]

    def ancestral_families(self) -> list[str]:
        fids = {self.child_of[pid][0] for pid in self.kekule if self.child_of.get(pid)}
        return sorted(fids, key=lambda fid: min(min(self.kekule.get(c, [10**12])) for c in self.families[fid].get("children") or []))

    # ---- reading facts

    @staticmethod
    def ev(rec: dict, key: str) -> dict:
        v = rec.get(key)
        return v if isinstance(v, dict) else {}

    def date(self, rec: dict, key: str) -> Date | None:
        return safe_date(self.ev(rec, key).get("date"))

    def has_sources(self, rec: dict, key: str) -> bool:
        return bool(self.ev(rec, key).get("sources"))

    def birth_year(self, p: dict) -> int | None:
        for key in ("birth", "baptism"):
            d = self.date(p, key)
            if d and d.precise:
                return d.year
        return None

    def death_year(self, p: dict) -> int | None:
        for key in ("death", "burial"):
            d = self.date(p, key)
            if d and d.precise:
                return d.year
        return None

    def living(self, pid: str) -> bool:
        p = self.persons[pid]
        if p.get("living") is not None:
            return bool(p["living"])
        if p.get("death") or p.get("burial"):
            return False
        w = self.birth_window(pid)
        if w and (w.hi or w.lo):
            return (w.hi or w.lo) > TODAY.year - 100
        return not any(n.bit_length() >= 4 for n in self.kekule.get(pid, []))

    # ---- descriptions

    def name(self, pid: str | None) -> str:
        p = self.persons.get(pid or "")
        if not p:
            return "?"
        given, sur = p.get("given") or "?", p.get("surname")
        married = p.get("married_surnames") or []
        if married:
            return f"{given} {married[-1]}" + (" " + tr("née {surname}", surname=sur) if sur else "")
        return f"{given} {sur or '?'}"

    def place_name(self, plid: str | None) -> str:
        pl = self.places.get(plid or "")
        return pl["name"] if pl else ""

    def parish_of(self, plid: str | None) -> dict | None:
        pl = self.places.get(plid or "")
        if not pl:
            return None
        if place_kind(pl) == "parish":
            return pl
        return self.places.get(pl.get("parish") or "")

    def region_of(self, plid: str) -> str | None:
        pl = self.places.get(plid) or {}
        return pl.get("geneteka_region") or (self.parish_of(plid) or {}).get("geneteka_region")

    def place_full(self, plid: str | None) -> str:
        pl = self.places.get(plid or "")
        if not pl:
            return ""
        par = self.parish_of(plid)
        out = pl["name"]
        if par and par is not pl:
            out += " (" + tr("parish {name}", name=par["name"]) + ")"
        return out + (f", {pl['today']}" if pl.get("today") else "")

    def parish_desc(self, plid: str) -> str:
        pl, par = self.places[plid], self.parish_of(plid)
        if not par:
            return tr("{place} (parish unknown)", place=pl["name"])
        denom = f" ({par['denomination']})" if par.get("denomination") else ""
        if par is pl:
            return tr("parish {name}{denomination}", name=par["name"], denomination=denom)
        return tr("{place} → parish {name}{denomination}", place=pl["name"], name=par["name"], denomination=denom)

    def event_text(self, ev: dict) -> str:
        d = safe_date(ev.get("date"))
        return " ".join(x for x in (d.text() if d else "", self.place_name(ev.get("place"))) if x)

    def life_lines(self, p: dict) -> list[str]:
        out = []
        if self.ev(p, "birth"):
            out.append("* " + (self.event_text(self.ev(p, "birth")) or "?"))
        elif self.ev(p, "baptism"):
            out.append(tr("bapt. {event}", event=self.event_text(self.ev(p, "baptism")) or "?"))
        if self.ev(p, "death"):
            out.append("† " + (self.event_text(self.ev(p, "death")) or "?"))
        elif self.ev(p, "burial"):
            out.append(tr("bur. {event}", event=self.event_text(self.ev(p, "burial")) or "?"))
        return out

    # ---- estimating dates

    def birth_window(self, pid: str) -> Window | None:
        p = self.persons[pid]
        female = p.get("sex") == "F"
        cons: list[tuple[int | None, int | None, str]] = []

        def add(bounds, lo_off, hi_off, basis):
            lo, hi = bounds
            cons.append((None if lo is None else lo + lo_off, None if hi is None else hi + hi_off, basis))

        if d := self.date(p, "birth"):
            add(d.bounds, 0, 0, tr("date of birth"))
        if d := self.date(p, "baptism"):
            add(d.bounds, -1, 0, tr("date of baptism"))
        death = self.date(p, "death") or self.date(p, "burial")
        age = self.ev(p, "death").get("age")
        if death and isinstance(age, int):
            add(death.bounds, -age - 2, -age + 1, tr("age in the death record"))
        elif death:
            add(death.bounds, -105, 0, tr("date of death"))
        child_years = []
        for fid in self.spouse_in.get(pid, []):
            f = self.families[fid]
            md = self.date(f, "marriage")
            age = self.ev(f, "marriage").get("husband_age" if f.get("husband") == pid else "wife_age")
            if md and isinstance(age, int):
                add(md.bounds, -age - 2, -age + 1, tr("age in the marriage record"))
            elif md:
                add(md.bounds, -70, -14, tr("date of marriage"))
            child_years += [y for c in f.get("children") or [] if (y := self.birth_year(self.persons[c]))]
        if child_years:
            cons.append((max(child_years) - (50 if female else 75), min(child_years) - (13 if female else 15), tr("births of children")))
        if f := self.parents_family(pid):
            if md := self.date(f, "marriage"):
                add(md.bounds, -2, 30, tr("parents' marriage"))
            for role, lo, hi, basis in (("wife", 13, 52, tr("mother's age")), ("husband", 15, 80, tr("father's age"))):
                par = self.persons.get(f.get(role))
                if par and (y := self.birth_year(par)):
                    cons.append((y + lo, y + hi, basis))
        if not cons:
            return None
        los = [c[0] for c in cons if c[0] is not None]
        his = [c[1] for c in cons if c[1] is not None]
        lo, hi = (max(los) if los else None), (min(min(his), TODAY.year) if his else None)
        if lo is not None and hi is not None and lo > hi:
            return Window(cons[0][0], cons[0][1], [cons[0][2]], conflict=True)
        return Window(lo, hi, list(dict.fromkeys(c[2] for c in cons)))

    def death_range(self, pid: str) -> tuple[int, int] | None:
        p = self.persons[pid]
        seen = [y for y in [self.birth_year(p)] if y]
        for e in p.get("events") or []:
            if isinstance(e, dict) and (d := safe_date(e.get("date"))):
                seen.append(d.bounds[1] or d.year)
        for fid in self.spouse_in.get(pid, []):
            f = self.families[fid]
            if md := self.date(f, "marriage"):
                seen.append(md.year)
            kids = [y for c in f.get("children") or [] if (y := self.birth_year(self.persons[c]))]
            if kids:
                seen.append(max(kids) - (1 if p.get("sex") == "M" else 0))
        w = self.birth_window(pid)
        lo = max(seen) if seen else (w.lo + 20 if w and w.lo else None)
        hi = w.lo + 100 if w and w.lo else (lo + 60 if lo else None)
        if lo is None or hi is None:
            return None
        return lo, min(max(hi, lo), TODAY.year)

    # ---- research hints

    def search_places(self, pid: str, purpose: str) -> list[tuple[str, str]]:
        p = self.persons[pid]
        found: list[tuple[str, str]] = []

        def add(plid, label):
            if plid in self.places:
                found.append((plid, label))

        if purpose == "birth":
            keyed = (("birth", tr("place of birth")), ("baptism", tr("place of baptism")))
        else:
            keyed = (("death", tr("place of death")), ("burial", tr("place of burial")))
        for key, label in keyed:
            add(self.ev(p, key).get("place"), label)
        events = [e for e in p.get("events") or [] if isinstance(e, dict) and e.get("type") in ("residence", "census")]
        for e in events if purpose == "birth" else reversed(events):
            add(e.get("place"), tr("place of residence"))
        for fid in self.spouse_in.get(pid, []):
            f = self.families[fid]
            bride = p.get("sex") == "F" and purpose == "birth"
            add(self.ev(f, "marriage").get("place"),
                tr("place of marriage") + (" " + tr("(marriages usually took place in the bride's parish)") if bride else ""))
            kids = [self.persons[c] for c in f.get("children") or []]
            for k in kids if purpose == "birth" else reversed(kids):
                add(self.ev(k, "birth").get("place") or self.ev(k, "baptism").get("place"), tr("place of birth of the children"))
        if purpose == "birth" and (f := self.parents_family(pid)):
            add(self.ev(f, "marriage").get("place"), tr("place of the parents' marriage"))
        if purpose == "death":
            add(self.ev(p, "birth").get("place"), tr("place of birth"))
        seen, out = set(), []
        for plid, label in found:
            key = (self.parish_of(plid) or {}).get("id", plid)
            if key not in seen:
                seen.add(key)
                out.append((plid, label))
        return out

    def gt_links(self, kind: str, places, rng, **query) -> list[tuple[str, str]]:
        if not query.get("surname") or not rng:
            return []
        who = " ".join(x for x in (query.get("surname"), query.get("given")) if x)
        if query.get("surname2") or query.get("given2"):
            who += " + " + " ".join(x for x in (query.get("surname2"), query.get("given2")) if x)
        links, seen = [], set()
        for plid, _ in places:
            region = self.region_of(plid)
            if region and region not in seen:
                seen.add(region)
                links.append((tr('Geneteka: {kind} "{who}" {start}–{end}, {region}', kind=kind_label(kind), who=who,
                                 start=rng[0], end=rng[1], region=REGIONS[region]),
                              page_url(kind=kind, w=region, lo=rng[0], hi=rng[1], **query)))
        return links

    def _where(self, places, fallback: str) -> list[str]:
        out = [tr("Search: {where} — {why}", where=self.parish_desc(plid), why=label) for plid, label in places[:3]] or [fallback]
        if places and not any(self.region_of(plid) for plid, _ in places):
            out.append(tr("Fill in geneteka_region of the place in places.yaml to get ready-made Geneteka links."))
        return out

    def person_hints(self, pid: str) -> list[Hint]:
        p = self.persons[pid]
        if self.living(pid):
            if len(self.parents(pid)) < 2:
                return [Hint(1, tr("Parents of a living person are missing — ask the family or order a full copy of the birth "
                                   "certificate from the civil registry office (it names the parents). Living persons are "
                                   "never searched online."))]
            return []
        hints = [Hint(1, tr("Task: {task}", task=t)) for t in p.get("todo") or []]
        given = (p.get("given") or "").split()[:1]
        given = given[0] if given else ""
        if p.get("confidence") == "hypothesis":
            hints.append(Hint(1, tr("This person / link is a hypothesis — confirm it with a primary source (a scan of the record).")))
        elif p.get("confidence") == "probable":
            hints.append(Hint(2, tr("The link is probable — worth confirming with a second source.")))

        fam = self.parents_family(pid)
        missing = [role for role in ("husband", "wife") if not fam or not fam.get(role)]
        if missing or not (self.has_sources(p, "birth") or self.has_sources(p, "baptism")):
            if len(missing) == 2:
                text, level = tr("End of line: no parents — find the birth/baptism record (it names the parents, usually "
                                 "also the mother's maiden name)."), 1
            elif missing:
                text, level = tr("Father missing — the birth/baptism record will name the missing parent." if missing[0] == "husband"
                                 else "Mother missing — the birth/baptism record will name the missing parent."), 1
            else:
                text, level = tr("Birth without a source — confirm it with a birth/baptism record."), 2
            w = self.birth_window(pid)
            places = self.search_places(pid, "birth")
            details = self._where(places, tr("Place unknown — marriage and death records or family accounts give it."))
            details += self.geo().hint_lines(pid, "birth")
            if w:
                details.append(tr("Estimated year of birth: {years} (evidence: {basis})", years=w.text(), basis=", ".join(w.basis))
                               + (" " + tr("— WARNING: the evidence is contradictory, check the dates") if w.conflict else ""))
            rng = search_range(w.lo, w.hi) if w else None
            if rng and rng[1] >= TODAY.year - 100:
                details.append(tr("Birth records younger than 100 years are kept by the civil registry office (USC), not "
                                  "the archive — request a full copy."))
            if missing and self.spouse_in.get(pid) and not any(self.has_sources(self.families[f], "marriage") for f in self.spouse_in[pid]):
                details.append(tr("Often faster via the marriage record: it usually names the parents of the couple (in "
                                  "Congress Poland from 1808 also age and place of birth)."))
            hints.append(Hint(level, text, details, self.gt_links("B", places, rng, surname=p.get("surname"), given=given)))

        if p.get("sex") == "F" and not p.get("surname"):
            hints.append(Hint(1 if missing else 2, tr("Maiden name unknown — the marriage record, the children's birth "
                                                      "records and the death record give it.")))

        if not (self.has_sources(p, "death") or self.has_sources(p, "burial")):
            d = self.date(p, "death") or self.date(p, "burial")
            rng = search_range(*d.bounds) if d else self.death_range(pid)
            text = (tr("Death without a source — confirm it with a death record.") if d
                    else tr("No death record (it gives the age, often the parents and the spouse)."))
            places = self.search_places(pid, "death")
            details = self._where(places, tr("Place unknown — search the parish of the last residence (e.g. where the "
                                             "youngest child was born)."))
            details += self.geo().hint_lines(pid, "death")
            if rng:
                details.append(tr("Years to search: {start}–{end}", start=rng[0], end=rng[1]))
                if rng[1] >= TODAY.year - 80:
                    details.append(tr("Death records younger than 80 years are kept by the civil registry office (USC)."))
            surname = (p.get("married_surnames") or [None])[-1] or p.get("surname")
            if p.get("married_surnames"):
                details.append(tr("Women usually appear in death records under the husband's surname (e.g. "
                                  "\"Kowalska née Nowak\")."))
            hints.append(Hint(2, text, details, self.gt_links("D", places, rng, surname=surname, given=given)))

        unsourced = sorted({event_type_label(e.get("type")) for e in p.get("events") or [] if isinstance(e, dict) and not e.get("sources")})
        if unsourced:
            hints.append(Hint(3, tr("Facts without a source: {facts}", facts=", ".join(unsourced))))
        return sorted(hints, key=lambda h: h.level)

    def family_hints(self, fid: str) -> list[Hint]:
        f = self.families[fid]
        hid, wid = f.get("husband"), f.get("wife")
        if any(self.living(x) for x in (hid, wid) if x):
            return []
        h, w = self.persons.get(hid or ""), self.persons.get(wid or "")
        hints = [Hint(1, tr("Task: {task}", task=t)) for t in f.get("todo") or []]
        if f.get("confidence") == "hypothesis":
            hints.append(Hint(1, tr("The union is a hypothesis — confirm it with the marriage record or the children's birth records.")))
        if not h or not w:
            hints.append(Hint(2, tr("Husband unknown — the children's birth records name both parents." if not h
                                    else "Wife unknown — the children's birth records name both parents.")))
        if not self.has_sources(f, "marriage"):
            md = self.date(f, "marriage")
            kids = sorted(y for c in f.get("children") or [] if (y := self.birth_year(self.persons[c])))
            if md:
                rng = search_range(*md.bounds)
            elif kids:
                rng = (kids[0] - 6, kids[0] + 1)
            else:
                wins = [win for x in (hid, wid) if x and (win := self.birth_window(x)) and win.lo]
                rng = search_range(max(x.lo for x in wins) + 16, max(x.lo for x in wins) + 40) if wins else None
            if self.ev(f, "marriage").get("place") in self.places:
                places = [(self.ev(f, "marriage")["place"], tr("place of marriage"))]
            else:
                places = [(pl, tr("bride: {label}", label=lab)) for pl, lab in (self.search_places(wid, "birth") if w else [])]
                for c in f.get("children") or []:
                    k = self.persons[c]
                    if (pl := self.ev(k, "birth").get("place") or self.ev(k, "baptism").get("place")) in self.places:
                        places.append((pl, tr("place of birth of the first child")))
                        break
                places += [(pl, tr("groom: {label}", label=lab)) for pl, lab in (self.search_places(hid, "birth") if h else [])]
                seen, uniq = set(), []
                for pl, lab in places:
                    key = (self.parish_of(pl) or {}).get("id", pl)
                    if key not in seen:
                        seen.add(key)
                        uniq.append((pl, lab))
                places = uniq
            details = self._where(places, tr("Place unknown — marriages usually took place in the bride's parish."))
            if rng:
                details.append(tr("Years to search: {start}–{end}", start=rng[0], end=rng[1]))
                if rng[1] >= TODAY.year - 80:
                    details.append(tr("Marriage records younger than 80 years are kept by the civil registry office (USC)."))
            details.append(tr("The marriage record usually names the parents of the couple (in Congress Poland from 1808 "
                              "also age and place of birth) — it lets you jump a generation."))
            text = tr("Marriage without a source — find the marriage record.") if md else tr("No marriage record.")
            query = dict(surname=(h or {}).get("surname") or (w or {}).get("surname"),
                         surname2=(w or {}).get("surname") if h else "", pair=bool(h and w and w.get("surname")))
            hints.append(Hint(2, text, details, self.gt_links("S", places, rng, **query)))
        return sorted(hints, key=lambda x: x.level)

    def place_gaps(self) -> list[tuple[str, list[str]]]:
        out = []
        for plid, pl in self.places.items():
            missing = []
            kind = place_kind(pl)
            if kind not in NO_PARISH_NEEDED and not pl.get("parish"):
                missing.append(tr("parish (parish)"))
            if pl.get("country", "PL") in ("PL", "UA", "BY", "LT") and not self.region_of(plid):
                missing.append(tr("Geneteka region (geneteka_region)"))
            if pl.get("country", "PL") == "PL" and not pl.get("partition") and kind != "region":
                missing.append(tr("partition (partition)"))
            if not pl.get("coords"):
                missing.append(tr("coordinates (coords; the map uses the parish's for now)")
                               if valid_coords((self.parish_of(plid) or {}).get("coords")) else tr("coordinates (coords)"))
            if missing:
                out.append((plid, missing))
        return out

    # ---- for the CLI

    def next_ids(self) -> dict[str, str]:
        out = {}
        for kind, prefix, recs in (("person", "I", self.persons), ("family", "F", self.families),
                                   ("place", "P", self.places), ("source", "S", self.sources)):
            n = max((int(r[1:]) for r in recs if r[1:].isdigit()), default=0) + 1
            out[kind] = f"{prefix}{n:04d}"
        return out

    def find(self, query: str) -> list[str]:
        tokens = fold(query).split()
        out = []
        for pid, p in self.persons.items():
            hay = fold(" ".join([p.get("given") or "", p.get("surname") or ""] + (p.get("married_surnames") or []) + (p.get("variants") or [])))
            if all(t in hay for t in tokens):
                out.append(pid)
        return out
