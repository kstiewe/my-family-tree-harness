# FamilySearch

[familysearch.org](https://www.familysearch.org): microfilmed parish and civil books from many countries, with indexes made
by volunteers. Free account; the user signs in. (Checked 2026-11.)

## Access

- The catalog, the images and the record search need a signed-in account. The agent never signs in. When the user asks for
  it, the agent reads in the user's own signed-in browser through a browser extension the user has connected — only reading:
  never "Attach" a record to the Family Tree, never edit the tree, sources or account, no downloads unless the private
  instructions allow them.
- Images with a padlock are restricted ("available to members of supporting organizations"): they can be seen only in a
  FamilySearch center or an affiliate library. Their index is often still searchable (below) — tell the user which film to
  look at there. `locations.familysearch.org` lists the centers and affiliate libraries of a country; centers may open by
  appointment only, and affiliates include public libraries and museums.
- Before sending the user to a center, read the catalog entry's notes: they say where the film was made ("filmed from
  manuscripts in …", a parish archive, a state archive). The same books may be elsewhere. Protestant books of the former German
  eastern provinces are often scanned on Archion ([german-sources.md](german-sources.md)). Catholic books are in the parish
  or the diocesan archive. Duplicate registers may sit in a state archive with scans on [Metryki GenBaza](metryki-genbaza.md).
- Profiles in the FamilySearch Family Tree are other people's work: a lead, never a source. Read the profile (dates, spouse,
  children, parents) and how many sources are attached to it; a profile with none only tells you what its author believed.
  Record it as a source of `type: other` with `quality: derivative`, not `online_tree`: the privacy guard treats the host of
  an `online_tree` source as private (right for a family's own website), and with FamilySearch's host it would flag every
  mention of the service in the repository. Check each claim in the index before you use it — a profile can join a
  record's place from a wrongly catalogued film, or give a date found nowhere else.

## From the catalog to an image

- A catalog entry is `https://www.familysearch.org/search/catalog/<number>`; a place search is
  `https://www.familysearch.org/search/catalog/results?query=%2Bplace%3A%22<place>%22` (for the former German provinces use the
  German place name). Each film row has "Go to images" (a camera) or a note about restrictions.
- In the user's signed-in browser the place search also works through the form: type the German place name into the
  "Place" field, pick the suggestion and search. The result address is
  `https://www.familysearch.org/search/catalog/results?q.place=<place>&q.placeId=<id>`; open the subject ("Church records")
  to see the entries. A keyword address (`…/catalog/results?keywords=…`) gave an empty page (2026-11).
- The last cell of a film row tells what is possible: images online, "visible with additional restrictions" (a FamilySearch
  center or an affiliate library), "not available digitally" (microfilm only), and often "Search the index" — the film's own
  index, `q.filmNumber=<DGS number>`. A film labelled with a filial parish can hold entries of the mother parish too; the
  index shows the place of each entry.
- In the viewer, type an image number into the image box and press Enter. Under the image, the "Image index" panel lists the
  indexed persons of that image with their age and an estimated year of birth — enough to find a year without reading the
  scans: jump, read the years, jump again. Example: marriages 1850–1925 on 325 images give about four images per year.
- To read an entry, zoom with the viewer's + button and move with Shift + arrow keys (dragging may not move the image in an
  automated browser), then take region screenshots.

## Searching the index of a collection

- The viewer's information panel names the collection ("Historical record collections"); open it to get its id. Search it
  with URL parameters, e.g.
  `https://www.familysearch.org/search/record/results?f.collectionId=<id>&q.surname=Kowalski&q.anyPlace=Przykładowo&count=100`,
  and narrow with `q.givenName`, `q.birthLikeDate.from` / `.to`, `q.marriageLikeDate.from` / `.to`, `q.deathLikeDate.from` /
  `.to`, `q.fatherGivenName`, `q.motherGivenName`, `q.spouseGivenName`, `q.surname.exact=on`.
- Results are ranked, not filtered: a total of thousands still shows the exact hits first, and spelling variants come with
  them (Kowalski, Kowalsky). Read the first hundred rows and keep those from the right place.
- A record page gives the age, the parents and often the parents-in-law; put its permanent "ark" address into the source.
  An image found through the viewer has its own "ark" address; record the film number and the image number too.
- Indexes make mistakes: one marriage index may give a father's name that the baptism contradicts. Prefer the entry closest
  to the fact (the baptism for the parents, the burial for the death) and record the conflict in `notes`.
- Negative results count only for the indexed years and places of that collection — note which ones were searched.
- **The priest's spelling.** The civil registrar and the parish clerk often spelled a surname differently ("Neesler" in the
  civil birth record, "Nezler" in the baptism), and the fuzzy match ranks such forms low or not at all. When the family
  surname gives nothing, search the forms a Polish or Latin writer would use (s / z / sz, ee / e, -er / -ar) and check the
  hit by the parents' names and the date.
- **All children of a couple in one search**: `q.surname=<family surname>&q.motherSurname=<her maiden name>` (narrow with
  `q.fatherGivenName`) lists the baptisms and burials of the couple's children in every indexed parish, each row with both
  parents. Rows with the same mother and another father's given name show either a second couple or an indexing error;
  note them.
- **One entry, two indexes.** A register filmed twice (an original and a copy) is indexed twice: the same baptism with the
  same page numbers, but the two catalog entries may name different places, one of them a namesake village in another
  county. Compare the page numbers before treating the rows as two events, and take the place that fits the family.
- **Given names that share a short form.** A mother written "Apolonia" in some entries and "Paulina" in others (both
  "Pola") may be one woman: Jan Kowalski's children baptised in the same villages and years with mothers "Apolonia Nowak"
  and "Paulina Nowak". Keep that a hypothesis until a record with both names, the marriage image or a civil record settles
  it — another couple with the same surnames may live nearby.
- **West Prussia: the Catholic and Lutheran church books collection, 1537–1981** (in Polish "Niemcy, Prusy, Prusy
  Zachodnie, Zapisy Kościoła katolickiego i luterańskiego"; take its id from a record page, the link "O tej kolekcji" /
  "About this collection") indexes parish books of the province, often with the exact date of a wedding that the
  regional indexes give only as year and record number. Coverage differs per parish (for one parish it held the
  19th-century baptisms and the weddings up to about 1918 only). Most of its images are restricted, but the record page
  ("Informacje o dokumencie" / "Document information") still shows the digital folder number and the image number: record
  both, so the image can be read at a FamilySearch center or an affiliate library.
- **Burial or death**: the index names the event type ("Burial", "Death"). Online trees often copy a burial date as the date
  of death. Record the burial separately (`burial`, with the age) and keep the death to the month when only the burial is
  known.
- A film's own index is searched with `q.filmNumber=<DGS number>` (the "Search the index" link of a catalog row), also when
  its images are restricted.
- **A search needs a name.** With only the parents' given names FamilySearch asks for a surname. Use the child's given name
  with a date range (`q.filmNumber=<DGS>&q.givenName=Johannes&q.birthLikeDate.from=1720&q.birthLikeDate.to=1730`), or a
  surname wildcard with the father's given name (`q.surname=Kow*&q.fatherGivenName=Jan`).
- **Old registers are indexed partly**: unreadable surnames appear as `*ski` or `Ko?al*`, and some entries have a given name
  only. In such a film, search by given name and years and read every row of the right years; no hit under the surname
  proves little there.
- **A child not found under the family surname**: search the given name and the exact year in the film, with no surname. An
  illegitimate child may be indexed under the father's surname when the baptism names him (Jan Kowalski, son of the unmarried
  Anna Kowalska, found as "Johannes Nowak" with mother "Anna Kowalska" and father "Thomas Nowak"). Latin given names count too
  (Johannes, Joannes for Johann).
- **Check the neighbouring entries before you accept such a father.** An indexer can attach a father, or a margin note about
  a later legitimation, to the wrong row. In the example, a second index of the same book (PomGenBaza) gave the next record
  of that year to Thomas Nowak: a son of Maria Wiśniewska, whom Thomas Nowak married a few months later. FamilySearch had
  indexed that son under his mother's surname, with no father, and the son later married as "Nowak, son of Thomas". So
  "Thomas Nowak" in Jan's entry most likely came from the next row. Look up the children baptised just before and after
  (given name, place, year), and the man himself as a parent: a search for his name also returns the rows where he is a
  father or a spouse, which lists his children and marriages. Compare with a second index. Until a scan settles it, keep
  such a father a hypothesis.
