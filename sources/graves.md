# Grave databases

Useful for 20th-century deaths, which civil registry offices hold for 80 years. Coverage is patchy:
many rural parish cemeteries are not online at all, so a negative result means little.

## Grobonet

`https://grobonet.com/wyszukiwanie?imie=<given>&nazw=<surname>&wojewodztwo=<voivodeship>&miasto=<town>` —
needs a given name or a voivodeship, and `miasto` must be a name from its own database.
**Without a given name** it needs the voivodeship and returns a list of cemeteries with the number of
hits; each cemetery is a link `/wyszukiwanie?nazw=X&wojewodztwo=Y&cmentarz=…&idcmproj=N` (persons as
"Given SURNAME YYYY-MM-DD — YYYY-MM-DD"). After about 15 quick requests the service answers "Brak
dostępu z uwagi na duże obciążenie systemu" (blocked because of load) — pause and query less.
(Verified 2026-11.)

## eCmentarze

`https://www.ecmentarze.pl/wyszukaj-pochowanego/szukaj?name=<given>&surname=<surname>` — the whole
country. In a tab on ecmentarze.pl the page can be fetched and parsed: remove `script`/`ins`, and for
each link `grave/detail/N` take the highest ancestor element that contains only that one link — that is
the row of the grave (persons, dates, cemetery). At most 10 graves per result. Collective graves
(e.g. a military cemetery) list hundreds of names — truncate the row text. Helper:
[ecmentarze.js](ecmentarze.js). (Verified 2026-11.)

## Others

- PomGenBaza cemetery indexes: see [pomgenbaza.md](pomgenbaza.md).
- mogily.pl did not open in the agent's browser (2026-11); Find a Grave and BillionGraves rarely have
  Polish rural cemeteries.
- When no database covers the cemetery: the family, a photo of the gravestone, or the civil registry office.

## Municipal cemetery finders (checked 2026-11)

Large cities run their own grave finders for municipal cemeteries (the city's or the municipal cemetery
board's website, "wyszukiwarka grobów"), separate from Grobonet and eCmentarze, with name, years of life
and the date of burial; parish cemeteries in the same city often have a separate finder. Typical form:
surname, given name, optional cemetery, a "Filtruj"/"Szukaj" button and results in a side panel. Useful
for families who settled in the western and northern territories after 1945. Search the surname alone
and read the list, then narrow by given name.
