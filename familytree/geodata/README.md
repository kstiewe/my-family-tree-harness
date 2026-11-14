# Map geometry

Embedded in the map page (`familytree/geomap.py`); nothing here is family data.

| File | What | Source |
|---|---|---|
| `world.json` | land and country borders of the world, 1:110 million | Natural Earth (public domain) via the npm package world-atlas 2.0.2 (`countries-110m.json`, ISC licence, © Michael Bostock) |
| `europe.json` | land and country borders of Central Europe (3–40° E, 42–61° N), 1:50 million | the same, `countries-50m.json` |
| `overlay.json` | borders of the partitions of Poland, about 1846–1914, and the positions of their labels | drawn by hand for this project through towns known to lie on either side; accurate to about 5–10 km |

`world.json` and `europe.json` are rebuilt with `python3 -I familytree/geodata/prepare.py DIR`, where
DIR holds the two world-atlas files. The format is described in `prepare.py`.
