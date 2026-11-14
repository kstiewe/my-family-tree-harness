# IPN archival inventory (Inwentarz archiwalny IPN)

[inwentarz.ipn.gov.pl](https://inwentarz.ipn.gov.pl/) — the online catalogue of the archive of the
Institute of National Remembrance (Archiwum IPN): about 3 million unit descriptions of records of the
communist-era security and police services, courts and prosecutors, prisons, the army and wartime
investigations. Free, no account. It holds **no scans**, but the unit titles of personal files carry the
person's **father's given name and full date of birth** — often enough to identify a 20th-century
relative and to learn where a file about them is kept.

## What is in it (checked 2026-11)

Typical unit titles, each with "imię ojca" (father's name) and "ur." (date of birth):

- personnel files of officers and employees: police (MO), security service (UB/SB), prison service
  (SW), volunteer reserve police (ORMO) — with the places of service;
- **passport files** ("akta paszportowe", 1950s–1980s) — questionnaires with parents and addresses;
- court and prosecutor files, investigations, prisoners' files;
- **proceedings to declare a person dead** ("uznanie za zmarłego", late 1940s–1960s) — the usual way
  missing soldiers, deportees and war victims were declared dead; the file names the person, the
  father and often the last known whereabouts;
- witness statements of Nazi crimes (with maiden names and other surnames).

## Searching

- `https://inwentarz.ipn.gov.pl/szukaj?fraza=<surname>` — the phrase searches titles and descriptions;
  "Kowalski Jan" finds units containing both words (not necessarily as one person). Further pages:
  `&page=1`, `&page=2` … (10 results per page).
- The result page can be fetched and parsed in the browser console: take `textContent` of the
  `DOMParser` document and split on "Sygnatura IPN … Tytuł … Daty skrajne" (the `innerText` of a parsed
  document has no line breaks).
- "pokaż opis j.a" opens the unit page (`/node/<id>`): number of volumes and pages, the archive branch
  (e.g. "Oddziałowe Archiwum IPN w <city>") and the creator's signature.
- A surname search also returns persons whose title mentions a place or a pseudonym with that word
  (a codename "Kowalski", a village "Kowalewo") — read each title.

## Using a hit

- Match on the father's name, the date of birth and the places of service against what the family
  knows. A personnel file of a son can confirm his date of birth and, through its questionnaire and
  CV, give the **mother's maiden name** and sometimes the parents' dates and places of birth — a way
  back to a grandmother whose own records are not online.
- Access: "Dodaj do kwerendy" on the unit page builds a report and explains how to apply. Files of a
  deceased person are released to close relatives and for research; third-party data may be redacted.
  Applying is the user's decision — the agent only prepares the reference.

## Traps

- Do not search for **living persons** (most people born after the 1920s in these files may still be
  alive). Search a surname only to find deceased relatives, and do not follow up hits on persons who
  may be living.
- The catalogue is still growing; no hit does not mean no file.
- Titles are typed from the files: dates can be wrong by a day and names can be misspelt.
