# Confidence: scores computed from the evidence

`build.py` gives every parent–child link and every fact a score from 0 to 100, computed from the
cited sources (`familytree/confidence.py`). Nobody types a score in: it follows from what the data
already says (source `type`, `quality`, `file`, `transcription`, which event cites the source,
whose event it is). A few optional fields refine it. The tree page shows the score with a
"why this score" breakdown on the person card and can hide what falls below a threshold; the build
writes a report (`confidence.md`, Polish `pewnosc.md`) and puts the scores in `build.py --json`.

The model follows the evidence analysis of the **Genealogical Proof Standard** (GPS). It is a guide
to what to research next, not a proof: the reasoning still belongs in `notes` and `conflicts`.

## What is scored

| Score | Question | Evidence it reads |
|---|---|---|
| **link** (child × parents' family) | Is this person the child of these parents, and the person named in the records (not a namesake)? | the child's birth/baptism sources; the child's death/burial and marriage records (when they name the parents); the parents' marriage (indirect); family accounts and other narratives cited on the child's extra `events`; the sources of the optional `parentage` field; identity signals |
| **birth** | date and place of birth or baptism | sources of `birth` and `baptism`; ages in the death and marriage records (indirect) |
| **death** | date and place of death or burial | sources of `death` and `burial` |
| **marriage** (family) | date and place of the marriage | sources of `marriage` |
| **union** (family) | is the couple attested at all? | the marriage score or a child's link, whichever is higher |
| **path** (from the proband) | how sure is the whole chain from the proband to this person? | the weakest step on the best path |

## GPS terms and their defaults

**Source classification** (`classification` overrides it):

| Class | Meaning | Default when |
|---|---|---|
| original | a record made at the time of the event, or an image of it | `quality: original` or `image` (a scan counts as the original) |
| derivative | made from another source: an index entry, a transcription, an abstract | `type: index`, or `quality: index / transcription / derivative`, or no quality |
| authored | a narrative made later from other information | `type: oral / online_tree / publication`, or `quality: oral` |

**Information** (`information` overrides it): *primary* comes from someone who knew it first-hand,
at the time; *secondary* from hearsay or long after. Default: primary when the record's own event is
the question (a birth or baptism record for the birth and the parents, a death record or gravestone
for the death, a marriage record for the marriage); secondary otherwise (a death record for the age
or the parents, a family account, someone's tree).

**Evidence** (`evidence` overrides it): *direct* answers the question alone, *indirect* only together
with other evidence. For a link: the child's own birth/baptism record is direct; a death or marriage
record is direct when its transcription names the parents (the given names are matched, Latin and
Cyrillic spellings included, also the forms in `variants`), indirect when it does not or has no
transcription; the parents' marriage is always indirect. For a birth date, an age in another record
is indirect.

**Family accounts of parentage.** Who the parents are is often known only from the family and
recorded as an extra event of the child, e.g.
`{type: other, sources: [S0001], note: "parents: Stanisław Nowak and Zofia Zielińska (family account)"}`.
A narrative source (`type: oral / online_tree / publication`, or `quality: oral`) cited on any of the
person's extra `events` counts for the link as authored, secondary, direct evidence — one account
alone gives 34 (39 with a transcription), and two accounts of one informant count once. Records cited on residence or
occupation events do not count for the link. To cite any other source for the parentage on purpose,
use the optional `parentage: {sources: [...], note}` of the person: its sources are direct evidence
(primary information for a birth, baptism or civil record or its index, secondary otherwise).

## The table of points

One cited source gives `base × information × evidence`, plus a little for what makes it checkable:

| Part | Points |
|---|---|
| base: original / derivative / authored | 70 / 55 / 45 (someone's online tree: 25) |
| information: primary / secondary | × 1.0 / × 0.75 |
| evidence: direct / indirect | × 1.0 / × 0.6 |
| local copy (`file`): original / derivative | +8 / +3 |
| transcription | +5 |

The strongest record is the **anchor**. Each further **independent** record adds 40 %, then 20 %,
then 10 % of its own strength (at most +30 together). Then:

| Adjustment | Points |
|---|---|
| identity: the records name the parents | +5 |
| identity: the ages in the death/marriage records agree with a cited birth (±1 year) | +3 |
| identity: born in the parish of the parents' marriage or of the siblings' births | +3 |
| `identity: {namesakes: excluded}` / `possible` | +5 / −15 |
| unresolved conflict (`conflicts`, `resolved: false`) | −20 each |
| resolved conflict | −5 each |
| chronology warning of the validator touching the score (unless a resolved conflict explains it) | −10 each |
| contradictory evidence about the year of birth | −10 |

The total is kept within 0–100. Worked examples from the sample family:

| Evidence | Score |
|---|---|
| a family account only (`S0001`) | 34 hypothesis |
| one index entry with its transcription (`S0017`) | 60 probable |
| the index entry and the image of the same act (`S0002`, `S0003`): one record | 83 probable |
| a civil birth record image and the independent parish baptism (`S0005`, `S0006`) | 99 confirmed |

## Thresholds

| Band | Score | Meaning |
|---|---|---|
| **confirmed** | ≥ 85 | direct evidence from an original source with primary information, a second independent record with direct evidence, no unresolved conflict |
| **probable** | 60–84 | good evidence from one record, or several weaker ones |
| **hypothesis** | 30–59 | some evidence: a family account, an index without the record, the parents' marriage only |
| **unsupported** | < 30 | nothing cited, someone else's tree, or evidence that contradicts itself |

The cut-offs are deliberately stricter than the manual labels used so far:

- **Confirmed is a gate, not only a number.** Without the three conditions above the score stops at
  84, and the breakdown says which condition is missing. One record, however good, is "probable":
  the full scan with a transcription and a local copy gives 83.
- An index entry alone is at most 60 (probable at its lowest), as the old rule "an index hit
  without a scan is at most probable" said.
- A family account alone stays in the hypothesis band (34; 45 when it is marked
  `information: primary`, e.g. a mother about her own children).

## Sources that are one record

Citations of one record count once — independent corroboration counts, duplicates do not. Sources
are one record when:

- one lists the other in `same_record_as`, or names it in `derived_from`;
- they point to the same local copy (`file`);
- they have the same `parish` (or `repository`), `year` and `act` and are cited for the same event
  (an index entry and the image of the act it indexes);
- a derivative source names the other source's ID in its `notes` or `transcription`;
- they are family accounts of the same informant (the name before the first comma or parenthesis
  of `informant`).

The breakdown shows such a source with ±0 and the reason.

## Manual labels and overrides

All new fields are optional; data written before them keeps working.

- A manual `confidence` is an **upper cap**: `probable` caps at 84, `hypothesis` at 59, `confirmed`
  caps nothing. On a person it caps the link and the person's place on every path; on a family, the
  marriage, the union and the links of its children; on an event, that fact.
- `confidence_override: {score: 0–100, reason: "…", about: link | birth | death}` (a person; a list
  for several) or `{score, reason}` (a family: the marriage) replaces the computed score. The reason
  is required and is shown with the score; the computed value stays in the breakdown.
- `conflicts: [{about, note, resolved, sources}]` records evidence that disagrees (person `about`:
  link, identity, birth, death; family: marriage, link; without `about` it touches every score of
  the record).
- `identity: {namesakes: excluded | possible, note}` records whether other persons of the same name
  were checked.
- `parentage: {sources: [...], note}` cites sources directly as evidence of the person's parents.

The field reference is in [data-format.md](data-format.md) and in `build.py --schema`.

## Exception to the weakest link: living persons

The path is the weakest link — with one deliberate exception. The links of living persons usually
rest on what the family knows first-hand: their records are younger than 100 years and not public.
Such a link keeps its honest score on the card (often a family account or nothing), its breakdown
says "living person: … does not lower the path", and a full copy of the civil certificate is
suggested — but it **does not lower the path**; only a manual label (`confidence` of the person or
the family) caps it. The same holds for the union of a couple with a living spouse. Without this
rule a proband whose own and parents' links cite nothing would hide the whole tree at any threshold.
The confidence report states the exception under its introduction, and the legend of the page next
to the band colours. A `confidence_override` on the link of a living person switches the exception
off for that link (the override then counts as the step).

## Path confidence and the filter in the page

The path to a person is the weakest step on the best path from the proband (the maximum over paths
of the minimum step). Upwards a step weighs the child's link; in the whole tree a spouse joins
through the union of the family. The page computes the paths in the browser for the proband picked
there (`templates/layout.js`, the same algorithm as `Confidence.paths()`).

The **Confidence** control in the header offers *all persons* and the named thresholds. A person is
shown when the path reaches the threshold; their ancestors are reached only through them, so a
hidden person takes the branch above with them. A counter shows how many persons are hidden; the
search list marks them; a hidden person's card says so. The PNG export draws what is shown. Every
tree card carries a small dot in the colour of its path band; the person card shows the path, the
link and the facts with "why this score" and "to strengthen". In `--public` outputs a living
person's card shows no breakdown (it would list their sources).

## The report and the JSON

`confidence.md` (Polish `pewnosc.md`) gives the bands of the links and facts, the ancestors per
generation by path, the weakest links on the line of ancestors with their breakdown and concrete
suggestions (the record to find with the parish and the years, the scan behind an index entry, the
local copy to save, the transcription to make, a second independent record, namesakes to check,
conflicts to resolve), the facts of the ancestors below probable, and manual labels that disagree
with the evidence. `build.py --json` carries the same as `confidence`: thresholds, counts, the
weakest links and the scores of every person and family.

## Limits

- The defaults are heuristics. The names in a transcription are matched by their first letters, a
  shared act number is trusted only for sources cited on the same event, and a death or marriage
  record without a transcription is treated as not naming the parents. The optional fields correct
  them where they are wrong.
- Siblings' records are not counted for a link: they show the parents, not the child.
- A score measures the evidence cited in the data, not the truth. A well-reasoned conclusion with a
  written proof argument may deserve more: record it with `confidence_override` and its reason.
