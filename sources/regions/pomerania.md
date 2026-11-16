# Pomerania and the former West Prussia

Gdańsk Pomerania (Pomerelia), Kashubia and the lower Vistula: today mostly the Pomeranian and
the northern Kuyavian-Pomeranian voivodeships. Prussian partition. Services: [PomGenBaza](../pomgenbaza.md),
[Geneteka](../geneteka.md) (regions `11pm` pomorskie, `02kp` kujawsko-pomorskie),
[Szukaj w Archiwach](../szukajwarchiwach.md), [German sources](../german-sources.md).

## Administration over time

| Period | Unit | What it means for records |
|---|---|---|
| until 1772 | Royal Prussia (Polish Crown) | Catholic parish books in Latin |
| 1772 / 1793 | First and Second Partition: Prussia | German place names appear in records |
| 1773–1829 and 1878–1919 | Province of West Prussia (Westpreußen) | districts (Kreise) grouped into two Regierungsbezirke |
| 1829–1878 | part of the Province of Prussia | — |
| from 1 Oct 1874 | Prussian civil registration (Standesamt) | civil records in German, in two copies |
| 1920 | most of the area → Poland (Pomeranian Voivodeship); Free City of Danzig 1920–1939; edges stay in Germany | civil records in Polish (USC) from 1920 |
| 1939–1945 | annexed (Reichsgau Danzig-Westpreußen) | records in German again; many church books moved west in 1944–45 |

Keep the German names of places and districts in `aliases`: civil records, gazetteers and loss lists
use them.

## Records and languages

- **Catholic parish books**: Latin, in the 19th century partly German or Polish. The originals of the
  diocese of Chełmno (seat in Pelplin from 1824) are in the **Diocesan Archive in Pelplin** (ADP);
  parishes of the diocese founded in 1925 for the Free City are in the Archdiocesan Archive in Oliwa. Some younger books are
  still in the parishes. `language: la` (or `de`/`pl`).
- **Protestant parish books**: German. Many were taken to Germany in 1944–45 and are in the
  Evangelisches Zentralarchiv in Berlin; many were microfilmed (FamilySearch). Some are in the Polish
  state archives. `language: de`.
- **Civil registration (Standesamt), from 1 October 1874**: German until 1919/1920, then Polish. Registers
  (birth, marriage, death) with the hour of birth, occupation, religion, whether the declarant could
  write. Books older than the 100/80-year limits are in the state archives (the State Archive in Gdańsk,
  signatures `10/<fonds>/0/<unit>`; the south of the region in the archives of Bydgoszcz and other
  Kuyavian-Pomeranian archives); younger ones in the civil registry offices. Scans on Szukaj w
  Archiwach typically reach about 1907. `language: de`.
- **One event, two records**: after 1874 a Catholic birth usually has a civil birth record *and* a
  parish baptism, with different record numbers (and often different name forms: Johann vs Joannes).

## Indexes and where to search first

1. **PomGenBaza** — the richest index for the region: parish and civil books that Geneteka does not
   have, with the archive signature of the book. Search by prefixes; use `motherMaidenName` to get all
   children of a couple at once.
2. **Geneteka** — `11pm` and `02kp`; for the Kuyavian-Pomeranian parishes it is often rich. Check the
   indexed years with `scripts/geneteka.py --parishes`; some parishes are not indexed at all.
3. **Szukaj w Archiwach** — scans of civil registry books, found through the signature from PomGenBaza.
4. **Genealogia w Archiwach** — scans and indexes of the Kuyavian-Pomeranian state archives (not of
   the State Archive in Gdańsk).
5. German sources: loss lists 1914–1919 (place of origin of soldiers), Meyers Gazetteer (parish and
   Standesamt of a village), GenWiki pages of districts and parishes.

## Church books and civil registers behind a login (verified 2026-11)

- **Archion** (archion.de, paid passes): Protestant church books kept in the Evangelisches Zentralarchiv in
  Berlin, among them many West Prussian parishes, often up to about 1900–1910 — years that the court duplicates
  in the Polish archives (and so PomGenBaza) do not cover. The parish pages are public without a login and list
  every book with its years and an id (e.g. `Taufen 1700–1790`, `Namensverzeichnisse Trauungen 1700–1880`):
  check there how far back a parish goes. FamilySearch may index only the later books of a parish (from the
  1770s in some West Prussian parishes) while Archion has the images of the older ones; the old name indexes
  (Namensverzeichnisse) are the quickest way into such a book.
- **GenWiki district pages** (`https://wiki.genealogy.net/Kreis_<name>`) list per parish which years are on
  Archion and which on FamilySearch, with the FamilySearch catalog numbers — the quickest way to learn where
  the books of a parish ended up.
- **Metryki GenBaza** (metryki.genbaza.pl, free account; a bot check at the entrance): PTG's own photos of
  civil registers and some Protestant registers from the State Archive in Gdańsk, including offices that have
  no scans on Szukaj w Archiwach. GenWiki lists them on pages whose titles start with "Metryki.GenBaza/"
  (one for civil registers, one for Protestant church books; find them with the wiki's full-text search).
  The "Nr zdjęcia" of a PomGenBaza entry is the photo there (unit = the last part of the signature). The bot check may
  not pass in an agent's own browser: read the photos in the user's signed-in browser (when the user asks for it) or
  let the user save them, see [metryki-genbaza.md](../metryki-genbaza.md).
- **Family association sites**: rare surnames of the region often have a family association with a TNG database
  (`…/search.php?mylastname=<surname>&myfirstname=<given>&mybool=AND`, person pages `getperson.php?personID=…`, families
  `familygroup.php?familyID=…`). They can give the whole family of a couple and illegitimate children with their
  mothers — a lead (`online_tree`), to be checked against civil records. Some association sites are framesets: the
  TNG folder is linked from the navigation frame, and the `tree` value (`tree=tree1` …) is in the links of the TNG
  start page. `search.php?mylastname=<surname>&lnqualify=equals&mybool=AND&tree=<tree>&order=birth` lists the
  bearers of a surname oldest first. Empty "Vater" and "Mutter" fields mean the association does not know the
  parents either; its notes (godparents, quotations from church books) and its source list are worth reading.
- **FamilySearch**: the catalog itself needs a login now; take the catalog numbers from GenWiki and give
  them to the user.

## More sources for the region (not yet used in sessions — verify and extend)

- **Pomorska Biblioteka Cyfrowa** (pbc.gda.pl) and **Kujawsko-Pomorska Biblioteka Cyfrowa**
  (kpbc.umk.pl): address books, newspapers (death notices), school reports, directories.
- **Bałtycka Biblioteka Cyfrowa** (bibliotekacyfrowa.eu): regional publications, maps.
- **Verein für Familienforschung in Ost- und Westpreußen** (VFFOW): publications, source editions,
  name indexes for East and West Prussia.
- **FamilySearch catalog**, search by the German place name: microfilms of Protestant and some Catholic
  books, and civil registers.
- **Polish electoral and population registers of the interwar period** in the state archives (city and
  commune records), when the civil records are still in the USC.

## Traps

- PomGenBaza tables show at most 50 rows — narrow the query.
- A name in Latin (Sophia), German (Sophie) and Polish (Zofia) in three records of the same person:
  search without a given name or in all forms; put the forms into `variants`.
- Clerks of the Standesamt often misspelled Polish surnames: search with short prefixes.
- Margin notes in civil registers correct names and dates — always read them.
- Grave databases cover few rural cemeteries here: deaths after the end of the indexes are often only
  known from the family or the USC.
- **Civil registers that stop in 1916**: for some offices the State Archive in Gdańsk holds the books only up to
  1916, and then the PomGenBaza index of the office and the photos on Metryki GenBaza stop there too. The books from
  1917 on are still in the civil registry office that took over the district (often a neighbouring town's USC),
  and no site has them. Before planning to read a civil record of 1917–1930s, open the unit list of the fonds on
  Szukaj w Archiwach (`_Zespol_nameofjsp=jednostki`, see [szukajwarchiwach.md](../szukajwarchiwach.md)) and look at
  the last unit. For those years use the parish indexes in PomGenBaza (marriages and deaths of the 1920s–1940s,
  deaths with the age), and leave the civil record to a request at the office. (Checked 2026-11.)
- **Newcomers after the First World War**: a surname that is absent from every index of a parish before 1917 and
  then appears as a cluster (a wedding, baptisms, adult siblings marrying, an old man dying at 70-odd) marks a
  family that moved in during or just after the war, often farm workers from the province of Posen or from Congress
  Poland. Example: no Kowalski in Przykładowo before 1917; from 1919 Jan Kowalski baptises children there, a
  Kowalska marries, and Franciszek Kowalski dies in 1936 aged 72 — a candidate for Jan's father, recorded as a
  hypothesis only. Search the man's birth nationwide (Geneteka region by region, BaSIA, FamilySearch, the
  Verlustlisten in [german-sources.md](../german-sources.md)); a common surname gives several equally good
  candidates, and only a record that names the birthplace (the marriage, the death) can decide between them.
- Religion matters: a Protestant family will not be in the Catholic books of the same village, and the
  Protestant parish may be in another place. Exception: the 18th century, below.
- **Protestant children in Catholic books before about 1775**: in villages of Protestant settlers on Catholic
  (e.g. monastic) estates of Royal Prussia, the Catholic parish priest often baptised the children of Lutheran
  families, in Latin. Indexers then garble the German surname: one Kowalski couple came out as "Kowalsky",
  "Kowalk", "Kawalke" and "Gowalski" in four baptisms. Search the Catholic parish of the village by the parents'
  given names without a surname (see [pomgenbaza.md](../pomgenbaza.md)) and compare the birth years with the
  ages the children give at their later Protestant weddings. The Protestant parish may have kept its own book
  for the same years as well: look in both.
- **Mixed marriages**: a Catholic wedding and Catholic baptisms of the children do not make the father
  Catholic — the children of a mixed marriage were often raised in the mother's church. Civil records give
  each parent's religion; when the father is "evangelisch" in several of them, look for his own baptism in
  the Protestant books (e.g. a Protestant Kowalski married to a Catholic Nowak: Catholic wedding and
  children, but the father's own baptism in the Protestant parish).
- **Parishes change**: the Meyers Gazetteer gives the parishes of about 1912. A parish founded later
  (books starting in the 1890s) did not serve the village decades earlier — check when its books begin and
  look in the older neighbouring parish.
