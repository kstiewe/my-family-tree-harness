# Genealogia w Archiwach

[genealogiawarchiwach.pl](https://www.genealogiawarchiwach.pl) — scans and volunteer indexes of the
two State Archives of the Kuyavian-Pomeranian region: parish and civil registry books,
about 3.9 million scans, 2.1 million index entries and 230 000 "person files" (2026-11). It does not
cover the State Archive in Gdańsk; for Pomerania see [pomgenbaza.md](pomgenbaza.md).

## Using the site (checked 2026-11)

- It is a Vaadin application: links with `#query.query=…` do **not** run a search when the page is
  loaded fresh — use the form. On the first visit close the welcome dialog (the X in its top-right
  corner) and, if shown, the grey "Informacja" notice (a click on it), which covers the "Szukaj" button.
- Type the surname into "Wpisz nazwisko / nazwę dokumentu" and click "Szukaj" (pressing Enter is not
  enough). The results page has its own search field at the top and an advanced form (surname, given
  name, record type, years).
- Results come in two kinds: **person files** ("Jan Kowalski 1888–1962 Wzorcowo": place and year of
  birth, place and year of death, parents with the mother's maiden name) and **scans** with their unit
  signature (e.g. `NN/xxxx/0/2.3/yyyy`; the first number identifies the archive), office, year
  range and "powiązane indeksy" (the names indexed on that scan). Read them with `document.body.innerText` and filter in JavaScript; the
  first page shows about 20 persons.
- **The full list of persons**: the results show about 20 person files; the button "Wczytaj więcej" (load
  more) at the bottom adds the next batch — click it in a loop until it disappears, then parse
  `document.body.innerText` (each file is "Given Surname years place", a line "…", then the labelled fields).
  Search the masculine and the feminine form separately ("Kowalski", "Kowalska"): the person lists differ.
  To change the query on the results page, set the main text field (e.g. with a form-input tool) and click
  the "Szukaj" `.v-button`; clicking and typing at screen coordinates often misses the Vaadin field.
- **A person file** opens in a dialog after a click on the person icon of the card (the URL gains
  `&person=<id>`). Its "Powiązane indeksy" table lists every indexed record of that person — birth,
  **marriage** (with the spouse's name), death — with unit signature and page. A marriage entry is the
  quickest way to see that a namesake married someone else and can be excluded.
- A query of two words (surname + town) is matched as one phrase: "Kowalski Przykładowo" can give
  nothing although both words occur separately.
- The person files are far from complete: no hit does not mean there is no record. For the scans
  themselves the same books are on [Szukaj w Archiwach](szukajwarchiwach.md) (fonds signatures start
  with the same archive number), where the unit list shows which years have scans.
- In November 2026 the site warned about network reconfiguration; searches worked after the dialogs
  were closed.

## Books, scans and the "related indexes" (checked 2026-11)

- **Search parameters in the address work once the page is loaded**: setting `location.hash` in a tab where the site is
  already open runs the search; a fresh load of the same link does not. Useful keys: `query.query`, `query.type` (`ALL` for
  scans with indexes, `UNIT` for books), `query.city` (the place filter, e.g. `query.city=Przykładowo`).
- **All books of one office**: `query.type=UNIT` with the fonds number as the query (e.g. `query.query=1234` for fonds
  `6/1234`) lists every book of that civil registry office with its years and number of scans. The archive's other catalogue,
  [Szukaj w Archiwach](szukajwarchiwach.md), may show "Liczba skanów 0" for the same fonds — for the two archives covered
  by this site always check here too.
- **"Powiązane indeksy" name more than the couple.** On a marriage scan they usually list the groom, his parents, the bride
  and her parents. That is enough to rule out a namesake: if the only baptism of a "Marta Kowalska" born in the right years
  belongs to a woman who, by these indexes, married someone else with the same parents' names, she is not the ancestor. The
  same works with a death scan of a child (age, parents). Only volunteers' indexes: many scans have none or only some names.
- **Opening a scan**: the book icon of a result card opens the viewer in the same tab and puts `modal=<scan id>` into the
  address; setting that hash in a loaded tab opens the scan again later. "Pokaż skan w nowej karcie" opens a popup with
  `externalmodal=<scan id>`; when a browser blocks the popup, the id can be read from the address the page tries to open.
- **Table of contents of a book** ("Spis treści dla księgi", the tab on the left of the viewer): a year selector and the
  scans of that year numbered from 0 (0 is often a title page), each with "Przejdź". In civil registers one record is usually
  one scan, so record 5 of a year is item 5 — check the record number on the scan.
- **Images** come from the site's own IIIF service (`…/loris/<id>/full/,896/0/default.jpg` in the viewer). For reading one
  record, the same address with a larger width (`full/1600,/0/default.jpg`) opened in a tab gives a sharper image than the
  viewer; read single records this way, not whole books.
- **"Przepraszamy plik niedostępny"** ("file unavailable") can affect a single book for a day or longer while other books
  load normally. Note the book and the record in the log and retry later; the record is not lost.
- **Page numbers in brackets** ("…/2.3/1088 (8)") are this site's own numbering; they need not match the scan numbers of
  the same book on [Szukaj w Archiwach](szukajwarchiwach.md), and the indexed name can belong to any person of the record
  (the deceased, a parent, the person reporting). When the scan does not open here, find the record there by reading the
  book (see "Reading a whole book without an index" in that guide).
- **The other copy of a register**: a main register held by one of the two archives (its fonds number starts with that
  archive's code) whose file is unavailable may exist as the duplicate ("Neben-Register", series 3.x) of the same office in
  the other archive on Szukaj w Archiwach — search the office's name there. The duplicate lacks later margin notes (e.g. post-war notes of death).
- **Interwar books marked "wtóropis (odtworzony)"** (reconstructed duplicate) may be German translations made during the
  occupation ("Beglaubigte Übersetzung aus dem in polnischer Sprache geführten Heiratsregister …"): the content follows the
  Polish original, but names and places are in German forms (Johann, Martha, occupation-era place names). They are often the
  only copy of the 1920s in the archive, because the original register stayed in the civil registry office.
