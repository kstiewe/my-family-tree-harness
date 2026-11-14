# PomGenBaza

[PomGenBaza](https://www.ptg.gda.pl/language/pl/pomgenbaza/przeszukiwanie-rejestrow-metrykalnych/)
of the Pomeranian Genealogical Society (PTG): indexes of Catholic and Protestant parish books and of
civil registry offices (Standesamt, from 1874) of Pomerania, Kashubia and the former West Prussia,
plus cemetery indexes. **Many books in it are not in Geneteka** — for this region always search
both. See also [regions/pomerania.md](regions/pomerania.md).

## The search form

Field ids: `textInput_firstName`, `textInput_lastName`, `textInput_spouseFirstName`,
`textInput_spouseLastName`, `textInput_fatherFirstName`, `textInput_motherFirstName`,
`textInput_motherMaidenName`, `textInput_yearFrom`, `textInput_yearTo`, and `selectParish`
(0 = all parishes). The default mode is "Dopasuj początek" — **prefix matching**. The modes
"fragment", "Soundex DM" and "±5 years" are for members only (🔒).

Results load by AJAX into three tabs: `divAjaxFindInner_births` / `_marriages` / `_deaths`. The
button `btn_findTab_*` shows the total, e.g. "Urodzenia (173)", but **the table shows only the first
50 rows** — narrow the years, the parish, or add the mother's maiden name. Do not rely on URLs with
parameters: fill the form and click "Szukaj". Helper: [pomgenbaza.js](pomgenbaza.js) (`pgSearch`,
verified 2026-11), which also takes `extra.parish` (sets `selectParish`).

**Parish IDs**: the `value` of `selectParish` options; the same number is the `parishId` of the parish
page. `pgParishes()` in the helper lists all of them — keep the ones you use in the workspace.

**Coverage per parish**: the parish page `https://www.ptg.gda.pl/language/pl/ptg-resource-parish/?parishId=N`
lists the address, deanery, the books with years (births/marriages/deaths separately) and where they
are kept. Coverage often has gaps (births only from a later year, a missing year): no hit in a
year outside the coverage means nothing.

## Techniques that work

- **All children of a couple in one query**: prefix of the father's surname + prefix of the mother's
  maiden name (`motherMaidenName`), no given name, over a range of years
  (`pgSearch('', 'Kowal', 1880, 1912, {motherMaidenName: 'Nowa'})`). The mother's maiden name alone
  returns far too much.
- **Children of a daughter**: her husband's surname + her maiden name as `motherMaidenName`.
- **Backwards to the parents' marriage**: surname + `spouseLastName` (both prefixes) finds the
  marriage of the parents once the children have given you the mother's maiden name.
- **Short prefixes catch variants** ("Kowal" → Kowalski/Kowalsky/Kowalska); clerks of civil offices
  often misspelled Polish names.
- **Language of names**: Catholic books are in Latin (Sophia, Joannes, Maximilianus), the Standesamt
  in German (Sophie, Johann, Max). A search for "Zof" misses "Sophia" — search without a given name
  or in both forms.
- **One event after 1874 usually has two entries**, in the parish and in the Standesamt, with different
  record numbers. The Standesamt entry leads to a scan (see the "Księga" column).

## The "Księga" (book) column

- `10/XXXX/0/YY` — the State Archive in Gdańsk (fonds / series / unit): civil registry books, often with
  scans on [Szukaj w Archiwach](szukajwarchiwach.md).
- `ADP/W…` — the Diocesan Archive in Pelplin; no scans online.
- A plain number (e.g. `831`) — a book kept in the parish; its PomGenBaza page gives no archive signature.
- "Nr zdjęcia" is PTG's photo number; on Szukaj w Archiwach it is **not** the scan number.

## Cemetery indexes

`/pomgenbaza/indeksy-cmentarzy-i-pomnikow/` — about 190 cemeteries (2026-11); many rural cemeteries
are not included.
