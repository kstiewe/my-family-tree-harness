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
}
