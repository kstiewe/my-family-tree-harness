# Sources: guides to services and regions

One guide per service (or family of services) and one per region. Agents read the relevant guide
before using a service and **add to it** what they learn — this is how the toolkit grows. Code
helpers live next to the guide (`*.js` for the browser's JavaScript console, Python in `familytree/`).

| Guide | Covers |
|---|---|
| [overview.md](overview.md) | all services at a glance: indexes, scans, gazetteers, supplementary sources, abroad |
| [geneteka.md](geneteka.md) | Geneteka (PTG): national index of births, marriages, deaths; `scripts/geneteka.py` |
| [pomgenbaza.md](pomgenbaza.md) | PomGenBaza (Pomeranian Genealogical Society): parish and civil books of Pomerania |
| [szukajwarchiwach.md](szukajwarchiwach.md) | Szukaj w Archiwach: scans from the Polish state archives |
| [genealogiawarchiwach.md](genealogiawarchiwach.md) | Genealogia w Archiwach: scans and indexes of the Kuyavian-Pomeranian state archives |
| [german-sources.md](german-sources.md) | CompGen (Verlustlisten, address books, GEDBAS), German gazetteers |
| [graves.md](graves.md) | grave databases (Grobonet, eCmentarze …) |
| [gazetteers.md](gazetteers.md) | finding villages and their parishes |
| [regions/pomerania.md](regions/pomerania.md) | Pomerania / former West Prussia |

## Writing a guide

- **Only general knowledge.** The mechanics of the service, URL patterns, form fields, how to read
  the results, coverage, traps. Examples use the fictional sample family (Kowalski, Nowak,
  Przykładowo, Wzorcowo …) or placeholders (`<parish id>`), never real research subjects.
- Family-specific findings — which IDs you used, where a record was found, open leads — go to the
  private workspace (`research/`).
- Mark what was verified and when ("checked 2026-11"); services change.
- Keep a guide skimmable: what it is, coverage, how to search, how to read results, traps, helpers.
- `python3 scripts/guard.py check < guide.md` before committing.

## Writing a region guide

Copy the structure of [regions/pomerania.md](regions/pomerania.md): history of administration
(which partition, provinces, districts, name changes), record types and languages by period, where
the books are, which indexes cover the region, gazetteers, typical traps.
