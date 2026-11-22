# Western and Northern Territories (Ziemie Zachodnie i Północne)

These are the lands that were German until 1945 and have been Polish since: Lower Silesia, most of Opole Silesia and
the west of Upper Silesia, the Lubusz land, Western (Farther) Pomerania, and the south of East Prussia (Warmia and
Masuria). Today they make up the Lower Silesian, Opole, Lubusz, West Pomeranian and Warmian-Masurian voivodeships,
and parts of the Pomeranian, Silesian and Greater Poland ones. The official term of the time was "Ziemie
Odzyskane" (Recovered Territories). Most of the German population fled or was expelled in 1945–1947, and Polish
settlers took its place. For a family that came after 1945, the German records of its village are about other people.
The work is to find **where the family came from**.

Services: [graves](../graves.md), [Szukaj w Archiwach](../szukajwarchiwach.md),
[IPN inventory](../ipn-inventory.md), [Arolsen](../arolsen.md), [Geneteka](../geneteka.md) for the regions of origin,
and [German sources](../german-sources.md) for the population before 1945.

## Administration over time

| Period | Unit | What it means for records |
|---|---|---|
| until 1945 | Germany: the Prussian provinces of Silesia, Brandenburg, Pomerania and East Prussia | German civil registers (Standesamt, from 1 October 1874) and church books. They record the people who lived there before 1945, not the settlers |
| 1945–1949 | Polish administration from spring 1945; Ministry of the Recovered Territories | the first settlers arrive and places get temporary Polish names; the German population is still present until the expulsions |
| 1946–1950 | new voivodeships for Lower Silesia, Western Pomerania and Warmia and Masuria; most of the Lubusz land in the Poznań voivodeship, Opole Silesia in the Silesian one | files of the State Repatriation Office (PUR) and of the district offices are in the archive of the voivodeship of that time |
| 1950–1975 | new voivodeships of Koszalin and Opole and one for the Lubusz land; PUR dissolved in 1951 | settlement matters pass to the presidia of the national councils, including the second repatriation from the USSR (1955–1959) |
| from 1975 | 49 small voivodeships, then today's 16 (1999) | the civil registry office (USC) of a village is usually that of today's commune |

## Who came, and where their earlier records are

| Group | When | Records from before they came |
|---|---|---|
| settlers from central and southern Poland (the former Congress Poland, Galicia, Greater Poland) | 1945–1950 | parish books and indexes of the region of origin: [Geneteka](../geneteka.md), [congress-poland.md](congress-poland.md) |
| "repatriates" from the former eastern lands annexed by the USSR | 1945–1946, in PUR transports | records from beyond the Bug: AGAD (older) and the Archiwum Akt Zabużańskich of the Warsaw civil registry office (younger). See docs/research-guide.md, "Eastern borderlands" |
| people returning from forced labour and camps in Germany | 1945–1947 | [Arolsen](../arolsen.md) |
| military settlers (demobilised soldiers) | 1945–1946 | the PUR had a military-settlement inspectorate (a series in the Poznań voivodeship branch, below); [IPN inventory](../ipn-inventory.md) |
| Ukrainian and Lemko families resettled by force in 1947 ("Akcja Wisła") | 1947 | Greek Catholic and Orthodox parishes of south-eastern Poland; the files of the PUR central board cover "Akcja W" |
| the second repatriation from the USSR | 1955–1959 | registration cards in the fonds of the presidia of the national councils (below) |
| the native population that stayed (Opole Silesia, Warmia and Masuria, edges of Pomerania) | — | their own German records before 1945 (Standesamt, church books) |

## "Born in Przykładowo": check the year first

A family account that a grandfather was "born in" a village of these lands is often only half right: the family
**lived** there after the war. Before you search the village's books:

1. **Compare the year of birth with the settlement.** A birth before 1945 in a village that was German until 1945 means
   a birth elsewhere. The exceptions are a family of the native population and a child of forced labourers (Traps).
2. **Date the family's arrival.** Use the oldest graves of the surname in the village cemetery (a grave of 1949 shows
   that the family was there by 1949), the family's first entries in the post-war parish books, and the settler lists of
   the commune (below).
3. **Get a record that names the real birthplace.** That is the person's own death or marriage record from the USC (a
   full copy usually gives the date and place of birth and the parents' names), or the same record of a sibling.

Example: Jan Kowalski was born in 1936, "probably in Przykładowo". Przykładowo was the German Musterdorf until 1945. The
Kowalski graves there start in 1949, and the family remembers "the transport". Jan's full death record gives a village
near Wzorcowo in central Poland as his birthplace, and the search moves to the books of Wzorcowo.

## Place names: German, temporary, official

- **Temporary names.** In 1945–1947 many places had a temporary Polish name (often a translation or adaptation of the
  German one) before the official name was fixed. Polish Wikipedia often gives it in the history section ("W latach
  1945–1947 wieś nosiła nazwę …", "nazwa przejściowa"). A full-text search on Wikipedia for the phrase "nosiła nazwę"
  with "1945" finds such articles, and the wiki's own search also finds a village by a temporary name mentioned in its
  article.
  (Checked 2026-11.)
- **Archive titles use the temporary names.** Units from 1945–1948 are titled with the temporary name and the official
  name in brackets, e.g. "Spis osadników gminy Wzorcowo Stare (Przykładowo)". Search the archive under both names.
  (Checked 2026-11.)
- **Family documents of the first years** (a 1946 certificate, a PUR card) may carry the temporary name. A place that
  "no longer exists" may be the temporary name of a village that still does.
- **In the data**, put every name into `aliases`: the German name, the temporary one and spelling variants. Put the
  period of each name into `notes` ("Musterdorf until 1945; Wzorcowo Stare 1945–1947, temporary; Przykładowo from 1947,
  official; source: Wikipedia, 2026-11-22"). The German district and the post-war units go into `admin`, e.g.
  `{period: "1871..1945", value: "Kreis Musterstadt (Germany)"}` and
  `{period: "1946..1950", value: "pow. przykładowski, woj. <of that time>"}`. `partition: prussian` describes the record
  system before 1918 (Standesamt from 1874).
- **The German name leads to the records before 1945**: Standesamt, church books, Meyers Gazetteer
  ([gazetteers.md](../gazetteers.md)). They concern the German population, not the settlers. Search them only for a
  native family or for a settler born in Germany.

## Where the settlers' records are

### Civil registry offices (USC)

Birth records younger than 100 years, and marriage and death records younger than 80 years, stay in the USC. For
settlers that is practically everything after 1945 (docs/research-guide.md, stage 2). A full copy (odpis zupełny) names
the parents. An entitled relative (a descendant, an ascendant, a sibling or the spouse) requests it at an office or
through the gov.pl e-service, which needs the user's own sign-in. Sending the request is the user's step. The agent
writes the data the form needs into the workspace `research/`: the kind of record, the office, the date and the names.
A village's books are usually held by the office of today's commune.

### Parish books after 1945

Catholic settlers often took over the village's former Protestant church. The parish books from 1945 on are kept in the
parish office and are rarely indexed online. A marriage there may name the spouses' places of birth.

### State archives: PUR and settler files (checked 2026-11)

- **The State Repatriation Office** (Państwowy Urząd Repatriacyjny, PUR, 1944–1951) has fonds of voivodeship branches
  ("Państwowy Urząd Repatriacyjny. Wojewódzki Oddział w …") and of district branches ("… Powiatowy Oddział w …") in the
  regional state archives. The State Archive in Olsztyn, for example, holds several district branches.
- **The files sit in the archive of the voivodeship of that time.** Many district branches of the Lubusz land are series
  13.x of the Poznań voivodeship branch (State Archive in Poznań, 53/918/0). A few are separate fonds in the state
  archive of today's Lubusz voivodeship.
- **What a PUR fonds holds**: the settlement section (applications for farms), the staging section (registers of
  repatriates, "księgi ewidencyjne repatriantów"), transport lists and resettlement certificates.
- **Registration cards of repatriates** ("karty ewidencyjne repatriantów") are units in PUR district fonds and in the
  fonds of district offices ("Starostwo Powiatowe w …", 1946). Cards from the repatriation of 1955–1959 are in the fonds
  of the presidia of voivodeship, district and town national councils ("Prezydium Wojewódzkiej / Powiatowej / Miejskiej
  Rady Narodowej"), also in central Poland.
- **Lists of settlers** ("spis osadników", one unit per commune, 1945–1948) are in the fonds of the district offices. An
  "Alfabetyczny spis osadników" can be in the fonds of a town administration. Some units are marked "Udostępniona: Nie"
  (not made available).
- **District land offices** ("Powiatowy Urząd Ziemski", fonds of 1945–1947 in the western districts) and the
  voivodeship land offices dealt with the allocation of farms.
- **None of these fonds or units had scans.** Search Szukaj w Archiwach by the unit title ("karty ewidencyjne
  repatriantów", "spis osadników"). The "Archiwum" filter on the results page shows which archives have hits, and the
  fonds' unit list gives the signature. Reading the files means an archive visit or a search request (kwerenda) by the
  user. The agent prepares the reference in the workspace: archive, fonds, unit signature and the persons sought.

### Graves

- **Post-1945 graves are well covered.** Towns run their own finders for the municipal cemeteries, and many village
  cemeteries are on Grobonet ([graves.md](../graves.md)). Search the surname in the whole voivodeship first: the list of
  cemeteries with the number of hits shows where the family lived.
- **A cluster of the surname in one village cemetery** is typical for settlers. Several households of one family, or of
  one village of origin, often came together. The birth years sort them into generations. The oldest generation (born
  before about 1900, died in the 1950s or 1960s) was born elsewhere, and their death records name the place of origin.
- **Neighbouring graves of the same surname** are a hypothesis about a relationship, never proof. A couple born about
  1900 next to a known sibling born in the 1930s are candidate parents. Check the ages and confirm with a death record;
  on Grobonet, consecutive person IDs add nothing (see [graves.md](../graves.md)).

### Tracing the region of origin

- **Death records of the settlers and of their children** (USC, full copy) give the place of birth of each person,
  which is the most direct way. A child who died young in the 1940s or 1950s has a death record in the village too.
- **The Geneteka surname overview** (`python3 scripts/geneteka.py --overview Kowalski --exact`) counts index entries per
  region. A rarer surname clusters in a few regions and parishes: a hint where to look, never a link
  ([geneteka.md](../geneteka.md)).
- **The IPN inventory** has personal files with the father's name and the full date of birth, e.g. a son's passport or
  service file. Use it only for deceased persons ([ipn-inventory.md](../ipn-inventory.md)).
- **Family papers of the first years**: a PUR evacuation card ("karta ewakuacyjna", which names the place of
  departure), a resettlement certificate ("zaświadczenie przesiedleńcze"), a land allocation document. Ask the family
  for them.
- **Neighbours from the same place**: settler villages were often filled by groups from one area. The settler list of
  the commune, or a PUR transport list, shows who came with the family.

## Traps

- **"Born in Germany" in a settler's document**: a child born in 1940–1945 may be a child of Polish forced labourers,
  born in a German town and registered by the German Standesamt. Look in [Arolsen](../arolsen.md) and the German registers, not
  in the village where the family lived later.
- **Two Polish names for one village** in 1945–1950 records (temporary and official), and a German one before. A record
  that names a place missing from today's map may use the temporary name.
- **The native population** that stayed (Silesians, Warmians, Masurians) has German records up to 1945 and Polish ones
  after. The same person appears with German and Polish forms of the given name.
- **A negative result in the village's books before 1945 means nothing** for a settler family: they were not there yet.
- **Nothing of the settlers is online in the civil registers**: the USC keeps their records, and the archives' scans of
  the region are the German-era books.
