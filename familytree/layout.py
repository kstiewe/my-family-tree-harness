"""Layout of the HTML diagram in generation lanes.

Each generation is a horizontal lane (the oldest at the top). Within a lane people form "units"
(spouses side by side). The order comes from anchors: the proband's ancestors in Kekule order
(father's line on the left, mother's on the right), their siblings right next to them on the outside,
everyone else next to the closest relative. Relaxation gives the x coordinates: siblings packed
under their parents, parents above their children, keeping the order and the gaps.
"""

from __future__ import annotations

from .i18n import tr
from .model import Tree

CARD_W, CARD_H = 190, 78
SPOUSE_GAP, SIB_GAP, GROUP_GAP = 34, 16, 48
ROW_GAP = 104                       # between lanes: marriage marker under the couple and lines to children


def lane_name(g: int) -> str:
    names = {0: tr("proband, siblings and cousins"), 1: tr("parents"), 2: tr("grandparents"), 3: tr("great-grandparents"),
             4: tr("great-great-grandparents"), -1: tr("peers of the proband's children"),
             -2: tr("peers of the proband's grandchildren"), -3: tr("peers of the proband's great-grandchildren")}
    if g in names:
        return names[g]
    return tr("{n} generations back", n=g) if g > 0 else tr("descendant generation {n}", n=-g)


def generations(tree: Tree) -> dict[str, int]:
    """Generation relative to the proband: 0 = proband, +1 parents, −1 children; a spouse shares the partner's."""
    pb = tree.project.get("proband")
    pb_year = tree.birth_year(tree.persons[pb]) if pb in tree.persons else None
    gen: dict[str, int] = {}
    for start in ([pb] if pb in tree.persons else []) + list(tree.persons):
        if start in gen:
            continue
        year = tree.birth_year(tree.persons[start])
        gen[start] = 0 if start == pb else (round((pb_year - year) / 30) if pb_year and year else 0)
        queue = [start]
        while queue:
            pid = queue.pop(0)
            near = [(x, 1) for x in tree.parents(pid)]
            for fid in tree.spouse_in.get(pid, []):
                f = tree.families[fid]
                near += [(f[r], 0) for r in ("husband", "wife") if f.get(r) and f[r] != pid]
                near += [(c, -1) for c in f.get("children") or []]
            for x, d in near:
                if x in tree.persons and x not in gen:
                    gen[x] = gen[pid] + d
                    queue.append(x)
    return gen


def _unit_order(comp: list[str], spouses: dict[str, list[str]], tree: Tree) -> list[str]:
    """Order of spouses in a unit: a chain (a person with two marriages in the middle), the man first."""
    if len(comp) == 1:
        return comp
    sexkey = lambda p: (tree.persons[p].get("sex") != "M", p)
    ends = [p for p in comp if len(spouses[p]) == 1]
    if ends and all(len(spouses[p]) <= 2 for p in comp):
        out = [min(ends, key=sexkey)]
        while len(out) < len(comp):
            nxt = [y for y in spouses[out[-1]] if y not in out]
            if not nxt:
                break
            out.append(nxt[0])
        if len(out) == len(comp):
            return out
    hub = max(comp, key=lambda p: len(spouses[p]))
    rest = sorted((p for p in comp if p != hub), key=sexkey)
    return rest[:len(rest) // 2] + [hub] + rest[len(rest) // 2:]


def _place_row(desired: list[float], weights: list[float], seps: list[float]) -> list[float]:
    """Closest (weighted) block positions that keep the order and minimum gaps (isotonic regression)."""
    off = [0.0]
    for s in seps:
        off.append(off[-1] + s)
    pools: list[list[float]] = []                       # [sum of weights, sum of weighted values, count]
    for d, o, w in zip(desired, off, weights):
        pools.append([w, w * (d - o), 1])
        while len(pools) > 1 and pools[-2][1] / pools[-2][0] > pools[-1][1] / pools[-1][0]:
            w2, s2, c2 = pools.pop()
            pools[-1][0] += w2
            pools[-1][1] += s2
            pools[-1][2] += c2
    out: list[float] = []
    for w, s, c in pools:
        out += [s / w] * int(c)
    return [y + o for y, o in zip(out, off)]


def layout_view(tree: Tree, pids: list[str], fids: list[str], gen: dict[str, int], public: bool) -> dict:
    if not pids:
        return {"w": 0, "h": 0, "nodes": {}, "fams": [], "lanes": []}
    shown = set(pids)
    fams = {fid: tree.families[fid] for fid in fids}
    pin = {fid: [x for x in (f.get("husband"), f.get("wife")) if x in shown] for fid, f in fams.items()}
    kin = {fid: [c for c in f.get("children") or [] if c in shown] for fid, f in fams.items()}
    par_of: dict[str, str] = {}
    for fid in fams:
        if pin[fid]:
            for c in kin[fid]:
                par_of.setdefault(c, fid)
    own = {p: [fid for fid in tree.spouse_in.get(p, []) if fid in fams and kin[fid]] for p in pids}
    spouses: dict[str, list[str]] = {p: [] for p in pids}
    for fid in fams:
        ps = pin[fid]
        if len(ps) == 2 and gen[ps[0]] == gen[ps[1]]:
            spouses[ps[0]].append(ps[1])
            spouses[ps[1]].append(ps[0])
    gens = sorted({gen[p] for p in pids}, reverse=True)
    R, row_of = len(gens), {g: i for i, g in enumerate(gens)}
    byear = {p: tree.birth_year(tree.persons[p]) for p in pids}

    def anchor(p: str) -> float | None:                 # ancestor's slot in its generation by Kekule number
        nums = tree.kekule.get(p)
        if not nums:
            return None
        n = min(nums)
        k = n.bit_length() - 1
        return (n - (1 << k) + 0.5) / (1 << k)

    rows: list[list[list[str]]] = [[] for _ in range(R)]
    seen: set[str] = set()
    for pid in pids:
        if pid in seen:
            continue
        comp, stack = [], [pid]
        seen.add(pid)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in spouses[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        rows[row_of[gen[pid]]].append(_unit_order(comp, spouses, tree))

    # -- unit geometry, packing a lane and relaxation
    step = CARD_W + SPOUSE_GAP
    width = lambda u: len(u) * CARD_W + (len(u) - 1) * SPOUSE_GAP
    sibs = lambda u, v: any(par_of.get(a) and par_of.get(a) == par_of.get(b) for a in u for b in v)
    sep = lambda u, v: width(u) + (SIB_GAP if sibs(u, v) else GROUP_GAP)
    seps = lambda row: [sep(row[i], row[i + 1]) for i in range(len(row) - 1)]
    X: list[list[float]] = []
    where: dict[str, tuple[int, int, int]] = {}
    cx = lambda p: X[where[p][0]][where[p][1]] + where[p][2] * step + CARD_W / 2
    drop_x = lambda fid: sum(map(cx, pin[fid])) / len(pin[fid])
    kids_x = lambda fid: sum(map(cx, kin[fid])) / len(kin[fid])
    anc_key = lambda u: min((a for a in map(anchor, u) if a is not None), default=2.0)

    def turn(u: list[str], pos: dict[str, float]) -> list[str]:
        """Ancestors in Kekule order (husband on the left); other couples flipped only for a clear gain."""
        anc = [anchor(p) for p in u]
        if sum(a is not None for a in anc) >= 2:
            known = [a for a in anc if a is not None]
            return u if known == sorted(known) else u[::-1]
        pulls = [sum(pos[x] for x in pin[par_of[p]]) / len(pin[par_of[p]]) if p in par_of else None for p in u]
        c0 = sum(pos[p] for p in u) / len(u)
        cost = lambda vals: sum(abs(v - (c0 + (j - (len(u) - 1) / 2) * step)) for j, v in enumerate(vals) if v is not None)
        return u[::-1] if cost(pulls[::-1]) < cost(pulls) - CARD_W / 2 else u

    def repack(pos: dict[str, float] | None) -> None:
        X.clear()
        for row in rows:
            if pos:
                des = [sum(pos[p] for p in u) / len(u) - width(u) / 2 for u in row]
                X.append(_place_row(des, [1.0] * len(row), seps(row)))
            else:
                xs, x = [], 0.0
                for i, u in enumerate(row):
                    xs.append(x)
                    x += sep(u, row[i + 1]) if i + 1 < len(row) else 0
                X.append(xs)
        where.clear()
        where.update({p: (r, i, j) for r, row in enumerate(rows) for i, u in enumerate(row) for j, p in enumerate(u)})

    def relax(rounds: int) -> None:
        for it in range(rounds):
            for r in (range(R) if it % 2 == 0 else range(R - 1, -1, -1)):
                row = rows[r]
                if not row:
                    continue
                num, den = [0.0] * len(row), [0.0] * len(row)
                groups: dict[str, list[int]] = {}       # siblings packed and centred under their parents
                for i, u in enumerate(row):
                    for fid in dict.fromkeys(par_of[p] for p in u if p in par_of):
                        groups.setdefault(fid, []).append(i)
                for fid, idx in groups.items():
                    x = drop_x(fid) - (sum(width(row[i]) for i in idx) + SIB_GAP * (len(idx) - 1)) / 2
                    for i in idx:
                        num[i] += x
                        den[i] += 1
                        x += width(row[i]) + SIB_GAP
                for i, u in enumerate(row):             # parents above the middle of their children
                    for fid in {fid for p in u for fid in own[p]}:
                        num[i] += len(kin[fid]) * (X[r][i] + kids_x(fid) - drop_x(fid))
                        den[i] += len(kin[fid])
                X[r] = _place_row([num[i] / den[i] if den[i] else X[r][i] for i in range(len(row))],
                                  [den[i] or 0.05 for i in range(len(row))], seps(row))

    # anchors: an ancestor sits at its Kekule slot; its siblings right next to it, on the outside (father's line
    # to the left, mother's to the right); everyone else inherits the anchor of the closest relative
    vkey: dict[str, float] = {p: anchor(p) for p in pids if anchor(p) is not None}
    for p in pids:                                      # siblings, half-siblings too (at least one shared parent)
        sib_anc = [x for q in (pin[par_of[p]] if p in par_of else []) for f in own[q] for x in kin[f] if x in tree.kekule]
        if p not in vkey and sib_anc:
            a = min(sib_anc, key=lambda x: min(tree.kekule[x]))
            vkey[p] = anchor(a) + (-1e-4 if min(tree.kekule[a]) % 2 == 0 else 1e-4)
    queue = list(vkey)
    while queue:
        p = queue.pop(0)
        near = list(spouses[p]) + [c for f in own[p] for c in kin[f]] + (pin[par_of[p]] if p in par_of else [])
        for x in near:
            if x not in vkey:
                vkey[x] = vkey[p]
                queue.append(x)
    order_key = lambda u: (anc_key(u) if anc_key(u) < 2 else sum(vkey.get(p, 2.0) for p in u) / len(u),
                           min((byear[p] for p in u if byear[p]), default=9999), u[0])
    for row in rows:
        row.sort(key=order_key)
    repack(None)
    relax(40)
    pos = {p: cx(p) for p in pids}
    rows[:] = [[turn(u, pos) for u in row] for row in rows]
    repack(pos)
    relax(300)

    pad_x, pad_y = 40, round(ROW_GAP * 0.45) + 10
    shift = pad_x - min(xs[0] for xs in X if xs)
    X = [[x + shift for x in xs] for xs in X]
    top = lambda r: pad_y + r * (CARD_H + ROW_GAP)
    nodes = {p: [round(cx(p) - CARD_W / 2), top(where[p][0])] for p in pids}
    w = max(cx(p) + CARD_W / 2 for p in pids) + pad_x
    h = top(R - 1) + CARD_H + round(ROW_GAP * 0.55)

    # -- lines: couple, drop from the couple, sibling bar (on tracks so they do not overlap), stems to children
    out_fams, bars = [], {}
    for fid in fids:
        ps, ks = pin[fid], kin[fid]
        if not ps:
            continue
        f, rec = fams[fid], {"id": fid, "parents": ps, "children": ks, "stems": {}, "extra": []}
        rows_p = {where[p][0] for p in ps}
        low = max(ps, key=lambda p: where[p][0])
        if len(ps) == 2 and len(rows_p) == 1:
            a, b = sorted(ps, key=cx)
            y = top(where[a][0]) + CARD_H / 2
            if abs(where[a][2] - where[b][2]) == 1 and where[a][1] == where[b][1]:
                rec["couple"] = [[cx(a) + CARD_W / 2, y], [cx(b) - CARD_W / 2, y]]
                start = y
            else:
                yb = top(where[a][0]) + CARD_H + 8
                rec["couple"] = [[cx(a), yb - 8], [cx(a), yb], [cx(b), yb], [cx(b), yb - 8]]
                start = yb
            dx = drop_x(fid)
            md = tree.date(f, "marriage")
            hidden = public and any(tree.living(x) for x in ps)
            rec["pill"] = {"x": dx, "y": top(where[a][0]) + CARD_H + 15,
                           "t": "⚭ " + md.text() if md and not hidden else "⚭"}
        else:
            dx = cx(low)
            start = top(where[low][0]) + CARD_H
            for p in ps:
                if p != low:
                    rec["extra"].append([[cx(p), top(where[p][0]) + CARD_H], [dx, start]])
        if ks:
            xs = [cx(c) for c in ks] + [dx]
            r_child = min(where[c][0] for c in ks)
            bars.setdefault(r_child, []).append((min(xs), max(xs), rec, dx, start))
        out_fams.append(rec)
    for r_child, items in bars.items():
        tracks: list[float] = []
        for lo, hi, rec, dx, start in sorted(items, key=lambda t: t[0]):
            t = next((i for i, end in enumerate(tracks) if end < lo - 8), len(tracks))
            if t < len(tracks):
                tracks[t] = hi
            else:
                tracks.append(hi)
            yb = top(r_child) - 22 - 9 * t
            rec["drop"] = [[dx, start], [dx, yb]]
            if hi - lo > 1:
                rec["bar"] = [[lo, yb], [hi, yb]]
            for c in rec["children"]:
                rec["stems"][c] = [[cx(c), yb], [cx(c), top(where[c][0])]]

    lanes = []
    for r, g in enumerate(gens):
        years = sorted(byear[p] for p in pids if gen[p] == g and byear[p] and not (public and tree.living(p)))
        lanes.append({"y": top(r) - round(ROW_GAP * 0.45), "h": CARD_H + ROW_GAP,
                      "title": tr("Generation {n}", n=g + 1) if g >= 0 else tr("Younger generation") + (f" ({-g})" if g < -1 else ""),
                      "name": lane_name(g),
                      "years": "" if not years else tr("b. {years}", years=years[0] if years[0] == years[-1] else f"{years[0]}–{years[-1]}")})
    rnd = lambda v: round(v, 1)
    for rec in out_fams:
        for k in ("couple", "drop", "bar"):
            if k in rec:
                rec[k] = [[rnd(x), rnd(y)] for x, y in rec[k]]
        rec["stems"] = {c: [[rnd(x), rnd(y)] for x, y in pts] for c, pts in rec["stems"].items()}
        rec["extra"] = [[[rnd(x), rnd(y)] for x, y in pts] for pts in rec["extra"]]
        if "pill" in rec:
            rec["pill"]["x"], rec["pill"]["y"] = rnd(rec["pill"]["x"]), rnd(rec["pill"]["y"])
    return {"w": round(w), "h": round(h), "card": [CARD_W, CARD_H], "nodes": nodes, "fams": out_fams, "lanes": lanes}


def html_views(tree: Tree, public: bool) -> dict:
    gen = generations(tree)
    anc = sorted(tree.kekule, key=lambda pid: min(tree.kekule[pid]))
    return {"full": layout_view(tree, list(tree.persons), list(tree.families), gen, public),
            "anc": layout_view(tree, anc, tree.ancestral_families(), gen, public)}
