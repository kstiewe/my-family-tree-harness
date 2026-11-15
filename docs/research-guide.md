# Research guide

How a family tree grows with this toolkit, and what to expect from records in Polish lands.
Service-specific techniques are in [sources/](../sources/README.md).

## Stages

**0. Foundation.** A workspace, the data format, the tools (this repository).

**1. Family knowledge.** Start with yourself and go up. Tell the agent everything you know: names,
surnames (maiden names for women), approximate dates, places, parishes, occupations, religion — and
for every piece of information where you know it from. Most valuable and most urgent: talking to
the oldest relatives and home documents (certificates, military books, school reports, funeral
notices, photos with notes on the back, inscriptions on gravestones). Record the conversations;
ask about places, parishes, nicknames, wars, resettlements, emigration.

**2. 20th-century civil records (USC).** In Poland birth records younger than 100 years and marriage
and death records younger than 80 years are kept by civil registry offices (USC); older ones go to
the state archives. A full copy (odpis zupełny) names the parents; it can be requested by the person,
the spouse, ascendants, descendants and siblings. Usually the shortest way to the generation born
around 1900–1925.

**3. Online indexes and scans (19th century and earlier).** For every end of a line search Geneteka
and the regional databases, verify hits on scans and record the source. One marriage record often
moves a line a whole generation back: marriage record → parents of the couple → their marriage → …

**4. Going deeper.** Siblings of ancestors, population registers, censuses, military records,
emigration, land and mortgage records — useful when a line hits a "brick wall".

**5. Sharing.** GEDCOM to Gramps, MyHeritage or FamilySearch; a page with the tree for the family
(`--public` hides living persons).

## The cycle for every batch of information

1. The user gives information in any form (example below).
2. The agent enters it into the workspace data, checks duplicates, sets confidence and the source.
3. `build.py` validates the data and the chronology (a mother aged 60, a child born after the
   father's death …).
4. For the ends of lines the agent searches Geneteka and other services. Every hit is a hypothesis
   until a scan of the record confirms it.
5. Results, also negative ones, go to the workspace `research/log.md`.
6. The user gets a short summary: what was added, what was found, the priority gaps and which books
   are worth checking (from the gap report).

How to give information — any form, as long as certain and uncertain things are distinguished:

```
Jan Kowalski, my great-grandfather on my father's side.
Born c. 1890 in Przykładowo, parish probably Wzorcowo. Died 1956 in Zmyślin.
Wife: Anna née Nowak, married c. 1915. Children: Józef (1916), Maria (c. 1920).
Farmer, Catholic. How I know: grandmother Zofia (conversation 2026), photo of the gravestone.
Uncertain: whether Jan's father was called Wojciech.
```

## Order of work with sources

1. **Family and home**: relatives, documents, photos, funeral notices, prayer books with entries,
   gravestones.
2. **Civil registry offices** for the 20th century (see stage 2).
3. **Online indexes**: fast search by surname; they point to candidates.
4. **Scans of books**: confirmation and the full content (witnesses, ages, occupation, annotations).
5. **Archives**: undigitised books, supplementary files, population registers, land records.

## What survived where: the partitions

**Congress Poland (Russian partition).** From 1808 civil-status records were kept by the clergy
acting as civil registrars, in two copies; the duplicates went to the courts and are now in the
state archives. Records are narrative ("Działo się we wsi…" — "It happened in the village…"). Until
1867/68 they were written in Polish, then in Russian until about 1917. Marriage records usually
give the age, place of birth and parents of the couple; birth records give the mother's maiden name.
Russian records carry two dates, Julian and Gregorian. Before 1808: parish books in Latin, shorter
and without ages. Source `language`: `pl` before 1868, `ru` after, `la` before 1808.

**Prussian partition.** Parish books were kept in Latin, from the 19th century also in German. From
1 October 1874 in Prussia (1876 in the whole German Empire) secular civil registry offices
(Standesamt) kept the records — in German until 1919/1920; they are in the state archives and often
online. Church books are in the diocesan archives. Source `language`: usually `la` for Catholic
books, `de` for Protestant books and the Standesamt.

**Austrian partition (Galicia).** Parishes kept the registers, from 1784 in tabular form, in Latin.
There are few duplicates in the state archives: search diocesan archives and parishes, for Eastern
Galicia AGAD in Warsaw and the archives in Lviv.

**Eastern borderlands.** Parish registers from the lands east of the Bug are in AGAD (Warsaw);
younger civil records from these lands are kept by the civil registry office of Warsaw (Archiwum
Akt Zabużańskich). Abroad: Lviv (CDIAL), Vilnius (LVIA), Minsk (NIAB).

## Reading records

- Latin: Joannes = Jan, Adalbertus = Wojciech, Laurentius = Wawrzyniec, Casimirus = Kazimierz,
  Hedvigis = Jadwiga, Agnes = Agnieszka; *legitimus/illegitimus* = born in/out of wedlock,
  *viduus/vidua* = widower/widow, *agricola* = farmer, *hortulanus* = smallholder,
  *inquilinus* = landless tenant.
- German (Standesamt): *unverehelicht* = unmarried, *unehelich* = illegitimate, *Arbeiter* = labourer,
  *Knecht*/*Magd* = farmhand/maid, *Einwohner*, *Instmann* = landless (estate) labourer, *Käthner* =
  cottager, *Besitzer*/*Eigentümer* = farm owner, *Altsitzer* = retired farmer, *Abbau X* = an outlying
  farmstead belonging to village X. Short forms of given names: Mina/Minna = Wilhelmine, Guste = Auguste,
  Fritz = Friedrich, Hans = Johann, Lene = Helene.
- Ages in death records are often exaggerated or rounded, by 5–10 years. Ages at marriage are
  usually more accurate.
- When an ancestor's own record is missing, the siblings help: the same parents, and relatives often
  appear as witnesses. The declarant of a death names his relation to the dead (*Sohn*, *Schwiegersohn*
  …): a son-in-law leads to a daughter's marriage.
- **When no married couple fits the parents' names**, consider an illegitimate birth before widening the
  search: the child bears the mother's surname and the father is usually not named ("Sohn der
  unverehelichten Anna Kowalski", "syn niezamężnej Anny Kowalskiej", *filius illegitimus*). A later record
  may call the mother *Arbeiterfrau* (working woman), which does not prove a marriage. Then search the
  mother's name alone: her other children (half-siblings) and her own birth, with her parents. The baptism may still name the
  natural father, and an index may then file the child under his surname — search by given name and date, without a surname.
  A father who appears only in an index is not proof. Indexers attach names and margin notes to the neighbouring entry, so
  check the children baptised just before and after, a second index of the same book and the man's own marriage
  (sources/familysearch.md).
  A Protestant mother's child may be baptised in the Catholic parish of the birthplace, especially where the Protestant
  parish was founded later.
- Read the margins of civil birth records: a book kept in the office for decades may note the person's
  marriage or death with the office and record number — a way to a death whose place nobody knew.
- Weigh who spoke: names given by a neighbour or co-worker who reported a death are the least reliable;
  a person's own marriage record is the best witness to the parents' names. A parent called *verstorben*
  (deceased) in a child's record died before that date, one given with a residence was alive — together
  they bound the search for the parent's death.
- Online trees can merge two namesakes of similar age: when the age or birthplace in a death record does
  not fit the tree, look for a second person of that name (two August Kowalskis: the tree gives one's
  birth and the other's death and wife). Check every date taken from a tree against a record.
- A Prussian civil record gives the hour and place of birth, occupation, religion and whether the
  declarant could write; a parish record usually does not.
- Family accounts can be wrong about names. When a later account agrees with another relative's and
  an index confirms it, revise the earlier decision — and record the change in `notes`.
