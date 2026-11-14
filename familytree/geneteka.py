"""Geneteka (geneteka.genealodzy.pl) helper: search links, parish lists, surname overview.

    python3 scripts/geneteka.py --overview Kowalski                 # regions where the surname is indexed (B/D/M)
    python3 scripts/geneteka.py --overview Kowalski --exact         # without spelling variants
    python3 scripts/geneteka.py --parishes -w 07mz --filter płońsk  # parishes of a region and indexed years
    python3 scripts/geneteka.py --link Kowalski -i Jan -t B -w 07mz --from 1840 --to 1860
    python3 scripts/geneteka.py --link Kowalski --surname2 Nowak -t M -w 07mz --pair
    python3 scripts/geneteka.py --link Kowalski -t B -w 07mz --parish Żukowo --nearby
    python3 scripts/geneteka.py --regions

Record types: B = births, M = marriages, D = deaths (Polish U/M/Z and Geneteka's B/S/D also work).
The Polish option names used earlier (--nazwisko, --imie, --od, --do, --parafie …) still work.

Geneteka renders result tables with a page script, and requests from outside a browser get
incomplete, randomised data (the service's protection). So this tool never downloads results: it
builds a link to open in a browser. HTML pages (parish list, surname overview) are fetched one
at a time, with a pause. An index entry is a lead — confirm it on the scan of the record.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

BASE = "https://geneteka.genealodzy.pl/"
USER_AGENT = "FamilyTree-research/1.0 (prywatne badania genealogiczne; pojedyncze zapytania)"
MIN_INTERVAL = 1.5  # seconds between requests

# Geneteka's region codes and labels (labels are matched when parsing the surname overview).
REGIONS = {
    "01ds": "dolnośląskie", "02kp": "kujawsko-pomorskie", "03lb": "lubelskie",
    "04ls": "lubuskie", "05ld": "łódzkie", "06mp": "małopolskie", "07mz": "mazowieckie",
    "71wa": "Warszawa", "08op": "opolskie", "09pk": "podkarpackie", "10pl": "podlaskie",
    "11pm": "pomorskie", "12sl": "śląskie", "13sk": "świętokrzyskie",
    "14wm": "warmińsko-mazurskie", "15wp": "wielkopolskie", "16zp": "zachodniopomorskie",
    "21uk": "Ukraina", "22br": "Białoruś", "23lt": "Litwa", "25po": "Pozostałe",
}
# Accepted record-type letters → Geneteka's own (B = births, S = marriages, D = deaths).
KINDS = {"B": "B", "M": "S", "D": "D", "U": "B", "Z": "D", "S": "S"}

_last_request = 0.0
_page_cache: dict[tuple, str] = {}


def kind_label(kind: str) -> str:
    from .i18n import tr
    return {"B": tr("births"), "S": tr("marriages"), "D": tr("deaths")}[kind]


def form_params(kind, w, surname="", given="", surname2="", given2="", lo=None, hi=None,
                rid=None, exact=False, pair=False, near=False, lastdays=None) -> dict:
    """Parameters of Geneteka's search form."""
    p = {
        "op": "gt", "lang": "pol", "bdm": kind, "w": w, "rid": rid or kind,
        "search_lastname": surname or "", "search_name": given or "",
        "search_lastname2": surname2 or "", "search_name2": given2 or "",
        "from_date": lo or "", "to_date": hi or "",
    }
    for flag, name in ((exact, "exac"), (pair, "pair"), (near, "near")):
        if flag:
            p[name] = 1
    if lastdays:
        p["last"] = 1
        p["lastdays"] = lastdays
    return p


def page_url(**kw) -> str:
    """Link to the results page (to open in a browser)."""
    return BASE + "index.php?" + urllib.parse.urlencode(form_params(**kw))


def fetch(params: dict) -> str:
    """Fetch one Geneteka HTML page (index.php), pausing between requests."""
    global _last_request
    key = tuple(sorted(params.items()))
    if key in _page_cache:
        return _page_cache[key]
    wait = _last_request + MIN_INTERVAL - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(BASE + "index.php?" + urllib.parse.urlencode(params), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            _page_cache[key] = resp.read().decode("utf-8", "replace")
    finally:
        _last_request = time.monotonic()
    return _page_cache[key]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def fold(text: str) -> str:
    text = text.lower().replace("ł", "l")
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


def parishes(w: str) -> list[dict]:
    """Parishes of a region with their B/M/D ids and indexed years."""
    page = fetch({"op": "gt", "lang": "pol", "bdm": "B", "w": w, "rid": "B"})
    start = page.find('id="sel_rid"')
    select = page[start:page.find("</select>", start)] if start >= 0 else ""
    out = []
    for attrs, name in re.findall(r"<option([^>]*)>([^<]*)", select):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
        if not a.get("value", "").isdigit():
            continue
        out.append({
            "name": clean(name), "years": a.get("data-years", "").strip("() "),
            "B": a.get("data-b") or None, "S": a.get("data-s") or None, "D": a.get("data-d") or None,
        })
    return out


def surname_overview(surname: str, exact: bool = False) -> list[tuple[str, int, int, int]]:
    """Number of index entries of a surname per region: (region, births, deaths, marriages)."""
    page = fetch({"op": "se", "lang": "pol", "search_lastname": surname, "search_lastname2": "",
                  "from_date": "", "to_date": "", "rpp1": "", "bdm": "", "w": "", **({"exac": 1} if exact else {})})
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [clean(re.sub(r"<[^>]+>", "", c)) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) == 4 and cells[0] in REGIONS.values():
            nums = [int(c) if c.isdigit() else 0 for c in cells[1:]]
            if any(nums):
                out.append((cells[0], *nums))
    return out


def resolve_parish(w: str, name: str, kind: str) -> tuple[str, str]:
    from .i18n import tr
    matches = [p for p in parishes(w) if fold(name) in fold(p["name"])]
    exact = [p for p in matches if fold(p["name"]) == fold(name)]
    matches = exact or matches
    if len(matches) != 1:
        names = ", ".join(p["name"] for p in matches[:20]) or tr("none")
        sys.exit(tr('Parish "{name}" in region {region}: {n} matches ({names}). Be more specific.',
                    name=name, region=REGIONS.get(w, w), n=len(matches), names=names))
    if not matches[0][kind]:
        sys.exit(tr("Parish {name}: no {kind} indexes ({years}).", name=matches[0]["name"], kind=kind_label(kind), years=matches[0]["years"]))
    return matches[0][kind], matches[0]["name"]


def main(argv: list[str] | None = None) -> int:
    from . import i18n
    from .i18n import tr
    ap = argparse.ArgumentParser(description="Geneteka helper.", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--overview", "--nazwisko", metavar="SURNAME", help="overview: number of index entries per region")
    ap.add_argument("--link", metavar="SURNAME", help="build a search link (person 1)")
    ap.add_argument("-i", "--given", "--imie", default="", help="given name (person 1)")
    ap.add_argument("--surname2", "--nazwisko2", default="", help="surname of person 2 (e.g. the bride)")
    ap.add_argument("--given2", "--imie2", default="", help="given name of person 2")
    ap.add_argument("-t", "--type", "--typ", dest="kind", default="B", choices=sorted(KINDS), help="B/M/D (default B)")
    ap.add_argument("-w", "--region", default="", help="region code (--regions)")
    ap.add_argument("--from", "--od", dest="year_from", type=int, help="from year")
    ap.add_argument("--to", "--do", dest="year_to", type=int, help="to year")
    ap.add_argument("--parish", "--parafia", help="limit to one parish (name or fragment)")
    ap.add_argument("--nearby", "--pobliskie", action="store_true", help="also parishes within 15 km (with --parish)")
    ap.add_argument("--exact", "--dokladnie", action="store_true", help="exact search (no variants)")
    ap.add_argument("--pair", "--para", action="store_true", help="search persons 1 and 2 as a couple")
    ap.add_argument("--recent", "--ostatnie", type=int, choices=[1, 3, 7, 14, 31, 60], help="only indexes added in the last N days")
    ap.add_argument("--parishes", "--parafie", action="store_true", help="list parishes of a region with indexed years")
    ap.add_argument("--filter", "--filtr", default="", help="filter parish names (with --parishes)")
    ap.add_argument("--regions", "--regiony", action="store_true", help="list region codes")
    ap.add_argument("--lang", help="output language (default: workspace project.yaml, then FAMILYTREE_LANG, then en)")
    a = ap.parse_args(argv)
    i18n.set_language(i18n.resolve(a.lang, _project_settings()))

    if a.regions:
        for code, name in REGIONS.items():
            print(f"{code}  {name}")
        return 0
    if a.parishes:
        if a.region not in REGIONS:
            ap.error("--parishes requires -w REGION_CODE")
        for p in parishes(a.region):
            if fold(a.filter) in fold(p["name"]):
                print(f"{p['name']:<40} {p['years']:<45} {tr('ids B/M/D')}: {p['B'] or '-'}/{p['S'] or '-'}/{p['D'] or '-'}")
        return 0
    if a.overview:
        rows = surname_overview(a.overview, a.exact)
        mode = tr("(exact)") if a.exact else tr("(with variants)")
        print(tr('Geneteka · "{surname}" {mode} — index entries per region:', surname=a.overview, mode=mode))
        print(f"{tr('region'):<22}{tr('born'):>8}{tr('died'):>8}{tr('marr.'):>8}")
        for name, b, d, s in rows:
            print(f"{name:<22}{b:>8}{d:>8}{s:>8}")
        if not rows:
            print(tr("none"))
        return 0
    if not a.link:
        ap.error("give --overview, --link, --parishes or --regions")
    if a.region not in REGIONS:
        ap.error("--link requires -w REGION_CODE (list: --regions)")
    kind = KINDS[a.kind]
    q = dict(surname=a.link, given=a.given, surname2=a.surname2, given2=a.given2, lo=a.year_from, hi=a.year_to,
             exact=a.exact, pair=a.pair, lastdays=a.recent)
    if a.parish:
        q["rid"], _ = resolve_parish(a.region, a.parish, kind)
        q["near"] = a.nearby
    print(page_url(kind=kind, w=a.region, **q))
    return 0


def _project_settings() -> dict:
    """project.yaml of the active workspace, if there is one (only for the language setting)."""
    try:
        from .workspace import find_workspace
        ws = find_workspace()
        return ws.project() if ws else {}
    except Exception:
        return {}


if __name__ == "__main__":
    sys.exit(main())
