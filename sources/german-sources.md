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
  and Protestant parish and the civil registry office. Search with `https://www.meyersgaz.org/search?search=<name>`
  (the parameter `q` does nothing); the list gives every place of that name with its Kreis — pick the one in
  the right district. A place page `/place/<id>` shows the type (Dorf, Rittergut …), population, Amtsgericht
  and Standesamt; the parishes are in the "Ecclesiastical" section, opened by the page's own
  `showSection('divEcclesiastical')` (then read `#divEcclesiastical`). The parishes are those of about 1912.
  (Verified 2026-11.)
- [GenWiki](https://wiki.genealogy.net): pages for places, districts (Kreis), parishes (Kirchspiel)
  and civil registry offices (Standesamt), often with the location of the books. District pages
  (`/Kreis_<name>`) list the church books of each parish available on Archion and on FamilySearch, with
  FamilySearch catalog numbers; the pages whose titles start with "Metryki.GenBaza/" list what Metryki
  GenBaza has from the State Archive in Gdańsk. A missing page title gives an empty page — use the wiki's full-text search
  (`/index.php?search=<word>&fulltext=1`). A script's fetch may get a bot-check page instead; the browser passes it.
  (Verified 2026-11.)
- [territorial.de](https://www.territorial.de) (Rolf Jehke): administrative history of German
  districts down to Amtsbezirke and Standesämter. (Not yet used in sessions.)

## Regional histories in library repositories

Articles of historical societies and Festschriften about the districts of West and East Prussia often
name the inhabitants of each village from 18th-century surveys. Library repositories (e.g. the document
server of the MGH library) host them as scanned PDFs with an OCR layer, which a page-fetching tool may
fail to read: save the PDF into a fresh folder in the scratchpad, extract it with `pdftotext -layout` and
search for the surname loosely (OCR errors: [digital-libraries.md](digital-libraries.md)). A namesake a
century earlier is a lead to where the surname lived, not an ancestor, until a chain of records connects
them. (Verified 2026-11.)
