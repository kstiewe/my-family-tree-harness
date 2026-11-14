# Digital libraries: newspapers and address books with full text

Regional digital libraries (most run on the dLibra software) hold interwar newspapers, official
gazettes and address books with an OCR text layer. They are a source of their own when the civil
registry books of the 1920s–1930s are still closed or not scanned: many town papers printed the
weekly **civil registry report**, and address books show who lived where.

Checked 2026-11:

| Library | Region | Notes |
|---|---|---|
| [KPBC](https://kpbc.umk.pl) | Kuyavia-Pomerania | interwar dailies, municipal weeklies, parish bulletins, address books; full text |
| [PBC](https://pbc.gda.pl) | Gdańsk Pomerania | full text with snippets ("dopasowań w treści"), but mostly post-war press |
| [Polona](https://polona.pl) | national | full-text search in many newspapers |
| other dLibra libraries (WBC Poznań, ŚBC, RCIN …) | regional | same software, same techniques |

## Full-text search

- URL (dLibra 6): `https://<library>/dlibra/results?q=<words>&action=SimpleSearchAction&type=-6&p=0`;
  `&ipp=64` gives 64 hits per page. Several words must all occur in the publication, not next to
  each other.
- The search **stems and fuzzes**: "Kowalska" and "Kowalski" give different, overlapping lists, and
  a rare surname can match a common word. Treat every hit as a candidate and read the page.
- Search the surname alone first (a few hundred hits is fine), then narrow with a town name; read
  the titles and dates of the hits before opening anything.
- PBC shows a snippet of the matching text in the result list — enough to skip most hits.

## Reading the text of a publication

- The content page `…/publication/<p>/edition/<e>/content` embeds a viewer. For DjVu it is
  `…/dlibra/applet/publication/<p>/edition/<e>?handler=djvu_html5` (`&p=<page>` opens a page). The
  viewer has an invisible **text layer**: select the whole `body` with a Range and read
  `getSelection().toString()`; switch pages with the second `<select>` (page list) and repeat. Only
  pages already rendered have text, so wait 2–3 s per page. In a script keep each call under the
  tool's time limit: start the loop in the background, store the result in `window`, read it later.
- For PDFs the content page embeds `/Content/<e>/PDF/<file>.pdf`; the PDF usually has a text layer
  (`pdftotext -layout`, then grep). Address books are large (100–300 MB) — fetch them into the
  scratchpad, never into the project.
- OCR errors: letters split by stray dots or hyphens ("Ko.walski", "Kowal- ski"), "ł" read as "l",
  Polish letters lost. Use loose regular expressions (`Kowal|K\W?o\W?w\W?a\W?l`) and confirm on the
  page image.

## What the newspapers contain

- **Weekly civil registry report** ("Z Urzędu Stanu Cywilnego w …"), for example in municipal
  weeklies: the period ("w czasie od 3. do 9. marca"), counts of births, deaths and marriages, then
  - "Urodzenie zgłosili: synów: … córek: …" — the **fathers** who registered a son or a daughter that
    week (not the children's names). Illegitimate births appear **only as a number**
    ("Nieślubnych 3"), so an absent father proves nothing for a child born out of wedlock.
  - "Zmarli:" — names with exact ages ("Jan Kowalski 47 l. 2 m.") and, for married women, maiden
    names ("Anna z Nowaków Kowalska").
  - "Ślub zawarli:" or banns — couples with the bride's name.
  Registration was due within a week of the birth, so a father who registered a son in the week of
  3–9 March most likely had a son born in late February or early March. Check the neighbouring weeks too.
- **Court reports, accidents, obituaries, election lists** (candidates with occupation and street
  address), lists of jurors, licences.
- **Parish bulletins** (e.g. "Wiadomości Kościelne") list baptisms, marriages and funerals of one
  parish.

## Address books

- Two kinds of lists: **alphabetical** (surname, given name, occupation, street) and **by street and
  house** (all heads of household in one building — people at the same address are often parents and
  adult children).
- Only heads of household and people with an occupation are listed: wives, children and lodgers
  usually are not. A missing name means little.
- Compare several years: the same person changes address and job; two people with the same name
  appear as "— Jan" lines under one surname.

## Traps

- A namesake is likely in a town: count how many men of the surname appear in the reports and
  address books before attributing a record.
- The full-text index and the viewer's text layer may come from different OCR runs: a hit in the
  search can be invisible to a regex on the viewer text, and the reverse.
