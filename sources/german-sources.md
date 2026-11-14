# German sources

Useful for the Prussian partition, for families with German roots or "from Germany", and for anyone
who served in the German army. Most are run by the Verein für Computergenealogie (CompGen).

## Loss lists 1914–1919 (Verlustlisten)

`https://des.genealogy.net/eingabe-verlustlisten/search/index?lastname=<surname>&firstname=&value01=&search=Search&page=<n>`
— 50 rows per page, counter "Es wurden N Einträge gefunden". Pages can be fetched (`fetch`) in a tab
on des.genealogy.net and parsed with DOMParser (columns: surname, given name, place with district,
list, regiment, status, …, date). They give the soldier's **place of origin** — good for mapping
where a surname lived. Check spelling variants separately (Kowalski / Kowalsky / Kowalskj).
(Verified 2026-11.)

## Address books (Adressbücher)

`https://adressbuecher.genealogy.net/search?name=<surname>&givenName=&occupation=&placeName=&placeId=&address=&companyName=`
— at most 50 results; details of an entry (title of the book, page) under `/entry/<uuid>`. The first
visit shows "Making sure you're not a bot!" — wait a few seconds. Cities and years are indexed
unevenly: check which years of a city exist before concluding anything.

Entries marked 📘 have a scan: the link "Scan herunterladen" on the entry page leads to a JPG on
files.genealogy.net (large, several columns per page). Open it in a tab and crop at 1:1 (a `div` the
size of the window with `overflow:hidden`, the image `position:absolute` with negative `left/top`) for
a readable screenshot of one column. The index can be incomplete — read the whole scanned page.
Address books list only independent householders: children, servants and sub-tenants are missing.
(Verified 2026-11.)

## GEDBAS

`https://gedbas.genealogy.net/search/simple?lastname=<surname>&firstname=&placename=&timelimit=none` —
family trees uploaded by researchers: a lead (`online_tree`), not a source.

## German state archives in Szukaj w Archiwach

Civil registry fonds of the former German eastern provinces are in the Polish state archives,
usually named "Urząd Stanu Cywilnego w X, pow. Y". If the full name gives "Brak wyników", search for
the place name alone (the books themselves are titled in German, e.g. "Geburts-Haupt-Register X").
20th-century books are usually without scans.

## Gazetteers and administrative units

- [Meyers Gazetteer](https://www.meyersgaz.org): places of the German Empire (~1912) with the Catholic
  and Protestant parish and the civil registry office.
- [GenWiki](https://wiki.genealogy.net): pages for places, districts (Kreis), parishes (Kirchspiel)
  and civil registry offices (Standesamt), often with the location of the books. (Not yet used in sessions.)
- [territorial.de](https://www.territorial.de) (Rolf Jehke): administrative history of German
  districts down to Amtsbezirke and Standesämter. (Not yet used in sessions.)
