# Geneteka

[geneteka.genealodzy.pl](https://geneteka.genealodzy.pl) — the national index of births, marriages
and deaths run by the Polish Genealogical Society (PTG), built by volunteers parish by parish.

## Tool

`scripts/geneteka.py` builds result links, lists parishes with their IDs and indexed years, and
gives a surname overview per region:

```bash
python3 scripts/geneteka.py --regions                              # region codes
python3 scripts/geneteka.py --parishes -w 07mz --filter wzorc      # parishes, years, ids B/M/D
python3 scripts/geneteka.py --overview Kowalski --exact            # where the surname is indexed
python3 scripts/geneteka.py --link Kowalski -i Jan -t B -w 07mz --from 1840 --to 1860
python3 scripts/geneteka.py --link Kowalski --surname2 Nowak -t M -w 07mz --pair
python3 scripts/geneteka.py --link Kowalski -t D -w 07mz --parish Wzorcowo --nearby
```

The gap report builds the same links automatically when places have `geneteka_region`.

**Read result tables in a browser.** The results API (`api/getAct.php`) gives scripts random and
repeated pages (checked 2026-11) — a protection of the service. Do not work around it.

## URL parameters

`bdm` = B/S/D (births/marriages/deaths), `w` = region code, `rid` = B/S/D for the whole region or a
parish ID, `search_lastname`, `search_name`, `search_lastname2`, `search_name2`, `from_date`,
`to_date`, `exac=1` (exact, no variants), `pair=1` (persons 1 and 2 as a couple), `near=1`
(parishes within 15 km; needs a parish ID), `last=1&lastdays=N` (added in the last N days).

**Every parish has separate IDs for B, M and D** — take them from `--parishes` (or store them in
the workspace `places.yaml` notes).

## Reading the results page

- The visible table is `table.tablesearch`; the counter `.dataTables_info` says "Pozycje od 1 do N z N".
- **"Uwagi" (remarks: age, year of birth, maiden name) are not cell text** but the `title` of an image
  `img[title^="Uwagi"]` in the last column — `innerText` of the row does not show them (checked 2026-11).
- The `title` of another icon says where the books are kept ("Miejsce przechowywania ksiąg"); the
  link to a scan is an `<a>` containing `img[src*="/s.png"]`.
- Helper: [geneteka-rows.js](geneteka-rows.js) returns rows with remarks and scan links.
- **At most 50 rows are rendered per page.** A URL asking for more (`rpp2=1000`) changes the counter ("Pozycje od 1 do
  140 z 140"), but the table still holds 50 rows. Narrow the query (a given name, fewer years) to stay under 50, or page
  with the DataTable (`.page('next').draw('page')`), before concluding that a row is missing. (Checked 2026-11.)
- **Many regions in one console call**: in a tab on geneteka.genealodzy.pl, load each result address in a hidden
  `iframe` of the same page and read its `table.tablesearch` once `.dataTables_info` has appeared and the rows have
  settled (about 3 s a page). The page then loads its data as in normal browsing; nothing calls the results API
  directly. Fifteen regions for one surname and given name take about a minute; keep one call under about 40 seconds
  (four or five regions, two queries each). (Checked 2026-11.)

## Techniques

- Without `exac=1` the search adds many spelling variants (Kowalski → Kowalewski …). For a surname
  overview use the exact mode; for finding a person, try both.
- A given name in the query also matches some foreign forms of the name.
- In births, a given name in the query matches the father as well as the child: a query "Kowalski Jan" also lists
  Jan Kowalski's daughters. Keep the rows whose child has the name. (Checked 2026-11.)
- 20th-century deaths often have the age or the year of birth in "Uwagi" (married women: the
  maiden name). Listing all deaths of a surname in a region and period, without a given name,
  finds children who died young.
- **A grandmother's maiden name from her death**: 20th-century death entries of married women often
  carry "maiden name + year of birth" in "Uwagi" (e.g. "Nowak 1878"). List the deaths of the married
  surname in the parish where the couple ended their lives; the maiden name then opens the search for
  her baptism and her parents' marriage.
- **Check the mother's age** before accepting parents found through a sibling: a mother born in 1860
  for a child of 1908 suggests the child belongs to the next generation (a son of the couple), not to
  the couple itself.
- **Children of a known father across a big surname result**: search the surname alone for a range of
  years (e.g. births "Kowalski" 1900–1926, hundreds of rows), then type the father's given name into
  the table's own "Szukaj:" box. The filter runs on the server over all columns of the result (child,
  father, mother, maiden name, parish), so "Jan" lists every child whose father — or mother's maiden
  name — contains "Jan"; a fragment of the mother's maiden name ("Nowak") or a given name works too.
  In the console: `jQuery('table.dataTable').DataTable().search('Jan').draw()`. Repeat region by
  region; it is the quickest way to rule a couple in or out nationwide (checked 2026-11).
- An oral account with an unusual maiden name ("Nowaczna or something like that"): run the overview
  with the variants; if the surname exists, the regions and parishes where it clusters are the next
  place to look — but a surname cluster alone links nobody.
- Two readings of a handwritten surname ("Kowalna" or "Kowalska"?): run the exact overview for each. A reading that
  occurs nowhere, or once, is probably a misreading; the frequent one is the likely surname — confirm it in a record or
  in the family's account.
- A rare surname: first `--overview SURNAME --exact` (regions), then the regional databases with a
  prefix, then narrow by years and parishes.
- The surname overview also hints at origins: the regions where a surname is frequent tell where a
  family with an uncertain place of origin may have come from.
- Check the indexed years with `--parishes` before concluding anything: **no hit often means the
  years are not indexed**, not that there is no record. Some parishes are indexed for a few years
  only; in some regions other databases are much richer (see `sources/regions/`).
- **Filter the result table from the URL**: `searchtable=<fragment>` (e.g. `&searchtable=Przykładowo`) filters the table
  on the server by any visible column, such as the parish; `.dataTables_info` then says "filtering from N in total", so
  hits can be counted without paging. The filter does not cover the "Uwagi" icon. `near=1` needs the ID of a parish of
  the *same* type (births, marriages or deaths) as the query.
- **What "Uwagi" holds depends on the parish**: in one parish a 20th-century death carries the full birth date or the
  maiden name, in another only the age ("8 d", "10 m"). Read two or three rows before building a search on it. In
  marriages of the German period it may hold the spouses' places of residence in German spelling ("Przykładowo
  Wzorcowo") — read it even when the parents are missing from the table.
- **A marriage after 1945, a death after about 2006 or a birth after 1926 is outside most indexes**: a zero for such
  a record says nothing about whether it exists.
- **The marriage of a couple known only from a gravestone**: when the children were born after 1926, their births are
  outside the indexes, but the parents' wedding of the 1920s–1930s may be indexed. Search marriages of the husband's
  surname and given name over the plausible years, region by region, and keep the rows whose bride has the wife's given
  name (filter the table, or the rows in a script). Then check each candidate's ages on the scan against the gravestone.
  Example: for Jan Kowalski (born 1898) and his wife Anna (born 1900), marriages "Kowalski Jan" 1916–1934 gave two
  weddings with an Anna; the scans gave grooms born in 1893 and 1905, so neither couple was theirs. (Checked 2026-11.)
- **Margin notes of a later death**: marriage records of the 1920s–1940s often carry a note added decades later, e.g.
  "zmarła dnia 12.03.1994 r. w Przykładowie, USC Przykładowo Nr 57/1994". A note that contradicts the family's dates
  (the wife buried elsewhere in 1979) excludes the candidate couple at once.
- **A probable brother as a second key**: when a couple's place of origin is unknown, but another man of the same
  surname and generation lies in the same village cemetery (Piotr Kowalski born 1901 beside Jan born 1898), search the
  births of both given names in their birth years (±1) region by region and look for the same pair of parents in both
  lists. One pair in one parish points to the place of origin; no pair proves little where the parishes are not indexed
  for those years. (Checked 2026-11.)
- In the Prussian partition the German spelling usually has many more entries than the Polish one ("Kowalsky" more
  often than "Kowalski"); exact mode treats them as different surnames, so run the overview for both.
- **A given name with no surname**: a query "Johannes" for one parish and five years lists every Johannes baptised there,
  whatever the surname spelling. A Kowalski family of Przykładowo was indexed only as "Kowalewski", which no prefix search
  had caught. In some Pomeranian parishes the "Akt" column holds the page number, not the record number.
- **A calligraphic capital Ł can be indexed as G** ("Gukowski" for Łukowski). When a known surname gives no
  hit, search the parish for the given name and the year alone and read every surname, or read the register at the end of
  the year on the scan.
