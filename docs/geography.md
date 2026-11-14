# Geography: the map and the context for research

Every build also turns the places of the family's events into a map and into a geography report
for the agent. Both come from `coords` in places.yaml; the examples below use the fictional sample
family.

## Where a place is

- A place with `coords: [lat, lon]` is drawn there.
- A place without coordinates is drawn at the coordinates of its `parish` (the map's register says
  "coordinates of the parish"). It stays in the gap report under "places to complete".
- A place with neither cannot be shown; its events are counted as "not on the map" and the place is
  listed under "Places to geocode", most events first.
- `type: region` / `country` (also `commune`, `county`) are areas: they are drawn as rings and left
  out of the heatmap, the clusters and the neighbourhood searches.

Each person contributes up to: a birth (the birth place, else the baptism place), a death (the death
place, else the burial place), a marriage (for both spouses) and residences and other events with a
place. A birth without a date gets the estimated year from the dates of the relatives (marked
"estimated").

## The map page

`map.html` (Polish `mapa.html`) and `map-artifact.html` (`mapa-artefakt.html`, without the document
skeleton, for Claude artifacts). The tree page carries the same map as its **Map** view (the
"Tree / Map" switch in its header), so one tree artifact shows both; a person's card in the tree has
"Show on the map", and a person on the map has "Show in the tree". The country outlines (Natural Earth, public domain) and the borders
of the partitions are embedded in the page, so it works without map servers; only the web fonts come
from Google Fonts.

- **Poland**: a conformal conic projection centred on Poland, with the borders of the partitions as
  they ran 1846–1914. The borders are traced by hand through towns on either side and are accurate
  to about 5–10 km — a guide for the eye. The partition of a place is its `partition` field.
- **World**: the Equal Earth projection, for emigrants.
- The heatmap shows how many of the chosen events (births, deaths, both, or all events) fall near
  each place; markers grow with the number of events. Filters: years (sliders and centuries),
  undated events, ancestors of the proband only.
- Arrows lead from a parent's place to the child's along the lines of ancestors (Kekule numbering).
- Clicking a place or a hot spot lists the people recorded there; clicking a person shows all their
  places and their route; the clusters on the right zoom to a group of places.
- `--public` leaves living persons out, as in the tree.

## The geography report (context for the agent)

`geography.md` and `geography.json` (Polish `geografia.md`, `geografia.json`) hold the same data:

| Part | What it says | Use it to |
|---|---|---|
| Clusters | places within 20 km of a centre (the busiest place), with the number of events, years, ancestors, surnames and partition | see where each branch lived and which parish books matter |
| Migration trails | for each line of ancestors, from the oldest known ancestors down to the proband, the place of each generation and the distance and direction between them | see where a line moved, so the older records are elsewhere |
| Largest moves | parent → child and birth → death changes of at least 10 km | find where a line probably changed parish or archive |
| Where to look | for each deceased ancestor without a located birth or death or without parents: a reference place (the closest located clue and why), the parishes and family places within 25 km, the nearest clusters, where the same surname occurs elsewhere (the person's own descendants left out) | choose the parishes and years to search |
| Places to geocode | places used by events but without coordinates | complete the data |

The gap report has a short "Geography" section, and the research hints of a person (in the gap
report and the tree) get one or two "Map:" lines: the parishes within 25 km of the reference place
and the nearest other family cluster.

## How the agent uses it

1. Before searching for an ancestor's birth, death or parents, read the person's entry under
   "Where to look". Start with the reference place: a woman's marriage place is usually her parish;
   a child's birth place is where the parents lived at the time.
2. Then search the neighbouring parishes nearest first, within the estimated years. Rural families
   mostly married and moved within 10–20 km; the list only knows parishes that are already in
   places.yaml, so look up the others (the diocese's list of parishes, `scripts/geneteka.py
   --parishes -w CODE`) and add them with coordinates.
3. A cluster of the same surname in another place (e.g. Nowak in Wzorki while the line of Kowalski
   lives around Przykładowo) is a lead for collateral relatives and witnesses, not a link.
4. A long move on a trail (e.g. Wzorki → Zmyślin, about 230 km) means the older generations are in
   another archive, often in another partition with records in another language.
5. Record what you searched in `research/log.md` as usual; nothing in the report is evidence.

The thresholds (20 km clusters, 25 km neighbourhood, 10 km moves) are in `familytree/geo.py`.
