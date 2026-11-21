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
    "Signature": "Podpis",
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
    '{ctx}: expected {{text: "…", source: S0001}}': '{ctx}: oczekiwano {{text: "…", source: S0001}}',
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
    "${n} generations back": "${n}. pokolenie wstecz",
    "descendant generation ${n}": "${n}. pokolenie potomków",
    "Generation ${num}": "Pokolenie ${num}",
    "Younger generation": "Młodsze pokolenie",
    "b. ${span}": "ur. ${span}",
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
    "scans.md": "skany.md",
    "# Local copies of the sources": "# Lokalne kopie źródeł",
    "**Rule:** a source that can be checked (a scan, a photo, a page) is saved in `{dir}/` as soon as it is found and "
    "attached with its `file` field; every new search starts with the local copy.":
        "**Zasada:** źródło, które można sprawdzić (skan, zdjęcie, strona), zapisujemy w `{dir}/` od razu po "
        "znalezieniu i podpinamy polem `file`; każde nowe poszukiwanie zaczyna się od kopii lokalnej.",
    "- sources: {n}": "- źródeł: {n}",
    "- saved locally: {n}": "- zapisane lokalnie: {n}",
    "- **missing — to be downloaded: {n}**": "- **brakuje — do pobrania: {n}**",
    "- index entries or transcriptions (the entry is in the data): {n}":
        "- wpisy indeksów i transkrypcje (wpis jest w danych): {n}",
    "- family accounts (no document): {n}": "- relacje rodzinne (bez dokumentu): {n}",
    "- files in `{dir}/` not attached to any source: {n}": "- pliki w `{dir}/` niepodpięte do żadnego źródła: {n}",
    "## 1. Missing local copies": "## 1. Brakujące kopie lokalne",
    "| Source | Title | Where | Persons |": "| Źródło | Tytuł | Gdzie | Osoby |",
    "## 2. Saved locally": "## 2. Zapisane lokalnie",
    "| Source | File | Persons |": "| Źródło | Plik | Osoby |",
    "## 3. Persons and their sources": "## 3. Osoby i ich źródła",
    "| Person | Saved locally | Missing | Index / transcription | Accounts |":
        "| Osoba | Zapisane lokalnie | Brakuje | Indeks / transkrypcja | Relacje |",
    "## 4. Files not attached to any source": "## 4. Pliki niepodpięte do żadnego źródła",
    "{ctx}: file {path} does not exist in the workspace": "{ctx}: plik {path} nie istnieje w workspace",

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
    "Pick the proband in the field above (the default one is set in data/project.yaml).":
        "Wybierz probanta w polu powyżej (domyślnego ustawia się w data/project.yaml).",
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
    "Proband": "Proband",
    "Type a name…": "Wpisz imię lub nazwisko…",
    "Persons": "Osoby",
    "(default)": "(domyślny)",
    "only ancestors": "tylko przodkowie",
    "Unticked: also the siblings of the ancestors (with spouses) and the proband's descendants":
        "Bez zaznaczenia: także rodzeństwo przodków (z małżonkami) i potomkowie probanta",
    "Show the ancestors of this person": "Pokaż przodków tej osoby",
    "Save the tree as an image (PNG)": "Zapisz drzewo jako obraz (PNG)",
    "Ancestors of ${name}": "Przodkowie: ${name}",
    "Ancestors of ${name} with their siblings": "Przodkowie z rodzeństwem: ${name}",
    "${Object.keys(V.nodes).length} persons · as of ${D.generated}": "${Object.keys(V.nodes).length} osób · stan na ${D.generated}",
    "Preparing the image…": "Przygotowuję obraz…",
    "Image saved.": "Zapisano obraz.",
    "Saving cancelled.": "Zapis anulowany.",
    "Saving files is not available in this view.": "W tym widoku nie można zapisywać plików.",
    "The image could not be created — the tree may be too large for this browser.":
        "Nie udało się utworzyć obrazu — drzewo może być za duże dla tej przeglądarki.",
    "language": "język",
    "View": "Widok",
    "Tree": "Drzewo",
    "Show on the map": "Pokaż na mapie",
    "At a glance": "W skrócie",
    "Sources": "Źródła",
    "probably": "prawdopodobnie",
    "Save the card (PNG)": "Zapisz kartę (PNG)",
    "Save this card as an image (PNG)": "Zapisz tę kartę jako obraz (PNG)",
    "The image could not be created.": "Nie udało się utworzyć obrazu.",

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
    "Show in the tree": "Pokaż w drzewie",
    "Places: ${ids.length}": "Miejsca: ${ids.length}",
    "Outside the filters: ${hidden} more events": "Poza filtrami: jeszcze ${hidden} zdarzeń",
    "Clusters of places": "Skupiska miejsc",
    "None yet.": "Na razie brak.",
    "Not on the map: places without coordinates: ${D.stats.geocode}, their events: ${D.stats.off} — see ${D.files.context}.":
        "Poza mapą: miejsca bez współrzędnych: ${D.stats.geocode}, ich zdarzenia: ${D.stats.off} — zob. ${D.files.context}.",
    "${D.title} · events on the map: ${D.stats.on} of ${D.stats.on + D.stats.off} · as of ${D.generated}":
        "${D.title} · zdarzeń na mapie: ${D.stats.on} z ${D.stats.on + D.stats.off} · stan na ${D.generated}",

    # ---- "At a glance" on the person card (familytree/summary.py); forms after "|" are plural forms (trn)
    "Who he was": "Kim był",
    "Who she was": "Kim była",
    "Who they were": "Kim był(a)",
    "Where he lived": "Gdzie mieszkał",
    "Where she lived": "Gdzie mieszkała",
    "Where they lived": "Gdzie mieszkał(a)",
    "Whom he lived with": "Z kim żył",
    "Whom she lived with": "Z kim żyła",
    "Whom they lived with": "Z kim żył(a)",
    "Worth knowing": "Co ciekawego",
    "The times he lived in": "W jakich czasach żył",
    "The times she lived in": "W jakich czasach żyła",
    "The times they lived in": "W jakich czasach żył(a)",
    "Rise in standing: {start} → {end}": "Awans społeczny: {start} → {end}",
    "Fall in standing: {start} → {end}": "Spadek pozycji społecznej: {start} → {end}",
    "baptism": "chrzest",
    "census": "spis ludności",
    "emigration": "emigracja",
    "occupation record": "zawód w akcie",
    "burial": "pogrzeb",
    "birth of a child|births of {n} children": "urodzenie dziecka|urodzenia {n} dzieci|urodzenia {n} dzieci",
    "wedding {date} ({place})": "ślub {date} ({place})",
    "{n} km": "{n} km",
    "in the same parish": "w obrębie tej samej parafii",
    "spouse unknown": "małżonek nieznany",
    "groom {a}, bride {b}": "on {a} l., ona {b} l.",
    "groom {a}": "on {a} l.",
    "bride {b}": "ona {b} l.",
    "{n} child|{n} children": "{n} dziecko|{n} dzieci|{n} dzieci",
    "({n} died in childhood)": "({n} zmarło w dzieciństwie)",
    "lasted {n} year|lasted {n} years": "trwało {n} rok|trwało {n} lata|trwało {n} lat",
    "ended with the death of his wife on {date}": "zakończone śmiercią żony {date}",
    "ended with the death of her husband on {date}": "zakończone śmiercią męża {date}",
    "ended with the death of the spouse on {date}": "zakończone śmiercią małżonka {date}",
    "ended with his death on {date}": "zakończone jego śmiercią {date}",
    "ended with her death on {date}": "zakończone jej śmiercią {date}",
    "ended with the person's death on {date}": "zakończone śmiercią tej osoby {date}",
    "divorced on {date}": "rozwód {date}",
    "cause: {cause}": "przyczyna: {cause}",
    "witnesses: {names}": "świadkowie: {names}",
    "He was widowed on {date}": "Owdowiał {date}",
    "She was widowed on {date}": "Owdowiała {date}",
    "Widowed on {date}": "Owdowiał(a) {date}",
    "remarried {after} ({date})": "ponowny ślub {after} ({date})",
    "{n} day later|{n} days later": "po {n} dniu|po {n} dniach|po {n} dniach",
    "{n} month later|{n} months later": "po {n} miesiącu|po {n} miesiącach|po {n} miesiącach",
    "{n} year later|{n} years later": "po {n} roku|po {n} latach|po {n} latach",
    "about {n} year later|about {n} years later": "po ok. {n} roku|po ok. {n} latach|po ok. {n} latach",
    "the same year": "w tym samym roku",
    "He lived {n} year|He lived {n} years": "Przeżył {n} rok|Przeżył {n} lata|Przeżył {n} lat",
    "She lived {n} year|She lived {n} years": "Przeżyła {n} rok|Przeżyła {n} lata|Przeżyła {n} lat",
    "Lived {n} year|Lived {n} years": "Przeżył(a) {n} rok|Przeżył(a) {n} lata|Przeżył(a) {n} lat",
    "He died aged {n} month|He died aged {n} months":
        "Zmarł w wieku {n} miesiąca|Zmarł w wieku {n} miesięcy|Zmarł w wieku {n} miesięcy",
    "She died aged {n} month|She died aged {n} months":
        "Zmarła w wieku {n} miesiąca|Zmarła w wieku {n} miesięcy|Zmarła w wieku {n} miesięcy",
    "Died aged {n} month|Died aged {n} months":
        "Zmarł(a) w wieku {n} miesiąca|Zmarł(a) w wieku {n} miesięcy|Zmarł(a) w wieku {n} miesięcy",
    "He died aged {n} day|He died aged {n} days": "Zmarł w wieku {n} dnia|Zmarł w wieku {n} dni|Zmarł w wieku {n} dni",
    "She died aged {n} day|She died aged {n} days": "Zmarła w wieku {n} dnia|Zmarła w wieku {n} dni|Zmarła w wieku {n} dni",
    "Died aged {n} day|Died aged {n} days": "Zmarł(a) w wieku {n} dnia|Zmarł(a) w wieku {n} dni|Zmarł(a) w wieku {n} dni",
    "aged {n}": "w wieku {n} roku|w wieku {n} lat|w wieku {n} lat",
    "aged {n} month|aged {n} months": "w wieku {n} miesiąca|w wieku {n} miesięcy|w wieku {n} miesięcy",
    "aged {n} day|aged {n} days": "w wieku {n} dnia|w wieku {n} dni|w wieku {n} dni",
    "under a year old": "w wieku poniżej roku",
    "He died under a year old": "Zmarł w wieku poniżej roku",
    "She died under a year old": "Zmarła w wieku poniżej roku",
    "Died under a year old": "Zmarł(a) w wieku poniżej roku",
    "the death record gives {n} year|the death record gives {n} years":
        "akt zgonu podaje {n} rok|akt zgonu podaje {n} lata|akt zgonu podaje {n} lat",
    "cause of death: {cause}": "przyczyna zgonu: {cause}",
    "Father of {n} child|Father of {n} children": "Ojciec {n} dziecka|Ojciec {n} dzieci|Ojciec {n} dzieci",
    "Mother of {n} child|Mother of {n} children": "Matka {n} dziecka|Matka {n} dzieci|Matka {n} dzieci",
    "Parent of {n} child|Parent of {n} children": "Rodzic {n} dziecka|Rodzic {n} dzieci|Rodzic {n} dzieci",
    "{n} of them died in childhood": "{n} z nich zmarło w dzieciństwie",
    "first child at the age of {a}, the last at {b}": "pierwsze dziecko w wieku {a} lat, ostatnie w wieku {b} lat",
    "the eldest of {n} known children": "najstarsze z {n} znanych dzieci swoich rodziców",
    "the youngest of {n} known children": "najmłodsze z {n} znanych dzieci swoich rodziców",
    "child {i} of {n} known children": "{i}. z {n} znanych dzieci swoich rodziców",
    "He was the longest-lived of the {surname} line ({n} with a known age)":
        "Najdłużej żyjący w linii {surname} (wiek znany u {n} osób)",
    "She was the longest-lived of the {surname} line ({n} with a known age)":
        "Najdłużej żyjąca w linii {surname} (wiek znany u {n} osób)",
    "The longest-lived of the {surname} line ({n} with a known age)":
        "Najdłużej żyjąca osoba w linii {surname} (wiek znany u {n} osób)",
    "He was the longest-lived of the proband's ancestors ({n} with a known age)":
        "Najdłużej żyjący z przodków probanta (wiek znany u {n} osób)",
    "She was the longest-lived of the proband's ancestors ({n} with a known age)":
        "Najdłużej żyjąca z przodków probanta (wiek znany u {n} osób)",
    "The longest-lived of the proband's ancestors ({n} with a known age)":
        "Najdłużej żyjąca osoba z przodków probanta (wiek znany u {n} osób)",
    "He was the first known of the {surname} line to leave the home area":
        "Pierwszy znany z linii {surname}, który opuścił rodzinne strony",
    "She was the first known of the {surname} line to leave the home area":
        "Pierwsza znana z linii {surname}, która opuściła rodzinne strony",
    "The first known of the {surname} line to leave the home area":
        "Pierwsza znana osoba z linii {surname}, która opuściła rodzinne strony",
    "military service": "służba wojskowa",
    "He signed his name": "Umiał się podpisać",
    "She signed her name": "Umiała się podpisać",
    "Signed their name": "Umiał(a) się podpisać",
    "He could not write and made a mark instead of a signature": "Nie umiał pisać — zamiast podpisu stawiał znak",
    "She could not write and made a mark instead of a signature": "Nie umiała pisać — zamiast podpisu stawiała znak",
    "Could not write and made a mark instead of a signature": "Nie umiał(a) pisać — zamiast podpisu stawiał(a) znak",
    "godparents: {names}": "chrzestni: {names}",
    "in the records also as: {names}": "w aktach także jako: {names}",
    "languages of the records: {languages}": "języki aktów: {languages}",

    # ---- great events of history (familytree/history.py)
    "the Great Northern War": "wielka wojna północna",
    "the War of the Polish Succession": "wojna o sukcesję polską",
    "the Seven Years' War": "wojna siedmioletnia",
    "the Bar Confederation": "konfederacja barska",
    "the First Partition of Poland": "I rozbiór Polski",
    "the Great Sejm and the Constitution of 3 May": "Sejm Wielki i Konstytucja 3 maja",
    "the Second Partition of Poland": "II rozbiór Polski",
    "the Kościuszko Uprising": "insurekcja kościuszkowska",
    "the Third Partition of Poland": "III rozbiór Polski",
    "the Napoleonic Wars and the Duchy of Warsaw": "wojny napoleońskie i Księstwo Warszawskie",
    "the Congress Kingdom of Poland is created": "powstaje Królestwo Polskie",
    "the November Uprising": "powstanie listopadowe",
    "the Kraków Uprising and the Galician peasant revolt": "powstanie krakowskie i rabacja galicyjska",
    "the Spring of Nations": "Wiosna Ludów",
    "serfdom is abolished in Galicia": "zniesienie pańszczyzny w Galicji",
    "the January Uprising": "powstanie styczniowe",
    "the peasants of the Congress Kingdom are granted their land": "uwłaszczenie chłopów w Królestwie Polskim",
    "the Austro-Prussian War": "wojna prusko-austriacka",
    "the Franco-Prussian War and the founding of the German Empire": "wojna francusko-pruska i powstanie Cesarstwa Niemieckiego",
    "the Kulturkampf": "Kulturkampf",
    "civil registry offices (Standesamt) are introduced in Prussia": "urzędy stanu cywilnego (Standesamt) w Prusach",
    "the Prussian deportations of Poles": "rugi pruskie",
    "the Russo-Japanese War": "wojna rosyjsko-japońska",
    "the Revolution of 1905": "rewolucja 1905 roku",
    "the school strikes against Germanisation": "strajki szkolne przeciw germanizacji",
    "the First World War": "I wojna światowa",
    "Poland regains independence": "odzyskanie niepodległości",
    "the Spanish flu pandemic": "epidemia grypy hiszpanki",
    "the lands of the Prussian partition join Poland": "ziemie zaboru pruskiego wracają do Polski",
    "the Polish–Soviet War": "wojna polsko-bolszewicka",
    "the Great Depression": "wielki kryzys",
    "the Second World War": "II wojna światowa",
    "the new borders of Poland and the resettlements": "nowe granice Polski i przesiedlenia",
    "the Poznań protests and the thaw of October 1956": "Poznański Czerwiec i odwilż październikowa 1956",
    "the protests of December 1970": "Grudzień 1970",
    "Karol Wojtyła becomes Pope John Paul II": "Karol Wojtyła papieżem Janem Pawłem II",
    "the Solidarity movement": "„Solidarność”",
    "martial law in Poland": "stan wojenny",
    "the end of communist rule in Poland": "koniec rządów komunistycznych w Polsce",
    "Poland joins the European Union": "Polska w Unii Europejskiej",

    # ---- confidence: validation of the new fields (familytree/model.py)
    '{ctx}: expected {{about: …, note: "…", resolved: true/false}}': '{ctx}: oczekiwano {{about: …, note: "…", resolved: true/false}}',
    '{ctx}: expected {{namesakes: excluded | possible, note: "…"}}': '{ctx}: oczekiwano {{namesakes: excluded | possible, note: "…"}}',
    '{ctx}: expected {{score: 0–100, reason: "…"}}': '{ctx}: oczekiwano {{score: 0–100, reason: "…"}}',

    # ---- confidence: scores, "why this score" and what would strengthen it (familytree/confidence.py)
    "confidence.md": "pewnosc.md",
    "unsupported": "bez dowodów",
    "birth record": "akt urodzenia",
    "baptism record": "akt chrztu",
    "marriage record": "akt małżeństwa",
    "death record": "akt zgonu",
    "burial record": "akt pochówku",
    "civil register record": "akt stanu cywilnego",
    "index entry": "wpis w indeksie",
    "population register": "księga ludności",
    "family document": "dokument rodzinny",
    "photo": "zdjęcie",
    "gravestone": "nagrobek",
    "family account": "relacja rodzinna",
    "online tree": "drzewo w internecie",
    "publication": "publikacja",
    "source": "źródło",
    "original source": "źródło oryginalne",
    "derivative source": "źródło pochodne",
    "authored source": "źródło autorskie",
    "direct evidence": "dowód bezpośredni",
    "indirect evidence": "dowód pośredni",
    "primary information": "informacja pierwotna",
    "secondary information": "informacja wtórna",
    "{evidence}: {type} {source} ({classification}, {information})": "{evidence}: {type} {source} ({classification}, {information})",
    "from the person's death": "z zapisu zgonu osoby",
    "from the person's marriage": "z zapisu ślubu osoby",
    "from the parents' marriage": "ze ślubu rodziców",
    "from the age in the record": "z wieku podanego w akcie",
    "names the parents: {names}": "podaje rodziców: {names}",
    "the transcription does not name the parents": "transkrypcja nie podaje rodziców",
    "local copy of {source}": "kopia lokalna {source}",
    "transcription of {source}": "transkrypcja {source}",
    "marked as the same record": "oznaczone jako ten sam akt",
    "the same local copy": "ta sama kopia lokalna",
    "the same parish, year and act, cited for the same event": "ta sama parafia, rok i numer aktu, przy tym samym zdarzeniu",
    "the entry refers to {source}": "wpis odsyła do {source}",
    "the same informant": "ten sam informator",
    "the same record": "ten sam akt",
    "{source} is the same record as {other} ({why}): counted once": "{source} to ten sam akt co {other} ({why}): liczony raz",
    "no source cited": "brak cytowanego źródła",
    "independent corroboration: {evidence}": "niezależne potwierdzenie: {evidence}",
    "more independent records: {sources}": "kolejne niezależne akty: {sources}",
    "confirmed needs direct evidence from an original source with primary information":
        "„potwierdzone” wymaga dowodu bezpośredniego ze źródła oryginalnego z informacją pierwotną",
    "confirmed needs a second independent record with direct evidence":
        "„potwierdzone” wymaga drugiego niezależnego aktu z dowodem bezpośrednim",
    "confirmed needs every conflict resolved": "„potwierdzone” wymaga rozstrzygnięcia każdej sprzeczności",
    "at most {cap}: {reason}": "najwyżej {cap}: {reason}",
    "set to {score} by confidence_override: {reason}": "ustawione na {score} przez confidence_override: {reason}",
    "resolved conflict: {note}": "rozstrzygnięta sprzeczność: {note}",
    "unresolved conflict: {note}": "nierozstrzygnięta sprzeczność: {note}",
    "chronology warning, explained by a resolved conflict: {warning}":
        "ostrzeżenie chronologiczne wyjaśnione rozstrzygniętą sprzecznością: {warning}",
    "chronology warning: {warning}": "ostrzeżenie chronologiczne: {warning}",
    "identity: {sources} name the parents": "tożsamość: {sources} podają rodziców",
    "identity: the ages in {sources} agree with the year of birth": "tożsamość: wiek w {sources} zgadza się z rokiem urodzenia",
    "identity: namesakes checked and excluded": "tożsamość: imiennicy sprawdzeni i wykluczeni",
    "identity: a namesake could be the person": "tożsamość: może chodzić o imiennika",
    "identity: the evidence about the year of birth is contradictory": "tożsamość: dowody co do roku urodzenia są sprzeczne",
    "identity: born in the parish where the parents married": "tożsamość: urodzony w parafii ślubu rodziców",
    "identity: born in the parish where the siblings were born": "tożsamość: urodzony w parafii, w której rodziło się rodzeństwo",
    "the evidence about the year of birth is contradictory": "dowody co do roku urodzenia są sprzeczne",
    'manual confidence "{label}" of the person': "ręczna pewność osoby: „{label}”",
    'manual confidence "{label}" of the family {family}': "ręczna pewność rodziny {family}: „{label}”",
    'the event is marked "{label}"': "zdarzenie oznaczone jako „{label}”",
    "living person: the link rests on the family's own knowledge and does not lower the path (only a manual label caps it)":
        "osoba żyjąca: powiązanie opiera się na wiedzy rodziny i nie obniża ścieżki (ogranicza je tylko ręczna etykieta)",
    "years unknown": "lata nieznane",
    "usually the bride's parish": "zwykle parafia panny młodej",
    "View the scan of the record behind the index entry {source} and cite it as a source of its own (quality: image).":
        "Obejrzyj skan aktu, z którego pochodzi wpis w indeksie {source}, i dodaj go jako osobne źródło (quality: image).",
    "Save a local copy of {source} (`file`).": "Zapisz kopię lokalną {source} (`file`).",
    "Resolve the conflict or the chronology warning and record the reasoning (`conflicts`: `resolved: true`, the reasoning in `note`).":
        "Rozstrzygnij sprzeczność lub ostrzeżenie chronologiczne i zapisz uzasadnienie (`conflicts`: `resolved: true`, "
        "uzasadnienie w `note`).",
    "The score is capped at {cap} ({reason}): change the label once the evidence supports more.":
        "Wynik jest ograniczony do {cap} ({reason}): zmień etykietę, gdy dowody pozwolą na więcej.",
    "A full copy of the civil birth certificate (USC) names the parents; living persons are never searched online.":
        "Odpis zupełny aktu urodzenia (USC) podaje rodziców; osób żyjących nigdy nie szukamy w internecie.",
    "Find the birth or baptism record of {name}: {where}, {years}.": "Znajdź akt urodzenia lub chrztu: {name} — {where}, {years}.",
    "Find the death or burial record of {name}: {where}, {years}.": "Znajdź akt zgonu lub pochówku: {name} — {where}, {years}.",
    "Find the marriage record of {name}: {where}, {years}.": "Znajdź akt małżeństwa: {name} — {where}, {years}.",
    "Transcribe {source} (`transcription`): it shows whether the record names the parents.":
        "Przepisz {source} (`transcription`): transkrypcja pokaże, czy akt podaje rodziców.",
    "A second independent record: the marriage record of {name} (it usually names the parents).":
        "Drugi niezależny akt: akt małżeństwa — {name} (zwykle podaje rodziców).",
    "A second independent record: the death record of {name} (it often names the parents).":
        "Drugi niezależny akt: akt zgonu — {name} (często podaje rodziców).",
    "A second independent record that names the parents: a census, a population register or the civil copy of a record of {name}.":
        "Drugi niezależny akt z rodzicami: spis ludności, księga ludności albo duplikat cywilny aktu — {name}.",
    "Check namesakes: other persons named {name} in {where}, {years}; record the result in `identity`.":
        "Sprawdź imienników: inne osoby o nazwisku i imieniu {name} — {where}, {years}; wynik zapisz w `identity`.",
    "A second independent record of the marriage: the civil copy (duplicate) of the parish book, or the banns.":
        "Drugi niezależny zapis ślubu: duplikat cywilny księgi parafialnej albo zapowiedzi.",
    "A second independent record of the birth: the age in the death or marriage record, or the civil copy next to the parish book.":
        "Drugi niezależny zapis urodzenia: wiek w akcie zgonu lub małżeństwa albo duplikat cywilny obok księgi parafialnej.",
    "A second independent record of the death: the burial record, the civil copy or the gravestone.":
        "Drugi niezależny zapis zgonu: akt pochówku, duplikat cywilny albo nagrobek.",

    # ---- confidence report (confidence.md)
    "# Confidence of the tree": "# Pewność drzewa",
    "Scores 0–100 computed from the evidence (docs/confidence.md): **confirmed** ≥ 85 · **probable** 60–84 · "
    "**hypothesis** 30–59 · **unsupported** < 30. The *link* of a person is the evidence that they are the child of "
    "their parents and the person in the records; the *path* is the weakest link between the proband and the person. "
    "A manual `confidence` caps a score; `confidence_override` replaces it.":
        "Wyniki 0–100 obliczone z dowodów (docs/confidence.md): **potwierdzone** ≥ 85 · **prawdopodobne** 60–84 · "
        "**hipoteza** 30–59 · **bez dowodów** < 30. *Powiązanie* osoby to dowody, że jest dzieckiem swoich rodziców i "
        "osobą z aktów; *ścieżka* to najsłabsze powiązanie między probantem a osobą. Ręczne `confidence` ogranicza "
        "wynik; `confidence_override` go zastępuje.",
    "- links parent–child: {n} ({counts})": "- powiązania rodzic–dziecko: {n} ({counts})",
    "- facts (birth, death, marriage): {n} ({counts})": "- fakty (urodzenie, zgon, ślub): {n} ({counts})",
    "- ancestors of the proband by path: {n} ({counts})": "- przodkowie probanta według ścieżki: {n} ({counts})",
    "## Ancestors per generation (path from the proband)": "## Przodkowie w pokoleniach (ścieżka od probanta)",
    "Gen.": "Pok.",
    "Ancestors": "Przodkowie",
    "## Weakest links on the line of ancestors": "## Najsłabsze powiązania na linii przodków",
    "_The lowest-scored links first; a weak link lowers the path of every ancestor above it._":
        "_Najniżej ocenione powiązania najpierw; słabe powiązanie obniża ścieżkę każdego przodka powyżej._",
    "- link to the parents: **{score}** · path from the proband to the parents: {path} · ancestors above: {n}":
        "- powiązanie z rodzicami: **{score}** · ścieżka od probanta do rodziców: {path} · przodków powyżej: {n}",
    "- why:": "- dlaczego:",
    "- to strengthen:": "- co by wzmocniło:",
    "## Facts of the ancestors below probable": "## Fakty przodków poniżej „prawdopodobne”",
    "## Manual labels that disagree with the evidence": "## Ręczne etykiety niezgodne z dowodami",
    "_A manual label above the computed band is not backed by the cited sources; one below it may be outdated._":
        "_Ręczna etykieta powyżej obliczonego przedziału nie ma pokrycia w cytowanych źródłach; poniżej — może być nieaktualna._",
    '- `{id}` {name}: manual "{label}", computed link {score}': "- `{id}` {name}: ręcznie „{label}”, obliczone powiązanie {score}",
    "## Other persons (not ancestors)": "## Pozostałe osoby (nie przodkowie)",

    # ---- confidence in the page (templates)
    "Confidence": "Pewność",
    "Show only the persons whose weakest link to the proband reaches this confidence (scores computed from the sources)":
        "Pokaż tylko osoby, których najsłabsze powiązanie z probantem osiąga tę pewność (wyniki obliczone ze źródeł)",
    "all persons": "wszystkie osoby",
    "${V.hidden.length} hidden": "ukryte: ${V.hidden.length}",
    "hidden by the filter": "ukryta przez filtr",
    "Path from the proband": "Ścieżka od probanta",
    "Link to the parents": "Powiązanie z rodzicami",
    "Birth or baptism": "Urodzenie lub chrzest",
    "Death or burial": "Zgon lub pochówek",
    "Marriage": "Ślub",
    "Why this score": "Skąd ten wynik",
    "To strengthen": "Co by wzmocniło",
    "no parents in the data": "brak rodziców w danych",
    "not connected to the proband in this view": "niepowiązana z probantem w tym widoku",
    "proband": "proband",
    "path": "ścieżka",
    "link": "powiązanie",
    "Hidden by the confidence filter: the weakest link from the proband is ${path ?? '—'}, the filter needs ${minConf}.":
        "Ukryta przez filtr pewności: najsłabsze powiązanie od probanta to ${path ?? '—'}, filtr wymaga ${minConf}.",
    "confidence ≥ ${band[2]} (${minConf})": "pewność ≥ ${band[2]} (${minConf})",
    "dot = weakest link from the proband; links of living persons do not lower it":
        "kropka = najsłabsze powiązanie od probanta; powiązania osób żyjących go nie obniżają",
    "cited on an event of the person": "przy zdarzeniu osoby",
    "cited as evidence of the parentage": "wskazane jako dowód pochodzenia",
    '{ctx}: expected {{sources: [S0001], note: "…"}}': '{ctx}: oczekiwano {{sources: [S0001], note: "…"}}',
    "**Exception to the weakest link:** the link of a living person (and the union of a couple with a living spouse) "
    "keeps its own score but does not lower the path — the family knows it first-hand and the records are not public; "
    "only a manual label caps it.":
        "**Wyjątek od najsłabszego powiązania:** powiązanie osoby żyjącej (i związek pary z żyjącym małżonkiem) "
        "zachowuje własny wynik, ale nie obniża ścieżki — rodzina zna je z pierwszej ręki, a akty nie są publiczne; "
        "ogranicza je tylko ręczna etykieta.",
}
