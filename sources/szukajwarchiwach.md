# Szukaj w Archiwach

[szukajwarchiwach.gov.pl](https://www.szukajwarchiwach.gov.pl) — scans published by the Polish
state archives. There are no name indexes: you find the **fonds** (zespół) of a parish or civil
registry office, then the **unit** (jednostka, one book), then the **scan**. Indexes that point to
a book: Geneteka "Uwagi", the PomGenBaza "Księga" column.

## From an office to a scan (verified 2026-11)

1. **Search by the name of the office**, e.g. "Urząd Stanu Cywilnego w Przykładowie" (Prussian
   partition: the Standesamt) or "Akta stanu cywilnego Parafii Rzymskokatolickiej w Przykładowie".
   A signature (`10/0000/0/00`) gives 0 results. URLs such as `wyszukiwarka?q=…`,
   `wyniki-wyszukiwania?q=…` or `_Wyszukiwarka_query=…` do **not** run a search: type into the field —
   on the home page `_Wyszukiwarka_INSTANCE_…_keywords`, on the results page `_Result_keywords` and
   the button `_Result_search_again`. The ids may change; find them via the "Szukaj" button.
   From a script: set the value of the home-page field and call `form.requestSubmit()` on its form —
   the results page lists the fonds as links `/zespol/-/zespol/<id>` (checked 2026-11).
2. **Two kinds of hits.** A row like "Przykładowo, gmina …" is a description from the PRADZIAD
   database (`_Zespol_id_zespolu=…`), without scans. The real fonds has the address
   `/zespol/-/zespol/<id>`; on its page check "Liczba skanów" — 0 means nothing is online.
3. **Units** (20 per page):
   `https://www.szukajwarchiwach.gov.pl/zespol/-/zespol/<id>?_Zespol_javax.portlet.action=zmienWidok&_Zespol_nameofjsp=jednostki&_Zespol_delta=20&_Zespol_resetCur=false&_Zespol_cur=<page>`
   (`_Zespol_delta=100` gives 100 per page; parse the `tr` rows with DOMParser).
4. **A unit** (book): `/jednostka/-/jednostka/<id>`. Thumbnails are paged by 20:
   `?_Jednostka_delta=20&_Jednostka_resetCur=false&_Jednostka_cur=<page>&_Jednostka_id_jednostki=<id>`.
   In the DOM each thumbnail is `.jednostka-skan` with its number in `.number-of-scan` and the image
   `photos.szukajwarchiwach.gov.pl/<hash>_mid`.
5. **Full resolution**: replace `_mid` with `_max` (1058×1552 px; `_big` and `_full` give a thumbnail).
   Open the image in its own tab and enlarge it with a style (`width:1600px;max-width:none;
   position:absolute;left:-100px;top:-400px`), then move `top`. The built-in scan viewer zooms in
   small steps and is slow.
6. **Finding a record**: in civil registry books one record usually takes one scan, shifted by a few
   scans (cover, microfilm cards). Estimate the position from the record number, then read the record
   number on the scan. The slider order may differ from the thumbnail numbering — trust `.number-of-scan`.
   Marriage records usually take **two scans** (two pages: the couple, then the witnesses), so record N sits
   near scan 2N + offset. A strip of the top of several scans (the helper `swaStrip`) shows the record
   numbers at a glance; start the strip lower when the number is printed below the page header.
7. **Margin notes** can change the content of a record ("Muß heißen Sophie" — "should read Sophie")
   or belong to the neighbouring record: always read the margin and check the record number next to it.

Helpers: [szukajwarchiwach.js](szukajwarchiwach.js) — list the scans of a unit with their
full-resolution URLs; show a strip of several scans in one screenshot.

## Fonds IDs without the search

In some archives the civil registry fonds have consecutive IDs in signature order. Knowing one pair
(ID₀, signature₀) you can estimate ID ≈ ID₀ + (signature − signature₀), with gaps of up to ±5:
fetch `/zespol/-/zespol/<id>` for a few neighbouring IDs and check "Sygnatura" and "Liczba skanów"
in the text. Record the pairs you have verified in the workspace notes.

The same works for **units inside one fonds**: their IDs often follow the signatures (unit ID ≈ ID₀ +
(signature − signature₀)). Fetch `/jednostka/-/jednostka/<id>` and check the "Sygnatura" in its text before
relying on it. (Verified 2026-11.)

## Coverage

- Civil registry books are online only up to the 100/110-year limit **at the time of digitisation** —
  for many offices about 1907, even when the description says 1874–1914.
- A fonds with "Liczba skanów: 0" is described but not digitised: order a copy from the archive.
- **Check per unit, not per fonds**: a fonds with thousands of scans may have only some years online
  (e.g. births of a few single years scanned, the years in between and the later decades not). The unit list (`delta=100`)
  shows the number of scans of every book; books of the 1920s are often "rejestr boczny" (the duplicate)
  without scans, while the main register is still in the civil registry office.
- **Duplicate registers (Neben-Register) may have no name index** at the end of the year; one marriage
  record then takes one double-page scan and the book has to be read record by record.

## Reading old German handwriting (Kurrent)

"Thomas" can look like "Ijomas": capital T resembles J or G. Compare with letters of known words
(month names, "geboren", "katholisch") on the same page.

## Outages

The search sometimes answers "Portlety jest tymczasowo niedostępny" or "Brak wyników" for everything;
a few hours later it works. Retry later and note the outage in the log.

## Browser window and screenshots

An agent's browser window may be 1024×768 with screenshots scaled to 800×600: size an image
container to the window (e.g. a 1024×768 `div` with `overflow:hidden`), otherwise the screenshot
shows only its top-left part. Size the container from `innerWidth`/`innerHeight` rather than fixed numbers.
When the browser pane is narrow, an emulated window size is shrunk to fit and the handwriting becomes
unreadable: clear the emulation, show the scan 1.3–1.5× wider than the window and take a region screenshot
(the `zoom` action), which keeps the pixels unscaled. (Verified 2026-11.)
