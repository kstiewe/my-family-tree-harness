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
   For several searches in a row, load the home page in a hidden `iframe`, do the same inside it and read the results page
   from the frame once it has loaded; the tab itself stays where it is. The left column of the results page counts the hits
   per archive and per decade — read it before the list.
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
- **A reconstructed duplicate may be the only scanned copy**: when the main register of a year shows 0 scans, look in the
  unit list for a "wtóropis [odtworzone]" unit that spans several years. It is often scanned: a Polish printed form, "(–)"
  where the signatures were, about one record per scan. A marriage of 1892 can be there although its own unit is not.
- **One office, two descriptions**: an office may be catalogued twice under neighbouring fonds IDs, one with 0 scans and
  one with scans. Search the office's name and open every hit before you conclude that the books are not online.
- **The office is not always named after the parish**: the civil registry office of a parish village can sit in a
  neighbouring village (Meyers Gazetteer gives the Standesamt of each place, see [gazetteers.md](gazetteers.md)); a fonds
  described as "vacat … włączony do zespołu X" points to the fonds that holds the books of an office that was dissolved.
- **Unit ids of one parish need not follow the years**: a unit for another period can sit between two consecutive years
  (a unit "1880–1905" between 1846 and 1847). Check the signature and the dates of each unit before relying on its id.
- **Dark microfilm duplicates** (light writing on a dark background): turn the image to greyscale and stretch the contrast
  (autocontrast) before reading. Find the yearly index pages on a contact sheet built from the `_max` images; the `_mid`
  thumbnails are too dark to tell index pages from records.

## Settlers after 1945: repatriation registers (checked 2026-11)

Families that settled in a new place in 1945–1950 passed through the State Repatriation Office (PUR). In the fonds of a PUR
voivodeship branch each district branch is a series of its own (`…/13.1/…`, `…/13.2/…` …). Besides reports and accounts, a
district series can hold the registers that name the settlers: "Książka meldunkowa repatriantów" (arrivals in order, numbered),
registration books of repatriates ("… rejestracyjna repatriantów"), "Listy imienne osadników", "Ewidencja wydanych
zaświadczeń" and an alphabetical
**"Skorowidz"** to the books. Such registers usually have a column for the place the family came from — the missing link for
a family whose earlier records are elsewhere.

- **Finding the series**: a voivodeship fonds can have over 3000 units. List it in the browser (`_Zespol_delta=100`, 30-odd
  pages, a pause between pages), keep the rows and filter them by the district town; the signature shows the series
  (`…/13.7/2345`). Units of the voivodeship branch outside the district series (lists of a staging point, lists of people
  resettled in 1947) can name the same families.
- **The district office's own fonds** (starostwo, 1945–1950) and the fonds of the communes (gminna rada narodowa) of the
  first years hold "sprawy przesiedleńcze", settler lists and the farm census of 1950; a commune that existed only in
  1945–1946 can have a fonds of its own under the village's name.
- **None of these units had scans.** Prepare a search request (kwerenda) for the user: archive, fonds and signature, the
  index first, then the books, with each person's name, date of birth and the village they settled in.

## Reading a whole book without an index (verified 2026-11)

When a register has no name index and the record you need could be anywhere in a year (or in several years), read one
line of every record instead of every page:

- **Collect the scan list inside the site.** Requests from a script outside the browser get a bot-protection page instead of
  the unit page; `fetch` from a tab of the site works (the unit pages, 20 thumbnails each). The image host
  (`photos.szukajwarchiwach.gov.pl/<hash>_max`) also answers plain downloads, but slowly — load images in the browser.
- **Show a mosaic of cropped bands**: replace the page with boxes (`overflow:hidden`), each holding one scan positioned so that
  only the line you need is visible, with the scan number as a label. At about half size, 60–120 records fit in one
  screenshot and names remain readable; re-render a doubtful box at full size before deciding.
- **Which line**: a death register — the line "und zeigte an, daß [name of the deceased]"; a marriage — two bands, the groom
  ("1. der …") and the bride ("2. die …"); a birth — the parents' lines ("daß von der … Ehefrau des …"), because the person
  reporting a birth in a town was often the midwife ("die Hebamme …"), not the father.
- **In village offices the father usually reported the birth himself**, so a band of the reporter line ("der Arbeiter Jan
  Kowalski, wohnhaft zu …") finds a family quickly; main registers of small offices often hold one record per scan with a
  constant offset (scan = record number + 2 or 3) within a year.
- **Left and right pages** of a book are offset differently (binding margin): calibrate the band on one odd and one even
  scan, and on scans of each new book — the image size can differ between offices and years.
- **Calibrate every year's book anew.** Render four consecutive scans at full width first and read off where the line you
  need starts on the odd and on the even scans. In one office the shift between odd and even scans was about a quarter of
  the page width, the line moved by one line height from year to year, and the side that is shifted swapped between years.
  Position the image by its real proportions (natural width and height), not by an assumed page size.
- **When the band shows the wrong line**, the clerk's wording changed: a midwife's "in ihrer Gegenwart von der …" pushes the
  mother's name to the end of the line and into the next one. Use a two-line band for those records, or re-read them singly.
- **Spellings vary within one family** (a Kowalski written "Kowalewski", a Przykładowski written "Przikladowsky" in a
  child's record): watch for the first letters and the given names of the parents, not for one exact spelling.
- Example: a death in the Kowalski family was indexed elsewhere with a page number that pointed to the wrong scan; a band
  review of the whole book found the record near the end, together with other records of the family the index had missed.

## Reading old German handwriting (Kurrent)

"Thomas" can look like "Ijomas": capital T resembles J or G. Compare with letters of known words
(month names, "geboren", "katholisch") on the same page.

## Saving a scan (verified 2026-11)

The viewer's right-hand panel has "Download" → "Download in jpg"; the file comes from
`/o/pliki-api/pliki/pobierzplikjpeg/<scan id>`, so a scan can be saved by opening that address in the signed-in
browser (one scan at a time, a few seconds apart; a repeated request for the same scan may answer 503). The scan id is
not `first id + scan number − 1` in every unit — ids are consecutive in some units and jump or run backwards in others
(a Congress-Poland duplicate book, for instance). Read the real id from the unit page: fetch the unit address with the
page-size parameter `_Jednostka_delta=200` in the browser tab, parse each `.jednostka-skan` element (its text is
"number id") and look the scan number up. The saved file is named `<archive>_<fonds>_0_-_<unit>_<scan id>.jpg`; rename it
to `<archive>_<fonds>_0_<unit>_s<scan number>.jpg` so that the name carries the number the signature in the source uses.
Check one scan per unit against the record before saving the rest.

The full-size image is also served without a login from `https://photos.szukajwarchiwach.gov.pl/<hash>_max`; the hash of
each scan appears in the unit pages (`_Jednostka_cur=N`, 20 scans per page). Several such images can be fetched from the
shell (`curl`) and read locally, which is faster than the viewer when a whole sequence of records has to be checked.

## Outages

The search sometimes answers "Portlety jest tymczasowo niedostępny" or "Brak wyników" for everything;
a few hours later it works. Retry later and note the outage in the log.

After about 60 full-size downloads in a row the image host answered scripted requests (curl) very slowly — over a minute
per image — while the same images still loaded in the browser. Then read the images in the browser at full width instead
of downloading them, and keep downloads to the records you cite.

**Ranking pages by a script**: the `_mid` thumbnails are served with CORS headers, so a script in a tab of the site can draw
them on an `OffscreenCanvas` and measure them (brightness, the number of ruled vertical lines) to rank the pages most likely
to be index tables. In books of the Polish period (before 1868) this gave many false hits; check the ranked pages by eye.

## Browser window and screenshots

An agent's browser window may be 1024×768 with screenshots scaled to 800×600: size an image
container to the window (e.g. a 1024×768 `div` with `overflow:hidden`), otherwise the screenshot
shows only its top-left part. Size the container from `innerWidth`/`innerHeight` rather than fixed numbers.
When the browser pane is narrow, an emulated window size is shrunk to fit and the handwriting becomes
unreadable: clear the emulation, show the scan 1.3–1.5× wider than the window and take a region screenshot
(the `zoom` action), which keeps the pixels unscaled. (Verified 2026-11.)
