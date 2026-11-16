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

- **Stillbirths** ("ein totes Mädchen/Knabe geboren") were entered only in the death register (Sterberegister) of the
  Prussian civil registry, not among the births: a family's child missing from the birth register may be found there, and
  such a record proves where the parents lived in that year (example: "Johann Kowalski, Arbeiter, wohnhaft in Przykładowo,
  reported that his wife gave birth to a dead boy").
- **Post-war Polish notes on Prussian birth records**: from the 1950s the civil registry offices stamped notes of death on
  the main birth registers ("Zmarł(a) dnia … w …, USC … nr …"). The duplicate register (Neben-Register) usually has no
  such notes — when the main register is not online, the note can only be asked for at the archive holding it.

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
- [Archion](https://www.archion.de): scans of Protestant church books. This includes the books of the former eastern provinces
  kept by the Evangelisches Zentralarchiv in Berlin: "Alle Archive" → "Evangelisches Zentralarchiv in Berlin" → the Kreis
  (with its province) → the parish. The catalog shows every book with its years without an account. A book marked as having
  no digital copy is not online. Name lists (indexes of baptisms, marriages, burials) are separate books, useful before
  reading a year page by page. Viewing needs a paid pass (2026-11: one month 19.90 € with 50 PDF downloads, three months
  52.20 €, a year 178.80 €). The user buys it and signs in; the agent then reads in the user's browser.
  A book's own page (`…/<parish>/<id>`, also without the `cHash` parameter) shows its archive signature ("Signatur Lokal",
  e.g. `EZA 980/1234`) without an account — cite it in the source's `repository`. A name list may be bound with a register
  and share its signature. (Verified 2026-11.)
- **Collect Archion lookups before buying a pass.** A pass is paid by time, so keep a register in the workspace (e.g.
  `research/archion.md`) of everything that only Archion has online: per entry the parish, the book with its years, id and
  signature, the record sought (e.g. the burial of Anna Kowalska, Przykładowo, 1891–1901), what it would settle (her age at
  death, so which of two baptisms is hers) and what free indexes already give (FamilySearch often indexes the same books while
  their images stay restricted). Add each new lead the day it appears; buy a pass when the list fills a month, read the name
  lists first and the registers in order of priority, and mark each entry done with its source ID.
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
