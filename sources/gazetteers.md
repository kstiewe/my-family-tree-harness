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

A place you cannot identify yet: record it with what is known (`notes`: the spelling in the source,
the candidates) and add a `todo` — the gap report lists places without a parish.
