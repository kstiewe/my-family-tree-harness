"""Rebuild world.json and europe.json from the world-atlas TopoJSON files (Natural Earth).

    python3 -I familytree/geodata/prepare.py DIR

DIR holds countries-110m.json and countries-50m.json of the npm package world-atlas@2.0.2. The
output is a small format the map page decodes without libraries:

    {"q": 50, "land": [ring, …], "borders": [line, …]}

Each ring/line is a flat list [x0, y0, dx1, dy1, …] of longitude/latitude multiplied by q and
delta-encoded. `land` are the land polygons (filled), `borders` the country borders (arcs shared by
two countries; coastlines are the edges of the land). Not used at run time; stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EUROPE_BOX = (3.0, 42.0, 40.0, 61.0)            # lon_min, lat_min, lon_max, lat_max


def decode_arcs(topo: dict) -> list[list[tuple[float, float]]]:
    (sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x, y = x + dx, y + dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def ring_points(arcs, refs: list[int]) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for r in refs:
        a = arcs[r] if r >= 0 else arcs[~r][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def polygons(geom: dict) -> list[list[list[int]]]:
    if geom["type"] == "Polygon":
        return [geom["arcs"]]
    if geom["type"] == "MultiPolygon":
        return geom["arcs"]
    if geom["type"] == "GeometryCollection":
        return [p for g in geom["geometries"] for p in polygons(g)]
    return []


def clip_ring(pts, box):
    """Sutherland–Hodgman clipping of a closed ring to a rectangle."""
    x0, y0, x1, y1 = box
    edges = [(lambda p: p[0] >= x0, lambda a, b: _ix(a, b, x0)), (lambda p: p[0] <= x1, lambda a, b: _ix(a, b, x1)),
             (lambda p: p[1] >= y0, lambda a, b: _iy(a, b, y0)), (lambda p: p[1] <= y1, lambda a, b: _iy(a, b, y1))]
    for inside, cut in edges:
        if not pts:
            break
        src, pts = pts, []
        prev = src[-1]
        for cur in src:
            if inside(cur):
                if not inside(prev):
                    pts.append(cut(prev, cur))
                pts.append(cur)
            elif inside(prev):
                pts.append(cut(prev, cur))
            prev = cur
    return pts


def _ix(a, b, x):
    t = (x - a[0]) / (b[0] - a[0])
    return (x, a[1] + t * (b[1] - a[1]))


def _iy(a, b, y):
    t = (y - a[1]) / (b[1] - a[1])
    return (a[0] + t * (b[0] - a[0]), y)


def clip_line(pts, box):
    """Split a polyline into the pieces inside a (slightly larger) rectangle."""
    x0, y0, x1, y1 = box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1
    pieces, cur = [], []
    for p in pts:
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
            cur.append(p)
        elif cur:
            pieces.append(cur + [p])
            cur = []
    if cur:
        pieces.append(cur)
    return [c for c in pieces if len(c) > 1]


def unwrap(pts):
    """Make longitudes continuous where a ring jumps across the antimeridian (179 → -179 becomes 181)."""
    out, shift = [], 0.0
    for i, (x, y) in enumerate(pts):
        if i:
            d = x + shift - out[-1][0]
            if d > 180:
                shift -= 360
            elif d < -180:
                shift += 360
        out.append((x + shift, y))
    return out


def world_rings(ring):
    """A ring that crosses the antimeridian, as pieces inside -180..180."""
    ring = unwrap(ring)
    lo, hi = min(x for x, _ in ring), max(x for x, _ in ring)
    if lo >= -180 and hi <= 180:
        return [ring]
    pieces = []
    for off in (-360, 0, 360):
        part = clip_ring([(x + off, y) for x, y in ring], (-180, -90, 180, 90))
        if len(part) >= 3:
            pieces.append(part)
    return pieces


def split_jumps(pts):
    pieces, cur = [], [pts[0]]
    for a, b in zip(pts, pts[1:]):
        if abs(b[0] - a[0]) > 180:
            pieces.append(cur)
            cur = []
        cur.append(b)
    return [c for c in pieces + [cur] if len(c) > 1]


def encode(pts, q: int) -> list[int]:
    flat, last = [], None
    px = py = 0
    for x, y in pts:
        ix, iy = round(x * q), round(y * q)
        if (ix, iy) == last:
            continue
        flat += [ix - px, iy - py] if last else [ix, iy]
        px, py, last = ix, iy, (ix, iy)
    return flat


def build(topo: dict, q: int, box=None) -> dict:
    arcs = decode_arcs(topo)
    land = []
    for poly in polygons(topo["objects"]["land"]):
        for refs in poly:
            ring = ring_points(arcs, refs)
            for piece in [clip_ring(ring, box)] if box else world_rings(ring):
                enc = encode(piece, q)
                if len(enc) >= 6:
                    land.append(enc)
    uses: dict[int, int] = {}
    for g in topo["objects"]["countries"]["geometries"]:
        for poly in polygons(g):
            for refs in poly:
                for r in refs:
                    uses[r if r >= 0 else ~r] = uses.get(r if r >= 0 else ~r, 0) + 1
    borders = []
    for i, n in sorted(uses.items()):
        if n < 2:
            continue
        for piece in (clip_line(arcs[i], box) if box else split_jumps(arcs[i])):
            enc = encode(piece, q)
            if len(enc) >= 4:
                borders.append(enc)
    return {"q": q, "land": land, "borders": borders}


def main(argv: list[str]) -> int:
    src = Path(argv[0]) if argv else Path(".")
    note = "Natural Earth (public domain) via world-atlas 2.0.2 (ISC); see README.md"
    for name, file, q, box in (("world.json", "countries-110m.json", 50, None),
                               ("europe.json", "countries-50m.json", 200, EUROPE_BOX)):
        topo = json.loads((src / file).read_text(encoding="utf-8"))
        data = {"source": note, **build(topo, q, box)}
        if box:
            data["box"] = list(box)
        (HERE / name).write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
        print(name, (HERE / name).stat().st_size, "bytes", len(data["land"]), "rings", len(data["borders"]), "borders")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
