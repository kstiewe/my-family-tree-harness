"""Polish translation."""

MESSAGES = {
    # ---- dates
    "c. {date}": "ok. {date}",
    "before {date}": "przed {date}",
    "after {date}": "po {date}",
    'invalid date range {value!r} (pattern: "1848..1852")': 'niepoprawny przedział dat {value!r} (wzór: "1848..1852")',
    'invalid date {value!r} (patterns: "1850-03-12", "1850", "~1850", "<1870", ">1845")':
        'niepoprawna data {value!r} (wzory: "1850-03-12", "1850", "~1850", "<1870", ">1845")',

    # ---- event labels
    "Birth": "Urodzenie",
    "Baptism": "Chrzest",
    "Death": "Zgon",
    "Burial": "Pogrzeb",
    "Residence": "Zamieszkanie",
    "Occupation": "Zawód",
    "Emigration": "Emigracja",
    "Military service": "Służba wojskowa",
    "Census": "Spis ludności",
    "Confirmation": "Bierzmowanie",
    "Education": "Edukacja",
    "Other": "Inne",

    # ---- languages of documents
    "Polish": "polski",
    "Latin": "łaciński",
    "German": "niemiecki",
    "Russian": "rosyjski",
    "Ukrainian": "ukraiński",
    "Belarusian": "białoruski",
    "Lithuanian": "litewski",
    "Latvian": "łotewski",
    "Czech": "czeski",
    "Slovak": "słowacki",
    "Hungarian": "węgierski",
    "Yiddish": "jidysz",
    "Hebrew": "hebrajski",
    "English": "angielski",
    "French": "francuski",
    "Italian": "włoski",
    "Dutch": "niderlandzki",
    "Swedish": "szwedzki",

    # ---- validation
    "missing file {path}": "brak pliku {path}",
    "{file}: YAML syntax error: {error}": "{file}: błąd składni YAML: {error}",
    "{file}: expected a list at the top level": "{file}: oczekiwano listy na najwyższym poziomie",
    "{file}: expected a mapping at the top level": "{file}: oczekiwano mapy na najwyższym poziomie",
    "{file}, entry {i}: missing id field": "{file}, wpis {i}: brak pola id",
    "{file}: id {id!r} should look like {prefix}0001": "{file}: id {id!r} powinno mieć postać {prefix}0001",
    "{file}: duplicate id {id}": "{file}: zduplikowane id {id}",
    "{ctx}: unknown fields {fields} (typo?)": "{ctx}: nieznane pola {fields} (literówka?)",
    "{ctx}: {value!r} — allowed: {allowed}": "{ctx}: {value!r} — dozwolone: {allowed}",
    "{ctx}.{key}: expected a list [..]": "{ctx}.{key}: oczekiwano listy [..]",
    "{ctx}: expected a mapping {{date: …, place: …}}": "{ctx}: oczekiwano mapy {{date: …, place: …}}",
    "{ctx}: unknown place {id}": "{ctx}: nieznane miejsce {id}",
    "{ctx}: unknown source {id}": "{ctx}: nieznane źródło {id}",
    "{ctx}.{key}: age must be an integer": "{ctx}.{key}: wiek jako liczba całkowita",
    "project.yaml: proband {id} does not exist in persons.yaml": "project.yaml: proband {id} nie istnieje w persons.yaml",
    "{id}: no given name and no surname": "{id}: brak imienia i nazwiska",
    "{ctx}: missing type field": "{ctx}: brak pola type",
    "{id}: child in several families ({families}) — the first one defines the line":
        "{id}: dziecko w kilku rodzinach ({families}) — linię wyznacza pierwsza",
    "{id}: family without spouses (set husband or wife)": "{id}: rodzina bez małżonków (podaj husband lub wife)",
    "{ctx}: unknown person {id}": "{ctx}: nieznana osoba {id}",
    "{ctx}: {id} has sex {sex}": "{ctx}: {id} ma płeć {sex}",
    "{id}: {person} is both a spouse and a child": "{id}: {person} jest jednocześnie małżonkiem i dzieckiem",
    "{ctx}: repeated ID": "{ctx}: powtórzone ID",
    "{id}: missing name": "{id}: brak nazwy",
    "{ctx}: expected [latitude, longitude]": "{ctx}: oczekiwano [szerokość, długość]",
    "{ctx}: expected {{period: …, value: …}}": "{ctx}: oczekiwano {{period: …, value: …}}",
    "{id}: missing title": "{id}: brak tytułu",
    "{ctx}: unknown language code {value!r} (use ISO 639-1, e.g. pl, la, de, ru)":
        "{ctx}: nieznany kod języka {value!r} (użyj ISO 639-1, np. pl, la, de, ru)",
    "{id}: source is not attached to any fact": "{id}: źródło nie jest przypisane do żadnego faktu",
    "{id}: is their own ancestor (cycle in family relations)": "{id}: jest własnym przodkiem (cykl w relacjach rodzinnych)",
    "{id} {name}: death ({death}) before birth ({birth})": "{id} {name}: zgon ({death}) przed urodzeniem ({birth})",
    "{id} {name}: age {age} years — check the dates": "{id} {name}: wiek {age} lat — sprawdź daty",
    "{id} {name}: baptism before birth": "{id} {name}: chrzest przed urodzeniem",
    "{id}: {name} is {age} years old at the marriage": "{id}: {name} w chwili ślubu ma {age} lat",
    "{id}: marriage ({year}) after the death of {name} ({death})": "{id}: ślub ({year}) po zgonie {name} ({death})",
    "{id} {name}: mother's age at the birth = {age} years ({family})": "{id} {name}: wiek matki przy urodzeniu = {age} lat ({family})",
    "{id} {name}: father's age at the birth = {age} years ({family})": "{id} {name}: wiek ojca przy urodzeniu = {age} lat ({family})",
    "{id} {name}: birth ({birth}) after the mother's death ({death})": "{id} {name}: urodzenie ({birth}) po zgonie matki ({death})",
    "{id} {name}: birth ({birth}) after the father's death ({death})": "{id} {name}: urodzenie ({birth}) po zgonie ojca ({death})",
    "{id} {name}: no dates and no living field — treated as living (set living: false if deceased)":
        "{id} {name}: brak dat i pola living — traktowana jako żyjąca (ustaw living: false, jeśli zmarła)",

    # ---- descriptions
    "née {surname}": "z d. {surname}",
    "parish {name}": "par. {name}",
    "{place} (parish unknown)": "{place} (parafia nieustalona)",
    "parish {name}{denomination}": "parafia {name}{denomination}",
    "{place} → parish {name}{denomination}": "{place} → parafia {name}{denomination}",
    "bapt. {event}": "chrz. {event}",
    "bur. {event}": "pochow. {event}",
    "Living person": "Osoba żyjąca",
    "age {age}": "wiek {age}",
    "Family tree": "Drzewo genealogiczne",

    # ---- evidence for estimated years
    "date of birth": "data urodzenia",
    "date of baptism": "data chrztu",
    "age in the death record": "wiek w akcie zgonu",
    "date of death": "data zgonu",
    "age in the marriage record": "wiek w akcie ślubu",
    "date of marriage": "data ślubu",
    "births of children": "urodzenia dzieci",
    "parents' marriage": "ślub rodziców",
    "mother's age": "wiek matki",
    "father's age": "wiek ojca",

    # ---- where to search
    "place of birth": "miejsce urodzenia",
    "place of baptism": "miejsce chrztu",
    "place of death": "miejsce zgonu",
    "place of burial": "miejsce pochówku",
    "place of residence": "miejsce zamieszkania",
    "place of marriage": "miejsce ślubu",
    "(marriages usually took place in the bride's parish)": "(ślub zwykle w parafii panny młodej)",
    "place of birth of the children": "miejsce urodzenia dzieci",
    "place of the parents' marriage": "miejsce ślubu rodziców",
    "place of birth of the first child": "miejsce urodzenia pierwszego dziecka",
    "bride: {label}": "panna młoda: {label}",
    "groom: {label}": "pan młody: {label}",
    'Geneteka: {kind} "{who}" {start}–{end}, {region}': "Geneteka: {kind} „{who}” {start}–{end}, {region}",
    "Search: {where} — {why}": "Szukaj: {where} — {why}",
    "Fill in geneteka_region of the place in places.yaml to get ready-made Geneteka links.":
        "Uzupełnij geneteka_region miejsca w places.yaml — pojawią się gotowe linki do Geneteki.",

    # ---- research hints
    "Parents of a living person are missing — ask the family or order a full copy of the birth certificate from the "
    "civil registry office (it names the parents). Living persons are never searched online.":
        "Brak rodziców osoby żyjącej — zapytaj rodzinę albo zamów w USC odpis zupełny aktu urodzenia (podaje rodziców). "
        "Danych osób żyjących nie wyszukujemy online.",
    "Task: {task}": "Zadanie: {task}",
    "This person / link is a hypothesis — confirm it with a primary source (a scan of the record).":
        "Osoba / powiązanie to hipoteza — potwierdź źródłem pierwotnym (skan aktu).",
    "The link is probable — worth confirming with a second source.": "Powiązanie prawdopodobne — warto potwierdzić drugim źródłem.",
    "End of line: no parents — find the birth/baptism record (it names the parents, usually also the mother's maiden name).":
        "Koniec linii: brak rodziców — odnajdź akt urodzenia/chrztu (podaje rodziców, zwykle też nazwisko rodowe matki).",
    "Father missing — the birth/baptism record will name the missing parent.": "Brak ojca — akt urodzenia/chrztu poda brakującego rodzica.",
    "Mother missing — the birth/baptism record will name the missing parent.": "Brak matki — akt urodzenia/chrztu poda brakującego rodzica.",
    "Birth without a source — confirm it with a birth/baptism record.": "Urodzenie bez źródła — potwierdź aktem urodzenia/chrztu.",
    "Place unknown — marriage and death records or family accounts give it.":
        "Miejsce nieznane — podają je akty ślubu i zgonu albo relacje rodzinne.",
    "Estimated year of birth: {years} (evidence: {basis})": "Szacowany rok urodzenia: {years} (przesłanki: {basis})",
    "— WARNING: the evidence is contradictory, check the dates": "— UWAGA: przesłanki są sprzeczne, sprawdź daty",
    "Birth records younger than 100 years are kept by the civil registry office (USC), not the archive — request a full copy.":
        "Akta urodzeń młodsze niż 100 lat są w USC, nie w archiwum — wniosek o odpis zupełny.",
    "Often faster via the marriage record: it usually names the parents of the couple (in Congress Poland from 1808 also "
    "age and place of birth).":
        "Często szybciej przez akt ślubu: zwykle podaje rodziców nowożeńców (w Kr. Polskim od 1808 także wiek i miejsce urodzenia).",
    "Maiden name unknown — the marriage record, the children's birth records and the death record give it.":
        "Nieznane nazwisko rodowe — podają je akt ślubu, akty urodzeń dzieci i akt zgonu.",
    "Death without a source — confirm it with a death record.": "Zgon bez źródła — potwierdź aktem zgonu.",
    "No death record (it gives the age, often the parents and the spouse).": "Brak aktu zgonu (podaje wiek, często rodziców i małżonka).",
    "Place unknown — search the parish of the last residence (e.g. where the youngest child was born).":
        "Miejsce nieznane — szukaj w parafii ostatniego zamieszkania (np. urodzenia najmłodszego dziecka).",
    "Years to search: {start}–{end}": "Okres poszukiwań: {start}–{end}",
    "Death records younger than 80 years are kept by the civil registry office (USC).": "Akta zgonów młodsze niż 80 lat są w USC.",
    'Women usually appear in death records under the husband\'s surname (e.g. "Kowalska née Nowak").':
        "Kobiety w aktach zgonu zwykle pod nazwiskiem męża (np. „z Nowaków Kowalska”).",
    "Facts without a source: {facts}": "Fakty bez źródła: {facts}",
    "The union is a hypothesis — confirm it with the marriage record or the children's birth records.":
        "Związek to hipoteza — potwierdź aktem ślubu lub aktami urodzeń dzieci.",
    "Husband unknown — the children's birth records name both parents.": "Nieznany(-a) mąż — akty urodzeń dzieci podają oboje rodziców.",
    "Wife unknown — the children's birth records name both parents.": "Nieznany(-a) żona — akty urodzeń dzieci podają oboje rodziców.",
    "Place unknown — marriages usually took place in the bride's parish.": "Miejsce nieznane — ślub zwykle w parafii panny młodej.",
    "Marriage records younger than 80 years are kept by the civil registry office (USC).": "Akta małżeństw młodsze niż 80 lat są w USC.",
    "The marriage record usually names the parents of the couple (in Congress Poland from 1808 also age and place of "
    "birth) — it lets you jump a generation.":
        "Akt ślubu zwykle podaje rodziców nowożeńców (w Kr. Polskim od 1808 także wiek i miejsce urodzenia) — pozwala "
        "przeskoczyć pokolenie.",
    "Marriage without a source — find the marriage record.": "Ślub bez źródła — odnajdź akt ślubu.",
    "No marriage record.": "Brak aktu ślubu.",
    "parish (parish)": "parafii (parish)",
    "Geneteka region (geneteka_region)": "regionu Geneteki (geneteka_region)",
    "partition (partition)": "zaboru (partition)",
    "coordinates (coords)": "współrzędnych (coords)",

    # ---- Geneteka
    "births": "urodzenia",
    "marriages": "małżeństwa",
    "deaths": "zgony",
    "none": "brak",
    'Parish "{name}" in region {region}: {n} matches ({names}). Be more specific.':
        "Parafia „{name}” w regionie {region}: {n} dopasowań ({names}). Doprecyzuj.",
    "Parish {name}: no {kind} indexes ({years}).": "Parafia {name}: brak indeksów typu {kind} ({years}).",
    "ids B/M/D": "id U/M/Z",
    "(exact)": "(dokładnie)",
    "(with variants)": "(z wariantami)",
    'Geneteka · "{surname}" {mode} — index entries per region:': "Geneteka · „{surname}” {mode} — indeksy w regionach:",
    "region": "region",
    "born": "urodz.",
    "died": "zgony",
    "marr.": "małż.",

    # ---- generations
    "proband, siblings and cousins": "proband, rodzeństwo i kuzyni",
    "parents": "rodzice",
    "grandparents": "dziadkowie",
    "great-grandparents": "pradziadkowie",
    "great-great-grandparents": "prapradziadkowie",
    "peers of the proband's children": "rówieśnicy dzieci probanta",
    "peers of the proband's grandchildren": "rówieśnicy wnuków probanta",
    "peers of the proband's great-grandchildren": "rówieśnicy prawnuków probanta",
    "{n} generations back": "{n}. pokolenie wstecz",
    "descendant generation {n}": "{n}. pokolenie potomków",
    "Generation {n}": "Pokolenie {n}",
    "Younger generation": "Młodsze pokolenie",
    "b. {years}": "ur. {years}",
    "- generation {n} ({name}): {have}/{total}": "- pokolenie {n} ({name}): {have}/{total}",

    # ---- reports
    "Generated by scripts/build.py — do not edit by hand.": "Wygenerowano przez scripts/build.py — nie edytuj ręcznie.",
    "# Gaps in the data and research suggestions": "# Luki w danych i sugestie poszukiwań",
    "_Generated {date} by `scripts/build.py` — do not edit by hand._": "_Wygenerowano {date} przez `scripts/build.py` — nie edytuj ręcznie._",
    "🔴 priority · 🟠 important · ⚪ supplementary. Geneteka links are ready-made queries; always confirm an index hit "
    "on the scan of the record.":
        "🔴 priorytet · 🟠 ważne · ⚪ uzupełnienie. Linki do Geneteki to gotowe zapytania; trafienie w indeksie zawsze "
        "potwierdzaj na skanie aktu.",
    "## Summary": "## Podsumowanie",
    "- persons: {persons}, families: {families}, places: {places}, sources: {sources}":
        "- osób: {persons}, rodzin: {families}, miejsc: {places}, źródeł: {sources}",
    "- ancestors of the proband in the data: {n}": "- przodków probanta w bazie: {n}",
    "**Ends of lines** (ancestors missing one or both parents):": "**Końce linii** (przodkowie bez jednego lub obojga rodziców):",
    "## 1. Ancestors of the proband": "## 1. Przodkowie probanta",
    "_Set `proband` in data/project.yaml to determine the line of ancestors._": "_Ustaw `proband` w data/project.yaml, aby wyznaczyć linię przodków._",
    "## 2. Marriages of the ancestors": "## 2. Małżeństwa przodków",
    "## 3. Other persons and families (collateral relatives)": "## 3. Pozostałe osoby i rodziny (krewni boczni)",
    "_Siblings of ancestors are often the key to a brick wall: their records name the same parents and witnesses._":
        "_Rodzeństwo przodków bywa kluczem do „ściany”: ich akty podają tych samych rodziców i świadków._",
    "## 4. Places to complete": "## 4. Miejsca do uzupełnienia",
    "- `{id}` {name}: missing {fields}": "- `{id}` {name}: brak {fields}",
    "_None._": "_Brak._",
    "## 5. Validation warnings": "## 5. Ostrzeżenia walidacji",
    "# List of ancestors (Kekule numbering)": "# Wykaz przodków (numeracja Kekulego)",
    "_Generated {date} by `scripts/build.py`. Proband = 1; father of person n = 2n, mother = 2n+1._":
        "_Wygenerowano {date} przez `scripts/build.py`. Proband = 1; ojciec osoby n = 2n, matka = 2n+1._",
    "| No. | Gen. | Person | Birth | Marriage (of the parents of no. n/2) | Death | Sources | ID |":
        "| Nr | Pok. | Osoba | Urodzenie | Ślub (rodziców nr n/2) | Zgon | Źródeł | ID |",
    "_? (father of no. {n})_": "_? (ojciec nr {n})_",
    "_? (mother of no. {n})_": "_? (matka nr {n})_",

    # ---- GEDCOM
    "Tree author": "Autor drzewa",
    "Confidence: {value}": "Pewność: {value}",
    "Language of the document: {languages}": "Język dokumentu: {languages}",

    # ---- CLI
    "Persons: {persons} (ancestors of the proband: {ancestors}) · families: {families} · places: {places} · sources: {sources}":
        "Osoby: {persons} (przodkowie probanta: {ancestors}) · rodziny: {families} · miejsca: {places} · źródła: {sources}",
    "ERROR: {message}": "BŁĄD: {message}",
    "warning: {message}": "uwaga: {message}",
    "{n} errors — fix the data; no outputs were generated.": "{n} błędów — popraw dane; wyniki nie zostały wygenerowane.",
    "Outputs in {dir}: {files}": "Wyniki w {dir}: {files}",
    "(public mode)": "(tryb publiczny)",
    "Next free IDs: {ids}": "Następne wolne ID: {ids}",
    "[no. {numbers}]": "[nr {numbers}]",
    "tree.mmd": "drzewo.mmd",
    "ancestors.mmd": "przodkowie.mmd",
    "tree.html": "drzewo.html",
    "tree-artifact.html": "drzewo-artefakt.html",
    "tree.ged": "drzewo.ged",
    "gaps.md": "luki.md",
    "ancestors.md": "przodkowie.md",

    # ---- HTML page (templates/*.html, ⟦…⟧ markers)
    "Whole tree": "Całe drzewo",
    "Ancestors of the proband": "Przodkowie probanta",
    "Search for a person…": "Szukaj osoby…",
    "Search for a person": "Szukaj osoby",
    "direct line of the proband": "linia prosta probanta",
    "collateral relatives": "krewni boczni",
    "hypothesis": "hipoteza",
    "probable": "prawdopodobne",
    "confirmed": "potwierdzone",
    "≈ probable · number in the corner = Kekule number · * birth · † death · ⚭ marriage · click a person to highlight their line":
        "≈ prawdopodobne · liczba w rogu = numer Kekulego · * urodzenie · † zgon · ⚭ ślub · kliknij osobę, by podświetlić jej linię",
    "Tree diagram: drag to pan; the mouse wheel or + and − zooms":
        "Diagram drzewa: przeciągnij, by przesunąć; kółko myszy albo + i − zmienia przybliżenie",
    "Zoom in": "Przybliż",
    "Zoom out": "Oddal",
    "Show the whole tree": "Pokaż całe drzewo",
    "Show the proband": "Pokaż probanta",
    "Click a person in the diagram or in the list.": "Kliknij osobę na diagramie lub na liście.",
    "${ids.length} persons · ${Object.keys(D.sources).length} sources · as of ${D.generated}":
        "${ids.length} osób · ${Object.keys(D.sources).length} źródeł · stan na ${D.generated}",
    "No ancestors to show — set proband in data/project.yaml.": "Brak przodków do pokazania — ustaw proband w data/project.yaml.",
    "No persons in data/persons.yaml.": "Brak osób w data/persons.yaml.",
    "no.": "nr",
    "living person": "osoba żyjąca",
    "Variants:": "Warianty:",
    "Facts": "Fakty",
    "Family": "Rodzina",
    "Parents": "Rodzice",
    "and": "i",
    "unknown": "nieznani",
    "Children:": "Dzieci:",
    "Notes": "Notatki",
    "To research": "Do zbadania",
    "No results.": "Brak wyników.",
    "language": "język",

    # ---- geography: the map page, clusters, migration trails, hints (familytree/geo.py, geomap.py)
    "map.html": "mapa.html",
    "map-artifact.html": "mapa-artefakt.html",
    "geography.md": "geografia.md",
    "geography.json": "geografia.json",
    "{ctx}: {coords} lies outside Poland — latitude and longitude swapped?":
        "{ctx}: {coords} leży poza Polską — zamienione szerokość i długość geograficzna?",
    "coordinates (coords; the map uses the parish's for now)": "współrzędnych (coords; mapa używa na razie współrzędnych parafii)",
    "N": "płn.",
    "NE": "płn.-wsch.",
    "E": "wsch.",
    "SE": "płd.-wsch.",
    "S": "płd.",
    "SW": "płd.-zach.",
    "W": "zach.",
    "NW": "płn.-zach.",
    "birth": "urodzenie",
    "death": "zgon",
    "marriage": "ślub",
    "residence": "zamieszkanie",
    "other event": "inne zdarzenie",
    "Russian partition": "zabór rosyjski",
    "Prussian partition": "zabór pruski",
    "Austrian partition": "zabór austriacki",
    "outside Poland": "poza Polską",
    "partition not recorded": "zabór niewpisany",
    "{place} and surroundings": "{place} i okolice",
    "{place} ({km} km {direction})": "{place} ({km} km {direction})",
    "place of birth of a sibling": "miejsce urodzenia rodzeństwa",
    "place of the spouse": "miejsce współmałżonka",
    "place of a parent": "miejsce rodzica",
    "Map: parishes within {km} km of {place} ({basis}) — check their books too: {list}":
        "Mapa: parafie w promieniu {km} km od {place} ({basis}) — sprawdź też ich księgi: {list}",
    "Map: no other parish within {km} km of {place} is in places.yaml — look up the neighbouring parishes and add them with coords.":
        "Mapa: w places.yaml nie ma innej parafii w promieniu {km} km od {place} — ustal sąsiednie parafie i dodaj je ze współrzędnymi (coords).",
    "Nearest other family cluster: {cluster}, {km} km {direction} (events: {n}, {years}).":
        "Najbliższe inne skupisko rodziny: {cluster}, {km} km {direction} (zdarzeń: {n}, {years}).",
    "## 6. Geography": "## 6. Geografia",
    "- events on the map: {n} (without coordinates: {missing})": "- zdarzeń na mapie: {n} (bez współrzędnych: {missing})",
    "- cluster {id} {label}: events: {n}, {years}": "- skupisko {id} {label}: zdarzeń: {n}, {years}",
    "- places to geocode (most events first): {list}": "- miejsca do zgeokodowania (najpierw te z największą liczbą zdarzeń): {list}",
    "- clusters, migration trails and hints per ancestor: {file}; the map: {map}":
        "- skupiska, szlaki migracji i wskazówki dla każdego przodka: {file}; mapa: {map}",
    "# Geography of the family": "# Geografia rodziny",
    "Context for research: where the family's events happened, clusters of places, migration trails along the lines of "
    "ancestors and where to look for the missing ones. Distances are straight lines; a place without coordinates takes "
    "those of its parish. Everything here is a heuristic for choosing where to search — never evidence. The same data as "
    "JSON: geography.json; on a map: map.html.":
        "Kontekst do poszukiwań: gdzie działy się zdarzenia z życia rodziny, skupiska miejsc, szlaki migracji wzdłuż linii "
        "przodków i gdzie szukać brakujących. Odległości są w linii prostej; miejsce bez współrzędnych dostaje współrzędne "
        "swojej parafii. Wszystko tutaj to heurystyka pomagająca wybrać, gdzie szukać — nigdy dowód. Te same dane jako "
        "JSON: geografia.json; na mapie: mapa.html.",
    "- places with coordinates: {own}, with the parish's coordinates: {parish}, without: {none}":
        "- miejsca ze współrzędnymi: {own}, ze współrzędnymi parafii: {parish}, bez: {none}",
    "- clusters (places within {km} km of a centre): {n}": "- skupiska (miejsca do {km} km od środka): {n}",
    "- events by kind: {list}": "- zdarzenia według rodzaju: {list}",
    "- events by partition: {list}": "- zdarzenia według zaboru: {list}",
    "## Clusters": "## Skupiska",
    "events: {n}": "zdarzeń: {n}",
    "- centre {lat}, {lon}; radius {km} km": "- środek {lat}, {lon}; promień {km} km",
    "- places: {list}": "- miejsca: {list}",
    "- events: {list}": "- zdarzenia: {list}",
    "- ancestors: {list}": "- przodkowie: {list}",
    "- surnames: {list}": "- nazwiska: {list}",
    "- partition: {list}": "- zabór: {list}",
    "_No events with coordinates yet — add `coords` to the places in places.yaml._":
        "_Brak zdarzeń ze współrzędnymi — dodaj `coords` do miejsc w places.yaml._",
    "## Migration trails along the lines of ancestors": "## Szlaki migracji wzdłuż linii przodków",
    "_From the oldest known ancestors of each line down to the proband; each person stands at the place of birth (else "
    "marriage, residence, death); (est.) = estimated year._":
        "_Od najstarszych znanych przodków każdej linii do probanta; każdą osobę reprezentuje miejsce urodzenia (a gdy go "
        "brak: ślubu, zamieszkania, zgonu); (szac.) = rok szacunkowy._",
    "(est.)": "(szac.)",
    "; overall {km} km {direction}": "; łącznie {km} km {direction}",
    "no. {n}": "nr {n}",
    "## Largest moves": "## Największe przenosiny",
    "_Changes of place of at least {km} km — where a line moved, the next generation's records are in another parish (or archive)._":
        "_Zmiany miejsca o co najmniej {km} km — gdzie linia się przeniosła, akta następnego pokolenia są w innej parafii (lub archiwum)._",
    "birth → death": "urodzenie → zgon",
    "parent → child": "rodzic → dziecko",
    "- {km} km {direction}: {a} ({ya}) → {b} ({yb}) — {who}, {what}": "- {km} km {direction}: {a} ({ya}) → {b} ({yb}) — {who}, {what}",
    "## Where to look for missing ancestors": "## Gdzie szukać brakujących przodków",
    "_For each deceased ancestor without a located birth or death or without parents. The reference place is the closest "
    "located clue; neighbouring parishes are only those already in places.yaml — the diocese's list of parishes or "
    "`scripts/geneteka.py --parishes` gives the others._":
        "_Dla każdego zmarłego przodka bez umiejscowionego urodzenia lub zgonu albo bez rodziców. Miejsce odniesienia to "
        "najbliższa umiejscowiona wskazówka; sąsiednie parafie to tylko te, które już są w places.yaml — pozostałe poda "
        "wykaz parafii diecezji albo `scripts/geneteka.py --parishes`._",
    "- missing: {list}": "- brakuje: {list}",
    "estimated birth: {years}": "szacowany rok urodzenia: {years}",
    "- no located clue: add coordinates to the places of this person and of the closest relatives":
        "- brak umiejscowionej wskazówki: dodaj współrzędne miejsc tej osoby i najbliższych krewnych",
    "- reference place: {place} `{id}` — {why}": "- miejsce odniesienia: {place} `{id}` — {why}",
    "(coordinates of the parish)": "(współrzędne parafii)",
    "- parishes within {km} km: {list}": "- parafie w promieniu {km} km: {list}",
    "- family places within {km} km: {list}": "- miejsca rodziny w promieniu {km} km: {list}",
    "- nearest clusters: {list}": "- najbliższe skupiska: {list}",
    "- the same surname elsewhere in the data: {list}": "- to samo nazwisko gdzie indziej w danych: {list}",
    "## Places to geocode": "## Miejsca do zgeokodowania",
    "_Places used by events that the map cannot show: add `coords` (and the source of the coordinates in `notes`), or the "
    "parish when it has coordinates._":
        "_Miejsca zdarzeń, których mapa nie może pokazać: dodaj `coords` (a źródło współrzędnych w `notes`) albo parafię, "
        "jeśli ona ma współrzędne._",
    "- `{id}` {name} — events: {n}": "- `{id}` {name} — zdarzeń: {n}",
    "parish unknown": "parafia nieznana",
    "**Ancestors without any place on the map:** {list}": "**Przodkowie bez żadnego miejsca na mapie:** {list}",
    "Family map": "Mapa rodziny",
    "Map": "Mapa",
    "Poland": "Polska",
    "World": "Świat",
    "Events": "Zdarzenia",
    "Births": "Urodzenia",
    "Deaths": "Zgony",
    "Births and deaths": "Urodzenia i zgony",
    "All events": "Wszystkie zdarzenia",
    "From year": "Od roku",
    "To year": "Do roku",
    "Centuries": "Stulecia",
    "all years": "wszystkie lata",
    "undated": "bez daty",
    "ancestors only": "tylko przodkowie",
    "lines of ancestors": "linie przodków",
    "partition borders": "granice zaborów",
    "Map: drag to pan; the mouse wheel or + and − zooms; click a place to list the people recorded there":
        "Mapa: przeciągnij, by przesunąć; kółko myszy albo + i − zmienia przybliżenie; kliknij miejsce, by zobaczyć zapisane tam osoby",
    "No events with coordinates yet — add coords to the places in data/places.yaml (or to their parishes) and build again.":
        "Brak zdarzeń ze współrzędnymi — dodaj coords do miejsc w data/places.yaml (albo do ich parafii) i zbuduj ponownie.",
    "Show all events": "Pokaż wszystkie zdarzenia",
    "fewer → more events": "mniej → więcej zdarzeń",
    "place": "miejsce",
    "region or country": "region lub kraj",
    "partition border, approx. 1846–1914": "granica zaborów, przybliżona, 1846–1914",
    "coordinates of the parish": "współrzędne parafii",
    "Where the family lived": "Gdzie żyła rodzina",
    "Click a place or a hot spot on the map to list the people recorded there. The colour shows how many of the chosen "
    "events fall in the area; arrows lead from a parent's place to the child's along the lines of ancestors.":
        "Kliknij miejsce albo gorący punkt na mapie, by zobaczyć zapisane tam osoby. Kolor pokazuje, ile wybranych zdarzeń "
        "przypada na okolicę; strzałki prowadzą od miejsca rodzica do miejsca dziecka wzdłuż linii przodków.",
    "Places on the map": "Miejsca na mapie",
    "Back to the selected places": "Wróć do zaznaczonych miejsc",
    "Places: ${ids.length}": "Miejsca: ${ids.length}",
    "Outside the filters: ${hidden} more events": "Poza filtrami: jeszcze ${hidden} zdarzeń",
    "Clusters of places": "Skupiska miejsc",
    "None yet.": "Na razie brak.",
    "Not on the map: places without coordinates: ${D.stats.geocode}, their events: ${D.stats.off} — see ${D.files.context}.":
        "Poza mapą: miejsca bez współrzędnych: ${D.stats.geocode}, ich zdarzenia: ${D.stats.off} — zob. ${D.files.context}.",
    "${D.title} · events on the map: ${D.stats.on} of ${D.stats.on + D.stats.off} · as of ${D.generated}":
        "${D.title} · zdarzeń na mapie: ${D.stats.on} z ${D.stats.on + D.stats.off} · stan na ${D.generated}",
}
