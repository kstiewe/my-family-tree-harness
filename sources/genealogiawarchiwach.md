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
