"""GEDCOM 5.5.1 export."""

from __future__ import annotations

import re
from pathlib import Path

from .dates import MONTHS_GED, TODAY, safe_date
from .i18n import language, tr
from .model import Tree
from .schema import event_type_label, language_names

GED_EVENT = {"birth": "BIRT", "baptism": "CHR", "death": "DEAT", "burial": "BURI"}
GED_EXTRA = {"residence": "RESI", "emigration": "EMIG", "census": "CENS", "confirmation": "CONF", "education": "EDUC"}
GED_LANG = {"pl": "Polish", "en": "English", "de": "German", "uk": "Ukrainian", "cs": "Czech", "fr": "French"}


def write_gedcom(tree: Tree, path: Path, public: bool) -> None:
    L: list[str] = []

    def add(level: int, tag: str, value="") -> None:
        text = "" if value is None else str(value)
        if not re.fullmatch(r"@[A-Z]\d+@", text):
            text = text.replace("@", "@@")
        for i, part in enumerate(text.split("\n")):
            chunks = [part[j:j + 200] for j in range(0, len(part), 200)] or [""]
            for k, chunk in enumerate(chunks):
                head = f"{level} {tag}" if i == 0 and k == 0 else f"{level + 1} {'CONC' if k else 'CONT'}"
                L.append(f"{head} {chunk}" if chunk else head)

    def place(plid: str | None, level: int) -> None:
        pl = tree.places.get(plid or "")
        if not pl:
            return
        add(level, "PLAC", ", ".join(x for x in (pl["name"], pl.get("today")) if x))
        if pl.get("coords"):
            lat, lon = pl["coords"]
            add(level + 1, "MAP")
            add(level + 2, "LATI", f"{'N' if lat >= 0 else 'S'}{abs(lat)}")
            add(level + 2, "LONG", f"{'E' if lon >= 0 else 'W'}{abs(lon)}")

    def event(level: int, tag: str, ev: dict, value: str = "", type_: str = "") -> None:
        add(level, tag, value)
        if type_:
            add(level + 1, "TYPE", type_)
        if d := safe_date(ev.get("date")):
            add(level + 1, "DATE", d.ged())
        place(ev.get("place"), level + 1)
        if isinstance(ev.get("age"), int):
            add(level + 1, "AGE", f"{ev['age']}y")
        if ev.get("cause"):
            add(level + 1, "CAUS", ev["cause"])
        if ev.get("note"):
            add(level + 1, "NOTE", ev["note"])
        for s in ev.get("sources") or []:
            add(level + 1, "SOUR", f"@{s}@")

    add(0, "HEAD")
    add(1, "SOUR", "FAMILYTREE_YAML")
    add(2, "NAME", "FamilyTree scripts/build.py")
    add(1, "DATE", f"{TODAY.day} {MONTHS_GED[TODAY.month - 1]} {TODAY.year}")
    add(1, "SUBM", "@U1@")
    add(1, "GEDC")
    add(2, "VERS", "5.5.1")
    add(2, "FORM", "LINEAGE-LINKED")
    add(1, "CHAR", "UTF-8")
    add(1, "LANG", GED_LANG.get(language(), "English"))
    add(0, "@U1@ SUBM")
    add(1, "NAME", tree.project.get("author") or tree.project.get("name") or tr("Tree author"))

    for pid, p in tree.persons.items():
        add(0, f"@{pid}@ INDI")
        hidden = public and tree.living(pid)
        if hidden:
            add(1, "NAME", tr("Living person"))
        else:
            add(1, "NAME", f"{p.get('given') or ''} /{p.get('surname') or ''}/".strip())
            if p.get("given"):
                add(2, "GIVN", p["given"])
            if p.get("surname"):
                add(2, "SURN", p["surname"])
            for ms in p.get("married_surnames") or []:
                add(1, "NAME", f"{p.get('given') or ''} /{ms}/".strip())
                add(2, "TYPE", "married")
            for v in p.get("variants") or []:
                add(1, "NAME", v)
                add(2, "TYPE", "aka")
        add(1, "SEX", p.get("sex", "U"))
        if not hidden:
            for key, tag in GED_EVENT.items():
                if tree.ev(p, key):
                    event(1, tag, tree.ev(p, key))
            for occ in p.get("occupation") or []:
                add(1, "OCCU", occ)
            if p.get("religion"):
                add(1, "RELI", p["religion"])
            for e in p.get("events") or []:
                t = e.get("type")
                if t == "occupation":
                    event(1, "OCCU", e, e.get("value") or "")
                elif t in GED_EXTRA:
                    event(1, GED_EXTRA[t], e)
                    if e.get("value"):
                        add(2, "NOTE", e["value"])
                else:
                    label = event_type_label(t)
                    event(1, "EVEN", e, e.get("value") or "", label if label != "?" else (t or tr("Other")))
            notes = [p.get("notes") or "", tr("Confidence: {value}", value=p["confidence"]) if p.get("confidence") else ""]
            if any(notes):
                add(1, "NOTE", "\n".join(n.strip() for n in notes if n))
        for fid in tree.child_of.get(pid, []):
            add(1, "FAMC", f"@{fid}@")
        for fid in tree.spouse_in.get(pid, []):
            add(1, "FAMS", f"@{fid}@")

    for fid, f in tree.families.items():
        add(0, f"@{fid}@ FAM")
        if f.get("husband"):
            add(1, "HUSB", f"@{f['husband']}@")
        if f.get("wife"):
            add(1, "WIFE", f"@{f['wife']}@")
        for c in f.get("children") or []:
            add(1, "CHIL", f"@{c}@")
        hidden = public and any(tree.living(x) for x in (f.get("husband"), f.get("wife")) if x)
        m = tree.ev(f, "marriage")
        if m and not hidden:
            event(1, "MARR", m)
            for role, tag in (("husband_age", "HUSB"), ("wife_age", "WIFE")):
                if isinstance(m.get(role), int):
                    add(2, tag)
                    add(3, "AGE", f"{m[role]}y")
        if tree.ev(f, "divorce") and not hidden:
            event(1, "DIV", tree.ev(f, "divorce"))
        if f.get("notes") and not hidden:
            add(1, "NOTE", f["notes"])

    for sid, s in tree.sources.items():
        add(0, f"@{sid}@ SOUR")
        add(1, "TITL", s.get("title", sid))
        repo = ", ".join(x for x in (s.get("repository"), s.get("signature")) if x)
        if repo:
            add(1, "PUBL", repo)
        if s.get("transcription"):
            add(1, "TEXT", s["transcription"].strip())
        langs = language_names(s.get("language"))
        note = "\n".join(x for x in (s.get("url"), s.get("notes"),
                                     tr("Language of the document: {languages}", languages=", ".join(langs)) if langs else "") if x)
        if note:
            add(1, "NOTE", note)
    add(0, "TRLR")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
