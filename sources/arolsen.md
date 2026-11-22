# Arolsen Archives

[collections.arolsen-archives.org](https://collections.arolsen-archives.org) — the online archive of
the former International Tracing Service: documents on about 17.5 million people persecuted or
displaced by Nazi Germany, and on foreigners in Germany 1939–1950. Useful for anyone from the
territories annexed by Germany in 1939 (Pomerania, Greater Poland, Silesia): forced labourers,
camp prisoners, people conscripted into the Wehrmacht who ended up in post-war lists, displaced
persons (DP) after 1945. Free, no account.

## Searching (checked 2026-11)

- `https://collections.arolsen-archives.org/en/search?s=<surname>` runs the search on load;
  `…/en/search/person?s=…` and typing into the field often do not. Wait 5–7 s for the results.
- Two lists: **People** (name, given name, maiden name, place and date of birth) and **Topics**
  (document groups: "Personal file of …", "Tracing and documentation case no. … for …").
  The preview shows 5 people; "Show all search results" opens the full list (25 per page).
- **In a narrow browser window the People table shows only the name columns**; widen the window
  (about 1600 px) to see maiden name, place and date of birth. The full list pages by 25 with the
  arrows under the table. (Checked 2026-11.)
- Search the surname alone; with two words ("Kowalski Jan") the search is strict and often
  returns nothing. When the surname alone gives hundreds of fuzzy matches, add the given name
  ("Kowalska Leokadia"): a hit is then reliable, and no hit proves little. Polish letters are folded (Kowalska = KOWALSKA), but spelling variants are not:
  also try the German spelling (Kowalsky, Nowack).
- **Dates are month/day/year in the English interface** ("03/25/1910" is 25 March 1910). Write a filter for a known
  date of birth in that order, or test both orders when the day is 12 or less.
- Until the search has run, the counters show the whole archive (tens of millions of people): wait for a count that fits
  the query before reading the list. (Checked 2026-11.)
- **Given names were Germanized** in wartime documents (Wojciech → Adalbert, Jan → Johann,
  Kazimierz → Kasimir, and sometimes a different German name altogether). Match on the date of birth and
  the home town rather than on the given name.
- A town alone in a "born in" column may stand for the district (Kreis) of that name: a village in
  "Landkreis Przykładowo" can be written just "Przykładowo". Check whether the same row writes the district
  explicitly elsewhere ("… Krs. Przykładowo") before moving a birth from the village to the town.
- Place names appear in German and are often misheard or misspelt by the clerk (a "Th" written as
  "D", a vowel changed). Keep a list of the German names of the family's towns at hand.

## Opening documents

- On the first document the site shows a **declaration of consent** (use of sensitive personal
  data under the applicable law) with "I agree". Accepting it is the user's decision: ask before
  ticking it. After that, documents open in a viewer with a "DeepLink"
  (`…/en/document/<DocID>`).
- The welcome dialog with the same declaration can appear already on the search page (checked 2026-11). The results
  load behind it, and the People list can be read from the page without ticking anything: each `tr` gives the archive
  unit, surname, given name, maiden name, place and date of birth. "Show all search results" opens 25 rows a page; the
  next page is the button whose `aria-label` contains "next". Opening a document still needs the declaration.
- The thumbnails on a person's record page (`…/search/person/<id>`) are already the full images: their
  `img` addresses end in `…/001.jpg`, `…/002.jpg`, so a card can be read without opening the viewer.
- The images are plain JPEGs on `collections-server.arolsen-archives.org/…/001.jpg`; open one in its
  own tab and enlarge it with a style (`width:2000px; height:auto; max-width:none; position:absolute`)
  to read typed lists.
- **Tracing and documentation (T/D) cases** created in the 1990s–2000s (compensation claims) often
  show no images ("parts of the file are not displayed for data protection reasons"); the title
  still gives the name, the date of birth and sometimes a later married name.

## What the documents give

- **Wartime and post-war lists of foreigners** (2.1.x, by German district): name, date and place of
  birth, home town ("Heimatort"), unit or employer, dates of stay — e.g. a hospital list naming a
  conscript's regiment and the dates he was treated.
- **DP files** (3.2.x, CM/1, "Fragebogen für DP", "Resettlement Record"): date and place of birth,
  last address before deportation, occupation, languages, family members travelling along, and
  sometimes the **number of the birth certificate** ("Birth certificate № 123/1921 Przykładowo"),
  which points straight to the civil registry record.
- **Camp files** (Stutthof, Dachau …): registration cards with parents' names and address.
- Parents are named only in some document types (camp registration, some CM/1 forms); the lists
  of foreigners do not name them.

- **The "Maiden Name" column identifies wives.** A woman listed under the family surname with a
  different maiden name (e.g. "NOWAK Maria, maiden name KOWALSKA") married into the family; open her
  record — post-war civil documents (e.g. a German copy of a marriage certificate, 1945–1950) name the
  husband with his date and place of birth.
- T/D case titles use the name the claimant gave in the 1990s; maiden names appear in the search when
  the claimant later married ("PRZYKŁADOWA, ANNA" found under "Kowalska"). A file under the family
  surname can therefore be a daughter or a wife — compare the day and month of birth with the other
  records before treating her as a sibling.
- The DP questionnaire ("Fragebogen für DP", 3.2.1.1) asks for the address on 31 August 1939, the date
  of leaving home, relatives living in Germany and documents held (e.g. a birth certificate from the
  home registry), but not for parents.

## Traps

- One person often has several records under slightly different dates of birth (a day or a month
  apart): treat a one-day difference from the family's date as the same person if the home town
  matches, and say so in the notes.
- The server sometimes answers with an IIS error page ("iisnode encountered an error"); retry later.
