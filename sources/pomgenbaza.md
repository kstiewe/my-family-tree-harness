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

**Which tab a filter applies to** (checked 2026-11): `fatherFirstName`, `motherFirstName` and
`motherMaidenName` filter only the births tab; `spouseFirstName` and `spouseLastName` only the marriages
tab. The other tabs then show the unfiltered results for the surname — read only the tab the filter
applies to (`pgQ` in the helper takes `types` for that, and a regex to keep only matching rows).

## Techniques that work

- **All children of a couple in one query**: prefix of the father's surname + prefix of the mother's
  maiden name (`motherMaidenName`), no given name, over a range of years
  (`pgSearch('', 'Kowal', 1880, 1912, {motherMaidenName: 'Nowa'})`). The mother's maiden name alone
  returns far too much.
- **Children of a daughter**: her husband's surname + her maiden name as `motherMaidenName`.
- **Backwards to the parents' marriage**: surname + `spouseLastName` (both prefixes) finds the
  marriage of the parents once the children have given you the mother's maiden name.
- **A husband from the wife's given name**: when the family remembers only "Teofila Kowalska, mother of
  Jan", the surname + `spouseFirstName` ("Kowal" + "Teof"; Latin books also "Theoph") lists the marriages
  of Kowalski men to a Teofila. A rare given name often leaves a single marriage — a strong candidate for the
  parents, to be checked against the parish and the years.
- **Siblings by the father's given name**: surname + `fatherFirstName` collects the children of one man
  across parishes when the mother's maiden name is still unknown; the result then gives the maiden name.
- **Short prefixes catch variants** ("Kowal" → Kowalski/Kowalsky/Kowalska); clerks of civil offices
  often misspelled Polish names.
- **Language of names**: Catholic books are in Latin (Sophia, Joannes, Maximilianus), the Standesamt
  in German (Sophie, Johann, Max). A search for "Zof" misses "Sophia" — search without a given name
  or in both forms.
- **One event after 1874 usually has two entries**, in the parish and in the Standesamt, with different
  record numbers. The Standesamt entry leads to a scan (see the "Księga" column).
- **A record missing under the known spelling**: query the **given name alone** (no surname) in the civil
  office and the parish of the event, over two or three years. The short list of every "Jan" who died there
  shows the person under a spelling no prefix would have guessed: clerks of the 1920s–1930s often wrote
  German-looking surnames the Polish way, and the reverse happened in German records (Kowalski / Kowalsky).
  Then search the new spelling everywhere — it also finds relatives indexed under it.
- **Survey a rare surname office by office**: run the same prefix with `extra.parish` set to each civil
  office and parish of the district in turn. A whole-database query shows only 50 rows per tab, so a record
  from the right office can stay hidden under hits from elsewhere. Keep the office ids of the district in
  the workspace.
- **The parish of the birthplace, not of the wedding**: a baptism missing from the index is often a coverage
  gap. Find the parish of the village independently — the [Meyers Gazetteer](german-sources.md) gives the
  Catholic and the Protestant parish — and check that parish's coverage: births may be indexed only from a
  later year than marriages and deaths. A wedding was usually held in the bride's parish.
- **Coverage of many parishes at once**: `fetch` each parish page in the console and read its `table tr`
  rows — the last three cells of a row are the years indexed for births, marriages and deaths.

## The "Księga" (book) column

- `10/XXXX/0/YY` — the State Archive in Gdańsk (fonds / series / unit): civil registry books, often with
  scans on [Szukaj w Archiwach](szukajwarchiwach.md).
- `ADP/W…` — the Diocesan Archive in Pelplin; no scans online.
- A plain number (e.g. `831`) — a book kept in the parish; its PomGenBaza page gives no archive signature.
- "Nr zdjęcia" is PTG's photo number; on Szukaj w Archiwach it is **not** the scan number. Many of these
  photos — also of years and offices with no scans on Szukaj w Archiwach — can be viewed on Metryki GenBaza
  with a free account (see [metryki-genbaza.md](metryki-genbaza.md)).

## Cemetery indexes

`/pomgenbaza/indeksy-cmentarzy-i-pomnikow/` — about 190 cemeteries (2026-11); many rural cemeteries
are not included.
