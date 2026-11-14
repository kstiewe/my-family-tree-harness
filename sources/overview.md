# Services at a glance

Addresses checked in 2026-11. Detailed guides are linked where they exist.

## Indexes (search by surname)

| Service | Coverage | Notes |
|---|---|---|
| [Geneteka](https://geneteka.genealodzy.pl) | births, marriages, deaths from all of Poland and the former eastern lands | the basic tool; [guide](geneteka.md), `scripts/geneteka.py`; exact search, "as a couple", parishes within 15 km, recently added indexes |
| [PomGenBaza](https://www.ptg.gda.pl/language/pl/pomgenbaza/przeszukiwanie-rejestrow-metrykalnych/) | Pomerania, Kashubia, former West Prussia: parish and civil (Standesamt) books, cemetery indexes | many books that Geneteka lacks; gives the archive signature and photo number; [guide](pomgenbaza.md) |
| [Genealogia w Archiwach](https://www.genealogiawarchiwach.pl) | scans and indexes of the state archives of the Kuyavian-Pomeranian region | person files with parents; [guide](genealogiawarchiwach.md) |
| [Geneszukacz](https://geneszukacz.genealodzy.pl) | combined search over PTG databases | supplements Geneteka |
| [Poznan Project](https://poznan-project.psnc.pl) | marriages from Greater Poland, mostly 19th century | excellent for the Prussian partition |
| [BaSIA](https://www.basia.famula.pl) | Greater Poland, record indexes with a map | links to scans |
| [Lubgens](https://lubgens.eu) | Lublin region and surroundings | needs a browser (bot protection) |
| [JRI-Poland](https://jri-poland.org) | Jewish records | — |
| [Gesher Galicia](https://www.geshergalicia.org) | Galicia: cadastral maps, censuses, records | — |
| [FamilySearch](https://www.familysearch.org) | microfilms and scans from Poland, Germany, the USA and more; indexes | free account (the user logs in); Catalog → search by place; scripts get 403 |
| MyHeritage, Ancestry, Geni | other people's trees and records | only a hint (`online_tree`), always verify |

**Reading a Geneteka hit**: results include surname variants unless the search is exact; the
"Uwagi" column links to the scan and says where the books are kept. A missing result often means
the years are not indexed, not that the record does not exist.

## Scans of books

- [Metryki](https://metryki.genealodzy.pl): scans of books published by PTG.
- [Szukaj w Archiwach](https://www.szukajwarchiwach.gov.pl): scans from the state archives; [guide](szukajwarchiwach.md).
- **Diocesan archives**: original parish books, especially before 1808 and from the Austrian and
  Prussian partitions. Contact by e-mail; searches are often paid.
- **Parishes**: younger books, or books never deposited in an archive.
- **AGAD (Warsaw)**: parish registers from the lands east of the Bug.
- **Archives abroad**: Lviv (CDIAL), Vilnius (LVIA), Minsk (NIAB).

## Places and parishes

See [gazetteers.md](gazetteers.md).

## Supplementary sources

- **Population registers** (Congress Poland, from the second half of the 19th century, in the state
  archives among the records of communes and towns): household compositions with dates of birth and
  moves.
- **Censuses, residence registers, land/mortgage and notarial records, commune records.**
- **Military and wars**: Central Military Archives (Polish Army soldiers),
  [straty.pl](https://straty.pl) (victims of WW2), [Arolsen Archives](https://arolsen-archives.org)
  (forced labour, camps, Wehrmacht conscripts in post-war lists, DP files; [guide](arolsen.md)), the IPN archive inventory ([guide](ipn-inventory.md)); German loss lists 1914–1919 ([german-sources.md](german-sources.md)).
- **Newspapers and address books** of the 1920s–1930s (digital libraries with full text): weekly civil
  registry reports, obituaries, court reports, residents by street; [digital-libraries.md](digital-libraries.md).
- **Cemeteries**: [graves.md](graves.md).
- **Emigration**: passenger lists (Ellis Island 1892–1924, the German emigration ports), FamilySearch.
- **United Kingdom and Ireland**: [FreeBMD](https://www.freebmd.org.uk) (civil indexes of England and
  Wales from 1837), FreeREG (parish registers), FreeCEN (censuses), GRO (certificates), ScotlandsPeople,
  [irishgenealogy.ie](https://www.irishgenealogy.ie), Irish censuses 1901/1911 (National Archives of Ireland).
- **USA**: county records (births, marriages, wills), federal censuses, naturalisation records; much
  of it on FamilySearch.

## Limitations seen so far (2026-11)

- FamilySearch: scripts get 403, the account needs a login (the user does it).
- Mapster (igrek.amzp.pl) does not respond; Lubgens has bot protection.
- `curl` from an agent sandbox may be intercepted; read pages in the browser (page text or a small
  JavaScript snippet that returns only the needed rows).
