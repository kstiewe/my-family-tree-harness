# Data format

The source of truth is five YAML files in `<workspace>/data/`. YAML is readable, allows comments,
is easy to edit by hand or by an agent, and diffs well in git. The model follows GEDCOM —
**persons**, **families** (a union: spouses, marriage, children), **places** and **sources** — so
the data can be moved to Gramps or another program without losing structure.

`python3 scripts/build.py --schema` prints the same model as JSON (it is generated from the code
that validates the data, so it is always current). Annotated templates are in
`familytree/skeleton/data/`; a complete example is `examples/sample-family/`.

## Files

| File | Content |
|---|---|
| `project.yaml` | `name`, `author` (GEDCOM header), `language` (`en`, `pl`), `proband` (person ID), researched `surnames` with variants, `regions` |
| `persons.yaml` | list of persons |
| `families.yaml` | list of unions with children |
| `places.yaml` | gazetteer: localities and parishes |
| `sources.yaml` | records, index entries, accounts, documents |

## Rules

- **IDs**: `I0001` persons, `F0001` families, `P0001` places, `S0001` sources (prefix + at least
  four digits). The build prints the next free IDs.
- **Dates always in quotes**: `"1850-03-12"`, `"1850-03"`, `"1850"`, `"~1850"` (about), `"<1870"`
  (before), `">1845"` (after), `"1848..1852"` (between). Dates are Gregorian; when a record from the
  Russian partition gives two dates, the Julian one goes to `note`.
- **Women** under their maiden name (`surname`); surnames after marriage in `married_surnames`.
- **Names** in the local form; Latin, Russian and German forms (Joannes, Иосифъ, Johann) in `variants`.
- **Every fact points to a source** (`sources`), even if it is only a family account (`type: oral`).
- **Confidence**: `confirmed` (confirmed by a record), `probable`, `hypothesis` (to be verified).
  An index hit without a scan is at most `probable`. The build also computes a score 0–100 for every
  link and fact from the cited sources ([confidence.md](confidence.md)); the manual label caps it.
- **Ages from records** (`age` at death, `husband_age` / `wife_age` at marriage) are always recorded:
  the build derives the range of birth years from them.
- **Parish**: a locality points to its parish (`parish`), the parish to the Geneteka region
  (`geneteka_region`); the gap report then contains ready-made Geneteka links.
- **Living persons** are marked `living: true`. Their data is never sent to search engines and
  `--public` hides it. A person without `living`, born less than 100 years ago and without a death
  date, is treated as living. `living: false` records a death confirmed by the family.
- **Language of sources**: `language` holds the language of the original document as an ISO 639-1
  code (`pl`, `la` Latin, `de`, `ru`, `uk`, `be`, `lt`, `cs`, `yi`, `he` …), or a list when a record
  mixes languages. Transcriptions keep the original language and spelling.

## persons.yaml

| Field | Meaning |
|---|---|
| `id`, `given`, `surname`, `married_surnames`, `variants` | identity |
| `sex` | `M`, `F`, `U` |
| `living` | `true` / `false` (see above) |
| `religion`, `occupation` (list) | free text |
| `birth`, `baptism`, `death`, `burial` | event: `{date, place, sources, note, age, cause, confidence, godparents}` |
| `events` | list of `{type, date, place, value, note, sources, age, confidence}`; `type`: residence, occupation, emigration, military, census, confirmation, education, signature, other |
| `quote` | optional `{text, source, note}`: one short sentence the person card shows as a quote |
| `confidence`, `notes`, `todo` | research state |
| `conflicts`, `confidence_override`, `identity`, `parentage` | evidence analysis (see "Confidence fields" below) |

All of these are optional; data written before a field existed stays valid.

- **Occupation and standing**: one `occupation` event per record that states it (a child's
  baptism, a marriage, a death), with its date and source; `value` is the occupation or status as
  the record writes it (`komornik (Einlieger)`, `gospodarz`, `wycużnik`). The free-text list
  `occupation` still works; a year written in an entry (`komornik (1889)`) dates it.
- **Residence**: `value` holds the house number or the address when the record gives one
  (`house no. 12`).
- **Signature**: `{type: signature, value: signed}` when the person signed the record, `value: mark`
  when they made a cross instead (could not write).
- **godparents** (birth, baptism) and **witnesses** (marriage): names as the record writes them,
  as text or a list.
- **confidence** on one event marks that fact alone as `probable` or `hypothesis`; the card then
  says "probably".

## families.yaml

`id`, `husband`, `wife`, `marriage` (event plus `husband_age`, `wife_age`, `witnesses`), `divorce`,
`children` (in order of birth), `confidence`, `notes`, `todo`, `conflicts`, `confidence_override`. A
child belongs to the family of its parents; a person may be a spouse in several families.

## places.yaml

`id`, `name`, `type`, `aliases` (historical and foreign names), `parish` (ID of the parish entry),
`denomination` (of a parish), `partition` (`russian`, `prussian`, `austrian`; the Polish values
`rosyjski`, `pruski`, `austriacki` are accepted too), `admin` (list of `{period, value}`), `today`,
`country` (ISO code), `coords` (`[lat, lon]`), `geneteka_region`, `records` (where the books are),
`notes`.

`coords` are decimal degrees (WGS84), latitude first: `[52.61, 20.38]`. They are optional; a place
without them is drawn at the coordinates of its parish, and the gap report lists it. Write where the
coordinates come from in `notes` (e.g. "coords: OpenStreetMap, 2026-11-14"). The build warns when a
Polish place lies outside Poland, which usually means latitude and longitude are swapped. The map and
the geography context are described in [geography.md](geography.md).

`type` is free text (village, town, manor …); these values have a meaning for the reports:
`parish` (also `parafia`), `region`, `commune` (`gmina`), `county` (`powiat`), `country` (`kraj`).

## sources.yaml

`id`, `type` (birth_record, baptism_record, marriage_record, death_record, burial_record,
civil_record, index, census, population_register, family_document, photo, gravestone, oral,
online_tree, publication, other), `title`, `parish`, `year`, `act`, `repository`, `signature`,
`url`, `quality` (original, image, transcription, index, derivative, oral), `language`, `accessed`,
`informant` (oral accounts: who, through whom, when), `file`, `transcription`, `notes`, and the optional
evidence fields `classification`, `information`, `evidence`, `same_record_as`, `derived_from` (see
"Confidence fields" below).

**Local copies.** `file` is the path (or a list of paths) of the saved copy of the source, relative to the
workspace and normally under `research/skany/<archive>/<fonds>/` — the scan, a screenshot, a saved page or
a PDF; an act on two photos lists both. The build fails when a listed file does not exist and writes
`output/scans.md` (`skany.md`): the sources that are scans, photos or pages without a local copy, the
sources that have one, per person what is saved and what is not, and files that no source points to.
Index entries (the transcription in the data is the copy) and family accounts need no file.

## Confidence fields

The confidence scores ([confidence.md](confidence.md)) are computed from the fields above. These
optional fields refine them; the build validates them (unknown values are errors with a `fix`).

| Where | Field | Meaning |
|---|---|---|
| source | `classification` | `original` (a record made at the time, or its image), `derivative` (index, transcription, abstract), `authored` (family account, someone's tree, publication). Default: from `type` and `quality`. |
| source | `information` | `primary` (first-hand, at the time) or `secondary`. Default: from the type and the event that cites the source. |
| source | `evidence` | `direct` (answers the question alone — for a link: names the parents) or `indirect`. |
| source | `same_record_as` | list of source IDs that are the same record (the index entry and the image of one act): they count once. |
| source | `derived_from` | the source ID (or list) this one was made from; they count once. |
| person, family | `conflicts` | list of `{about, note, resolved, sources}`: evidence that disagrees. Person `about`: `link`, `identity`, `birth`, `death`; family: `marriage`, `link` (the children's links); without `about` every score of the record. `resolved: true` once the reasoning is in `note`. |
| person | `confidence_override` | `{score: 0–100, reason, about: link \| birth \| death}` (or a list): replaces the computed score; the reason is required and shown. |
| family | `confidence_override` | `{score: 0–100, reason}`: replaces the score of the marriage. |
| person | `identity` | `{namesakes: excluded \| possible, note}`: whether other persons of the same name were checked. |
| person | `parentage` | `{sources: [S0001], note}`: sources cited directly as evidence that the person is the child of their parents (direct evidence for the link). A family account cited on one of the person's extra `events` (e.g. `{type: other, sources: [S0001], note: "parents: … (family account)"}`) counts for the link too, without this field. |

```yaml
- id: I0013
  given: Karol
  conflicts:
    - {about: link, resolved: true, sources: [S0001],
       note: "Born after his father's recorded death: the family's death date for August is the doubtful one."}
  identity: {namesakes: excluded, note: "no other Karol Nowak born in Wzorki 1905–1920 in the index"}
```

## Validation

`build.py` reports errors (the outputs are not generated until they are fixed) and warnings
(unknown fields, unused sources, chronology: death before birth, a mother aged over 52 at a birth,
a child born after the father's death, marriage before 14/16 …). `--json` gives each issue a stable
`code`, the `record` it concerns and a `fix` suggestion.

## "At a glance" on the person card

The card of every person in `tree.html` opens with a short portrait computed from the data only
(`familytree/summary.py`; nothing is invented). Each row is one line and opens to the details:

| Row | From |
|---|---|
| Who they were | occupation events and the `occupation` list in time order (`parobek 1893 → gospodarz 1903`), the rise or fall in standing on the rural ladder (servant, landless, cottager, farmer), the religion |
| Where they lived | birth, residence/census/emigration events, places of occupation records, the births of the children and the death, in order; consecutive records of one place merged (`1850–1872 Przykładowo`), the distance of each move in km, a click shows the place on the map; a wedding in a parish church is told with the place of residence of its time |
| Whom they lived with | each marriage: date and place, ages of both, children (and how many died in childhood), how long it lasted and how it ended, how long until the next marriage (`widowed on …; remarried 5 months later`), witnesses |
| Worth knowing | age at death and its cause (and the age the record gives when it differs), children who died in childhood, ages at the first and the last child, place among the siblings, the longest-lived of a surname line or of the proband's ancestors, the first of a line to leave the home area (≥ 50 km), military service, emigration, signature, godparents, spellings, languages of the records |
| The times they lived in | the partition of the person's places and the great events of history during the life, with the age (a general list in `familytree/history.py`) |

A quote follows: the person's `quote`, else a sentence of a family account (`type: oral`) or of
the person's own record that names them. Every item carries footnote numbers of its sources;
`probable` and `hypothesis` facts are marked. Rows without data are left out. Living persons get
no summary in `--public` outputs, and there family accounts, informants, and witnesses or
godparents of records younger than 100 years are left out. The card can be saved as a PNG image.

## How the research hints are made (gap report)

For every person the build collects evidence about the year of birth (date of birth or baptism,
age in the death or marriage record, the children's years of birth, the parents' marriage and
ages) and intersects it. It then points to parishes to search (place of birth, residence,
marriage, the children's births) and builds Geneteka queries. Ends of the proband's lines come
first (Kekule numbering: proband = 1, father of n = 2n, mother = 2n+1).
