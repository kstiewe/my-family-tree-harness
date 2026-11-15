# Finding villages and their parishes

The parish decides where the records are. Record it in `places.yaml` (`parish`, `partition`,
`geneteka_region`, `coords`, historical names in `aliases`).

- **Wikipedia (Polish)**: the commune, sometimes the parish. Watch out for disambiguation pages —
  several villages often share a name. Add the commune or county to the search, e.g.
  "Przykładowo wieś powiat przykładowski gmina".
- **polskawliczbach.pl** and **PRNG** (the national register of geographic names): coordinates and
  current administrative units.
- **[Słownik geograficzny Królestwa Polskiego](https://dir.icm.edu.pl/Slownik_geograficzny/)**
  (19th century): `https://dir.icm.edu.pl/pl/Slownik_geograficzny/Tom_<volume>/<page>`. First comes
  "Sprawdzamy, czy nie jesteś botem!" — wait a few seconds. The parish is in the village's entry, or
  the village is listed in the parish's entry — this also lets you rule a parish out.
- **[Meyers Gazetteer](https://www.meyersgaz.org)**: the German Empire (~1912) with Catholic and
  Protestant parishes and the civil registry office — the Prussian partition.
- **[Polona](https://polona.pl)** and **[FBC](https://fbc.pionier.net.pl)**: place indexes, maps,
  address books.
- **Mapster** (igrek.amzp.pl): old topographic maps (WIG, German); often unavailable.
- **German administrative history**: see [german-sources.md](german-sources.md) (GenWiki, territorial.de).
- `python3 scripts/geneteka.py --parishes -w CODE --filter NAME`: whether Geneteka knows the parish,
  its indexed years and IDs.

Records spell places in German, Polish, Kashubian or by ear, and the same village may appear under two
unrelated German names. A record that writes two forms side by side ("Musterdorf (Przykładowo)") settles
the identification — note such a record in the place's `notes`.

A place you cannot identify yet: record it with what is known (`notes`: the spelling in the source,
the candidates) and add a `todo` — the gap report lists places without a parish.

## Coordinates (`coords`)

The map and the geography context (docs/geography.md) need `coords: [latitude, longitude]` of each
place, or at least of its parish. One targeted lookup per place, never a bulk download:

- **OpenStreetMap Nominatim** (`https://nominatim.openstreetmap.org/search?format=json&q=…`): add the
  commune or county and the country to the query ("Przykładowo, gmina Wzorcowo, Polska"); at most one
  request per second, with a descriptive User-Agent. Check the result's `display_name` — the commune
  and county must match, not just the name.
- **PRNG** and **polskawliczbach.pl**: the official coordinates of Polish villages, useful when the
  name is shared by several villages.
- **Wikipedia**: the coordinates in the infobox (the GeoHack link).
- A village that no longer exists or cannot be told apart from its namesakes: leave `coords` out (the
  map uses the parish) and say why in `notes`.

Write the source in `notes` ("coords: OpenStreetMap Nominatim, 2026-11-14"). Coordinates of a parish
are those of its church or village; a place known only as a region or country gets the `type`
`region` or `country` and is drawn as a ring, not counted in clusters.
