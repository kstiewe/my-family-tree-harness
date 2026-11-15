# FamilySearch

[familysearch.org](https://www.familysearch.org): microfilmed parish and civil books from many countries, with indexes made
by volunteers. Free account; the user signs in. (Checked 2026-11.)

## Access

- The catalog, the images and the record search need a signed-in account. The agent never signs in. When the user asks for
  it, the agent reads in the user's own signed-in browser through a browser extension the user has connected — only reading:
  never "Attach" a record to the Family Tree, never edit the tree, sources or account, no downloads.
- Images with a padlock are restricted ("available to members of supporting organizations"): they can be seen only in a
  FamilySearch center or an affiliate library. Their index is often still searchable (below) — tell the user which film to
  look at there.
- Profiles in the FamilySearch Family Tree are other people's work: a lead (`online_tree`), never a source.

## From the catalog to an image

- A catalog entry is `https://www.familysearch.org/search/catalog/<number>`; a place search is
  `https://www.familysearch.org/search/catalog/results?query=%2Bplace%3A%22<place>%22` (for the former German provinces use the
  German place name). Each film row has "Go to images" (a camera) or a note about restrictions.
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
- A film's own index is searched with `q.filmNumber=<DGS number>` (the "Search the index" link of a catalog row), also when
  its images are restricted.
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
