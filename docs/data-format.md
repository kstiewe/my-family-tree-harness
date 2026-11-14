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
  An index hit without a scan is at most `probable`.
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
| `birth`, `baptism`, `death`, `burial` | event: `{date, place, sources, note, age, cause}` |
| `events` | list of `{type, date, place, value, note, sources}`; `type`: residence, occupation, emigration, military, census, confirmation, education, other |
| `confidence`, `notes`, `todo` | research state |

## families.yaml

`id`, `husband`, `wife`, `marriage` (event plus `husband_age`, `wife_age`, `witnesses`), `divorce`,
`children` (in order of birth), `confidence`, `notes`, `todo`. A child belongs to the family of its
parents; a person may be a spouse in several families.

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
`informant` (oral accounts: who, through whom, when), `transcription`, `notes`.

## Validation

`build.py` reports errors (the outputs are not generated until they are fixed) and warnings
(unknown fields, unused sources, chronology: death before birth, a mother aged over 52 at a birth,
a child born after the father's death, marriage before 14/16 …). `--json` gives each issue a stable
`code`, the `record` it concerns and a `fix` suggestion.

## How the research hints are made (gap report)

For every person the build collects evidence about the year of birth (date of birth or baptism,
age in the death or marriage record, the children's years of birth, the parents' marriage and
ages) and intersects it. It then points to parishes to search (place of birth, residence,
marriage, the children's births) and builds Geneteka queries. Ends of the proband's lines come
first (Kekule numbering: proband = 1, father of n = 2n, mother = 2n+1).
