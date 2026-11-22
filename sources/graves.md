# Grave databases

Useful for 20th-century deaths, which civil registry offices hold for 80 years. Coverage is patchy:
many rural parish cemeteries are not online at all, so a negative result means little.

## Grobonet

`https://grobonet.com/wyszukiwanie?imie=<given>&nazw=<surname>&wojewodztwo=<voivodeship>&miasto=<town>` —
needs a given name or a voivodeship, and `miasto` must be a name from its own database.
**Without a given name** it needs the voivodeship and returns a list of cemeteries with the number of
hits; each cemetery is a link `/wyszukiwanie?nazw=X&wojewodztwo=Y&cmentarz=…&idcmproj=N` (persons as
"Given SURNAME YYYY-MM-DD — YYYY-MM-DD"). After about 15 quick requests the service answers "Brak
dostępu z uwagi na duże obciążenie systemu" (blocked because of load) — pause and query less.
(Verified 2026-11.)

**One cemetery by its id**: `idcmproj=N` from such a link restricts any later query to that cemetery
(`/wyszukiwanie?nazw=<surname>&wojewodztwo=<voivodeship>&idcmproj=N`), also for a surname that was not in
the first list. In a tab on grobonet.com the pages can be fetched one after another and the `main article`
elements read (one person each) — a quick way to check several family surnames in the cemetery where one
relative is known to lie. (Verified 2026-11.)

**Parish finders on a Grobonet subdomain**: many parishes run their own Grobonet site,
`https://<parish>.grobonet.com/` (found by a web search for the parish name with "grobonet"). It often
covers more than grobonet.com: several cemeteries of the parish (old and new), "Ostatnio pochowani"
(latest burials — shows how current the data are, sometimes up to the last few months), "Nekrologi" and
an advanced search `/wyszukiwarka/zaawansowana` with separate fields for the day, month and year of birth
and of death (`dur`, `mur`, `rur`, `dzg`, `mzg`, `rzg`) and a cemetery choice (`cmentarz`, the last
option = all cemeteries). What works (checked 2026-11): the simple search `/wyszukiwarka/wyniki?id=wyniki&name=<surname or given name>`
(a given name alone lists everyone of that name); a full date of birth (day + month + year); month +
year of birth or of death (e.g. everyone born 11.1946, everyone who died 06.2022). Day + month without
a year and a year alone return nothing, and the death-year field is ignored when a given name is typed.
Before reading a negative result, count the burials of the year you need month by month: a parish whose
"latest burials" reach this year may still have only a handful of entries for a year a few years back —
then that year is filled in only partly and a missing name proves nothing.

## eCmentarze

`https://www.ecmentarze.pl/wyszukaj-pochowanego/szukaj?name=<given>&surname=<surname>` — the whole
country. In a tab on ecmentarze.pl the page can be fetched and parsed: remove `script`/`ins`, and for
each link `grave/detail/N` take the highest ancestor element that contains only that one link — that is
the row of the grave (persons, dates, cemetery). At most 10 graves per result. Collective graves
(e.g. a military cemetery) list hundreds of names — truncate the row text. Helper:
[ecmentarze.js](ecmentarze.js). (Verified 2026-11.)

**One cemetery, every grave of a surname**: the cemetery's own search
`https://www.ecmentarze.pl/cmentarz/<cemetery-slug>/search?mode=search&name=&surname=<surname>` lists all graves of the
surname there; each grave page shows sector / row / plot (municipal partner data often without dates). Two graves of the
surname in neighbouring plots of one row (e.g. 5/3/41 and 5/3/42) are often a married couple — a hypothesis to check on
the gravestone. (Verified 2026-11.)

## Timenote

`https://timenote.info/en/search?q=<surname>` lists everyone of the surname in the service, 20 per page (`&start=N`, up
to about 100–120 results); the person page gives the cemetery and "section / grave". The list of a cemetery
(`/en/person/list?cemetery_id=N&start=20*k`) is not sorted by surname, can be incomplete (a burial of the last few years
may be missing) and usually stops 10–15 years ago. The "near buried" block on a person page is a neighbourhood on the
map, not the people in the same grave. To find a family grave, collect the grave numbers of everyone of the surname in
that cemetery: neighbouring numbers (796-797, 801, 802-803) are often relatives.

## Parish cemetery plans: Cmentarnik.net and parish finders (checked 2026-11)

Many small parish cemeteries that are on neither Grobonet nor eCmentarze have an interactive plan with a search on a
platform of their own. A web search for the parish village with "cmentarz" lists the services that host its cemetery
(cmentarnik.net, mogily.pl, a Grobonet subdomain, eCmentarze); do it for the parish and for each village with a filial
church, because a filial church often has its own cemetery.

**Cmentarnik.net** (parishes and municipalities, about 200 cemeteries):
- **Which cemeteries are there**: the global search page `https://cmentarnik.net/szukaj` has a select field listing every
  cemetery ("Cmentarz Parafialny w Przykładowie"); read its options. The global search itself is behind a reCAPTCHA — do not
  use it. Each cemetery has its own search without one.
- **The cemetery's page** is `https://cmentarnik.net/<slug>`, the slug being the place name without diacritics, spaces or
  hyphens (`przykladowowielkie`), with a hyphen before a district (`wzorcowo-zarzecze`). Test the candidates: a wrong slug gives 404.
- **Search**: the form on the cemetery page posts to `/<slug>/szukaj/zmarly` with `_token` (a hidden field of the page) and
  `mane` (a surname or a given name). In a tab of the site, `fetch` with a `FormData` and parse the `tr` rows: "Kowalski Jan
  1921-03-04 1988-11-30 B/2/7", married women with "(zd. Nowak)" — the maiden name comes from the parish files and is often
  not on the stone. The token of one cemetery page worked for the other cemeteries in the same session.
- **The grave card** is `/<slug>/<sector>/<row>/<place>` (or `/g/<id>`): everyone in the plot with both dates, and photos under
  `/images/inst/<cemetery id>/graves/…` in full size. The "Lat" column is the difference of the years, not the exact age.
- **Neighbours in the row**: fetch the cards of the plots next to a family grave (place − 2 … + 2). Consecutive plots often
  hold one family: the parents, a son-in-law, the wife's own parents. A neighbour whose name the family already gave (a
  sibling's spouse, say) is the strongest sign that the grave next to him is that of the family's parents.
- **Coverage**: search a common given name ("Jan", "Maria") — dozens of hits show a filled database, while a common surname
  may honestly give 0 in a small village.

**A parish's own finder** (e.g. `cmentarz-<town>.pl`): a POST form with given name and surname; each result has "Pokaż grób"
(show the grave), and the card shows sector / row / place, the photo and everyone in the plot. "0000-00-00" means that the
date is unknown, not that the person is alive. Such a finder covers the parish cemetery only; the town's municipal cemetery
is usually a separate site (often a Grobonet subdomain whose data start in the 2000s).

## Reading grave results

- **The stone and the parish database can disagree on the given name**: the database may hold the first baptismal name
  (from the parish register) and the stone the name used in life — "Jan" in the database, another name on the stone. Record
  both (`variants`) and quote both in the source.
- **A family's account may give a near form of a name** (a similar-sounding name, a diminutive, the second of two given
  names). When the surname, the maiden name, the year, the cemetery and the spouse all match the account, the stone's name is
  the better one: correct `given`, keep the family's form in `variants` and say in `notes` what changed. When the names differ
  and nothing else ties the grave to the person, keep the grave as an unlinked candidate and ask the family.

- A search by a woman's given name and her maiden surname returns hundreds of unrelated graves nationwide (eCmentarze,
  Timenote). Use the married surname, a cemetery filter, or Grobonet with a voivodeship, which at least lists the
  cemeteries with the number of hits.
- Municipal cemeteries in eCmentarze often show only sector / row / plot, no dates; Grobonet's cemetery view shows dates
  or "date unknown", and a shared grave number links spouses. A cemetery inventoried in one service is often missing from
  the other — try both.
- Grobonet's `miasto=` returns "0 cemeteries" for a place outside its own list, also for a surname that certainly occurs:
  test the place with a very common surname before concluding that the cemetery is not in the service. Even then the
  cemetery may be there under a name `miasto=` does not match: it shows up in the voivodeship-wide list of a surname
  that has a grave in it (e.g. "Przykładowo, Cmentarz Parafialny (nowy)"), and its `idcmproj` then opens it for any
  surname (see above). The person page
  has the gravestone photo — read the inscription there; "Osoby pochowane w tym grobie" lists only the entries typed into
  the database, not every name on the monument.
- Burials from about 2012 on are in practically no index (cemetery indexes, parish indexes and the obituary search
  `nekrolog.pl/nekrologi?q=<surname>` stop earlier). The exception is a parish's own Grobonet site (above), which can
  be current to the last few months, though often with gaps in single years. For a recent death what is left
  otherwise is the parish office of the cemetery, a photo of the gravestone, an obituary the family kept and the civil
  registry office.
- A parish website rarely helps for a funeral a few years back: many keep only the current weekly announcements and
  Mass intentions (often as an image), and the archive of posts may start years after the death. Look at the archive
  months before reading anything. (Checked 2026-11.)
- A village cemetery beside a town may belong to a family that lived there before moving to the town: check who bore the
  surname in the records of the cemetery's parish.

## Others

- PomGenBaza cemetery indexes: see [pomgenbaza.md](pomgenbaza.md).
- mogily.pl did not open in the agent's browser (2026-11); Find a Grave and BillionGraves rarely have
  Polish rural cemeteries.
- **Find a Grave holds bulk imports of some big-city municipal cemeteries** (name, exact dates of birth and death,
  cemetery; no plot, no photo): `https://www.findagrave.com/memorial/search?firstname=<given>&lastname=<surname>`
  searches worldwide and may find a city burial that Grobonet and eCmentarze lack — then open the city's own finder
  for the plot and the others in the grave. A BillionGraves result URL with parameters was blocked in the agent's
  browser (2026-11).
- When no database covers the cemetery: the family, a photo of the gravestone, or the civil registry office.

## Municipal cemetery finders (checked 2026-11)

Large cities run their own grave finders for municipal cemeteries (the city's or the municipal cemetery
board's website, "wyszukiwarka grobów"), separate from Grobonet and eCmentarze, with name, years of life
and the date of burial; parish cemeteries in the same city often have a separate finder. Typical form:
surname, given name, optional cemetery, a "Filtruj"/"Szukaj" button and results in a side panel. Useful
for families who settled in the western and northern territories after 1945. Search the surname alone
and read the list, then narrow by given name.
The details of a result ("Pokaż szczegóły rekordu" / "Więcej") often add the **burial date** and "Inne osoby" — the
others buried in the same grave, with their dates — the quickest way to a spouse; a person born too late to be the
mother of a known child rules out one candidate couple. Prefix matching ("początek") with the short surname also
catches the German spelling (Kowalsk… → Kowalski, Kowalsky). (Checked 2026-11.)
