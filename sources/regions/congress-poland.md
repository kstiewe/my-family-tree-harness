# Congress Poland (Russian partition)

The Kingdom of Poland of 1815–1915 ("Congress Poland"): today central and eastern Poland, among them the
regions around Kalisz, Sieradz, Łódź, Warsaw, Lublin and Kielce. Services: [Geneteka](../geneteka.md)
(regions such as `15wp` wielkopolskie for the former Kalisz governorate, `05ld` łódzkie, `07mz` mazowieckie),
[Szukaj w Archiwach](../szukajwarchiwach.md), Skanoteka (below). See also docs/research-guide.md, "What survived where".

## Administration over time

| Period | Unit | What it means for records |
|---|---|---|
| 1807–1815 | Duchy of Warsaw | civil-status records kept by parish priests from 1808 (Napoleonic model), in Polish |
| 1815–1867 | Kingdom of Poland, voivodeships, then governorates (gubernie) | same system; records in Polish |
| 1867–1915 | governorates (gubernie), counties (powiaty), communes (gminy) | records in Russian from about 1868 |
| 1915–1918 | German / Austrian occupation | Polish again in many parishes |
| from 1918 | Poland | parish civil-status records in Polish until 1945; then secular civil registry offices (USC) |

A village's parish and commune are in the Słownik geograficzny (see [gazetteers.md](../gazetteers.md)); the
commune of about 1880 often differs from today's.

## Records

- **One book per parish and year**, usually births, marriages and deaths in one volume, each section with its
  own numbering. The second copy (duplicate) went to the court and is now in a state archive — that is the copy
  you see online. Annexes to marriage records ("dowody do akt małżeństw": birth certificates, permissions) are
  separate units, rarely scanned.
- **Narrative form**: "Działo się we wsi Przykładowo…" / "Состоялось въ деревнѣ…". The marriage record gives
  each party's age, place of birth *with its parish*, residence and parents with the mother's maiden name — the
  key to the previous generation. A birth record gives the father's age and occupation and the mother's maiden
  name and age, so it dates the parents too.
- **Language**: Polish until 1867/68, Russian until about 1917 (`language: ru`). Around 1906–1907 some parishes
  switched back and forth: in one volume the January marriages may be in Polish and the September ones in
  Russian. Names of the parties are often repeated in Polish in brackets ("Войцѣхъ Ковальскій / Wojciech Kowalski /"),
  which settles the Polish spelling.
- **Two dates** in Russian records: Julian first, Gregorian second ("второго / четырнадцатаго" = 2/14). Use the
  Gregorian date and put the Julian one in `note`. Some volumes after 1905 give only one date.
- **Surname forms change**: the same man can be "Kowal" in two records and "Kowalski" in the next; women appear as
  "z Kowalskich" (genitive plural) or "урожденная Ковальская". Search both forms; feminine forms of adjectival
  surnames (Wzorcowy → Wzorcowa) are the same surname.
- **Godparents and witnesses** are often relatives (an uncle as witness, a grandmother as godmother) — record them
  for the next generation, but do not treat them as proof.

## Indexes inside the books

Each yearly section ends with an alphabetical index (alfabetyczny spis, "Списокъ / Алфавитный указатель") giving
the record number. Reading the index first is much faster than paging through the records:

- In Russian volumes the index is usually in **Russian alphabetical order** (А Б В Г Д Е Ж З И К Л М Н О П Р С Т
  У Ф Х Ц Ч Ш Щ…): Polish names starting with "Cz" (Ч) are near the end, "W" (В) near the beginning, "Ł" under
  Л. Some parishes ordered the same index by the Polish alphabet even when writing in Cyrillic — check the
  order on the page before concluding that a name is missing.
- Births index right after the births, marriages index after the marriages, deaths at the end of the volume.
  On Szukaj w Archiwach, a grid of small thumbnails of a whole volume shows the index pages (tables) at a glance.
- Record numbers in the margin, often with the village name ("№ 75. Przykładowo") — the village is also an
  identification aid.

## Where the scans are (checked 2026-11)

- **Szukaj w Archiwach**: duplicates of many parishes from the state archives (e.g. Kalisz, Łódź), typically up to
  the year that was 100 years old at the time of digitisation (often 1907–1912). Check each unit's scan count
  in the fonds list: later years may be described but have 0 scans.
- **Skanoteka (metryki.genealodzy.pl)**: PTG's scans, often the years after the end of the Szukaj w Archiwach
  scans (e.g. 1908–1923 of a parish whose state-archive scans stop in 1907). Geneteka rows link there
  (`metryki.php?op=kt&ar=<archive>&zs=<fonds>&sy=<year>&kt=<1 births | 2 marriages | 3 deaths>`). The year page
  lists files named after the record numbers they contain (`247-250.jpg`); the file page is
  `metryki.php?op=pg&id=<unit id>&sy=<year>&kt=<kind>&plik=<file>`. The image is drawn on a canvas: use the
  page's "Powiększ" button and region screenshots. The server is slow (about 10 s per page) and sometimes
  answers "504 Gateway Time-out" for hours — retry later.
- **A fonds marked "vacat … przekazany do Archiwum Państwowego w …"** on Szukaj w Archiwach: the books were moved
  to another archive; if the search finds no fonds there, they are not described online — the user has to ask
  that archive, the civil registry office of the commune or the parish.
- **Geneteka** coverage per parish varies widely; see the trap below.

## Traps

- **A Geneteka year range hides gaps**: a parish listed as "U 1671–1921" may have births indexed only up to
  about 1800 plus a few late years. Search a common surname of the region (e.g. Kowalski) over the whole range
  and count the hits per decade before concluding that a record does not exist. The gap can also sit in the middle:
  "M 1830–1880" may be 1830–1858 plus 1874–1880. Search the parish for one common given name over the range and see which
  years appear; for the missing years read the yearly marriage indexes on the scans (Szukaj w Archiwach) — the Kowalski ×
  Nowak marriage of a missing year was found that way.
- **A widow's second marriage names her late husband** with the date and village of his death ("wdową po zmarłym Janie
  Kowalskim, zmarłym we wsi Przykładowo dnia …"). That leads to his death record, often in a neighbouring parish, and the
  death record gives his parents.
- **A death reported by neighbours can name the wrong mother**: "Piotr Kowalski, son of Wawrzyniec and Dorota née Nowak" was
  in fact the husband of Dorota née Nowak. Check the parents in a death record against the deceased's own marriage before
  using them.
- **Ages drift by a year or two** between records (a woman aged 26 at her wedding in 1907 may have been born in
  late 1880) — search ±2 years.
- **Same village name in two counties**: check that the candidate village belongs to the parish named in the
  record (the Słownik geograficzny or the parish entry on Wikipedia).
- **A "birth date" may be the date of the record**: Congress-Poland birth records were written a few days after the
  birth, and a later document or a family tree often gives the day the record was drawn up ("akt spisano 11 maja",
  birth on the 9th). A date that matches the record's own date is strong evidence that it is the right record.
- **Variant spellings fall out of exact searches**: a Geneteka query with the exact-surname option misses a baptism
  indexed as "Kowal" for a later "Kowalski". Make the last pass without the exact option and read the rows.
- **Vertical margin notes** (baptism and godparents written along the margin): turn them with the helper
  `swaRotate` in [szukajwarchiwach.js](../szukajwarchiwach.js) instead of reading them sideways.
- **An unclear word in a later record** (e.g. a birthplace in an interwar civil record): compare its letters with
  words the same clerk wrote elsewhere in the record ("katolickiego", "żony", "żyjącej"; compare handwriting with handwriting,
  not with the printed words of a form). One clerk's
  "ż" may look like "r", his "m" like "n" with a short stroke; a place first read as "Wzorcońsk" can turn out to be
  "Wzorcomsk" once the letter shapes are matched — and only the second exists in the gazetteer.
