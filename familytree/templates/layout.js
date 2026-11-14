// Layout of the tree diagram in generation lanes. It runs in the page, so any person can be the proband, and it is
// a pure function of the exported data (no DOM): the tests run it in node.
//
// Each generation is a horizontal lane (the oldest at the top). Within a lane people form "units" (spouses side by
// side). The order comes from anchors: the proband's ancestors in Kekule order (father's line on the left, mother's on
// the right), their siblings right next to them on the outside, everyone else next to the closest relative. Relaxation
// gives the x coordinates: siblings packed under their parents, parents above their children, keeping the order and
// the gaps.
const TreeLayout = (() => {
  const CARD_W = 190, CARD_H = 78, SPOUSE_GAP = 34, SIB_GAP = 16, GROUP_GAP = 48;
  const ROW_GAP = 104;                     // between lanes: marriage marker under the couple and lines to children

  const roundEven = x => { const r = Math.round(x); return Math.abs(x % 1) === 0.5 && r % 2 ? r - 1 : r; };
  const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
  const cmpKey = (a, b) => { for (let i = 0; i < a.length; i++) { if (a[i] < b[i]) return -1; if (a[i] > b[i]) return 1; } return 0; };
  const bitLength = n => { let k = 0; while (2 ** k <= n) k++; return k; };

  // ---- relations

  /** Indexes of the exported families: parents' family of a child, families of a spouse. */
  function graph(D) {
    const childOf = {}, spouseIn = {};
    for (const [fid, f] of Object.entries(D.families)) {
      for (const x of [f.h, f.w]) if (x) (spouseIn[x] ??= []).push(fid);
      for (const c of f.c) (childOf[c] ??= []).push(fid);
    }
    const parentsFamily = pid => childOf[pid] ? D.families[childOf[pid][0]] : null;
    const parents = pid => { const f = parentsFamily(pid); return f ? [f.h, f.w].filter(Boolean) : []; };
    return { childOf, spouseIn, parentsFamily, parents };
  }

  /** Kekule numbers of the ancestors of `pb`: proband = 1, father of n = 2n, mother = 2n+1. */
  function kekule(D, G, pb) {
    const nums = {};
    if (!D.persons[pb]) return nums;
    const queue = [[pb, 1]];
    for (let i = 0; i < queue.length; i++) {
      const [pid, n] = queue[i];
      if (bitLength(n) > 40) continue;
      (nums[pid] ??= []).push(n);
      const f = G.parentsFamily(pid);
      if (f && D.persons[f.h]) queue.push([f.h, 2 * n]);
      if (f && D.persons[f.w]) queue.push([f.w, 2 * n + 1]);
    }
    return nums;
  }

  /** Generation relative to `pb`: 0 = proband, +1 parents, −1 children; a spouse shares the partner's. */
  function generations(D, G, pb) {
    const P = D.persons, pbYear = P[pb] ? P[pb].by : null, gen = {};
    for (const start of [...(P[pb] ? [pb] : []), ...Object.keys(P)]) {
      if (start in gen) continue;
      const year = P[start].by;
      gen[start] = start === pb ? 0 : pbYear && year ? roundEven((pbYear - year) / 30) : 0;
      const queue = [start];
      for (let i = 0; i < queue.length; i++) {
        const pid = queue[i], near = G.parents(pid).map(x => [x, 1]);
        for (const fid of G.spouseIn[pid] || []) {
          const f = D.families[fid];
          for (const x of [f.h, f.w]) if (x && x !== pid) near.push([x, 0]);
          for (const c of f.c) near.push([c, -1]);
        }
        for (const [x, d] of near) if (P[x] && !(x in gen)) { gen[x] = gen[pid] + d; queue.push(x); }
      }
    }
    return gen;
  }

  /** Families of the parents of every ancestor, the closest to the proband first. */
  function ancestralFamilies(D, G, kek) {
    const fids = [...new Set(Object.keys(kek).filter(p => G.childOf[p]).map(p => G.childOf[p][0]))];
    const key = Object.fromEntries(fids.map(fid => [fid, Math.min(...D.families[fid].c.map(c => kek[c] ? Math.min(...kek[c]) : 1e12))]));
    return fids.sort((a, b) => key[a] - key[b]);
  }

  function laneName(g) {
    const names = {0: '⟦proband, siblings and cousins⟧', 1: '⟦parents⟧', 2: '⟦grandparents⟧', 3: '⟦great-grandparents⟧',
                   4: '⟦great-great-grandparents⟧', '-1': "⟦peers of the proband's children⟧",
                   '-2': "⟦peers of the proband's grandchildren⟧", '-3': "⟦peers of the proband's great-grandchildren⟧"};
    if (g in names) return names[g];
    const n = Math.abs(g);
    return g > 0 ? `⟦${n} generations back⟧` : `⟦descendant generation ${n}⟧`;
  }

  // ---- placing a view

  /** Order of spouses in a unit: a chain (a person with two marriages in the middle), the man first. */
  function unitOrder(comp, spouses, P) {
    if (comp.length === 1) return comp;
    const key = p => [P[p].sex !== 'M' ? 1 : 0, p];
    const ends = comp.filter(p => spouses[p].length === 1);
    if (ends.length && comp.every(p => spouses[p].length <= 2)) {
      const out = [ends.reduce((best, p) => cmpKey(key(p), key(best)) < 0 ? p : best)];
      while (out.length < comp.length) {
        const nxt = spouses[out.at(-1)].filter(y => !out.includes(y));
        if (!nxt.length) break;
        out.push(nxt[0]);
      }
      if (out.length === comp.length) return out;
    }
    const hub = comp.reduce((best, p) => spouses[p].length > spouses[best].length ? p : best);
    const rest = comp.filter(p => p !== hub).sort((a, b) => cmpKey(key(a), key(b)));
    const half = Math.floor(rest.length / 2);
    return [...rest.slice(0, half), hub, ...rest.slice(half)];
  }

  /** Closest (weighted) block positions that keep the order and minimum gaps (isotonic regression). */
  function placeRow(desired, weights, seps) {
    const off = [0];
    for (const s of seps) off.push(off.at(-1) + s);
    const pools = [];                      // [sum of weights, sum of weighted values, count]
    desired.forEach((d, i) => {
      pools.push([weights[i], weights[i] * (d - off[i]), 1]);
      while (pools.length > 1 && pools.at(-2)[1] / pools.at(-2)[0] > pools.at(-1)[1] / pools.at(-1)[0]) {
        const [w2, s2, c2] = pools.pop(), last = pools.at(-1);
        last[0] += w2; last[1] += s2; last[2] += c2;
      }
    });
    const out = [];
    for (const [w, s, c] of pools) for (let k = 0; k < c; k++) out.push(s / w);
    return out.map((y, i) => y + off[i]);
  }

  function layoutView(D, G, pids, fids, gen, kek) {
    if (!pids.length) return { w: 0, h: 0, card: [CARD_W, CARD_H], nodes: {}, fams: [], lanes: [] };
    const P = D.persons, shown = new Set(pids), inView = new Set(fids);
    const pin = {}, kin = {}, parOf = {};
    for (const fid of fids) {
      const f = D.families[fid];
      pin[fid] = [f.h, f.w].filter(x => x && shown.has(x));
      kin[fid] = f.c.filter(c => shown.has(c));
    }
    for (const fid of fids) if (pin[fid].length) for (const c of kin[fid]) parOf[c] ??= fid;
    const own = Object.fromEntries(pids.map(p => [p, (G.spouseIn[p] || []).filter(fid => inView.has(fid) && kin[fid].length)]));
    const spouses = Object.fromEntries(pids.map(p => [p, []]));
    for (const fid of fids) {
      const ps = pin[fid];
      if (ps.length === 2 && gen[ps[0]] === gen[ps[1]]) { spouses[ps[0]].push(ps[1]); spouses[ps[1]].push(ps[0]); }
    }
    const gens = [...new Set(pids.map(p => gen[p]))].sort((a, b) => b - a);
    const R = gens.length, rowOf = new Map(gens.map((g, i) => [g, i]));
    const byear = Object.fromEntries(pids.map(p => [p, P[p].by]));

    const anchor = p => {                  // ancestor's slot in its generation by Kekule number
      if (!kek[p]) return null;
      const n = Math.min(...kek[p]), k = 2 ** (bitLength(n) - 1);
      return (n - k + 0.5) / k;
    };

    const rows = Array.from({ length: R }, () => []);
    const seen = new Set();
    for (const pid of pids) {
      if (seen.has(pid)) continue;
      const comp = [], stack = [pid];
      seen.add(pid);
      while (stack.length) {
        const x = stack.pop();
        comp.push(x);
        for (const y of spouses[x]) if (!seen.has(y)) { seen.add(y); stack.push(y); }
      }
      rows[rowOf.get(gen[pid])].push(unitOrder(comp, spouses, P));
    }

    // -- unit geometry, packing a lane and relaxation
    const step = CARD_W + SPOUSE_GAP;
    const width = u => u.length * CARD_W + (u.length - 1) * SPOUSE_GAP;
    const sibs = (u, v) => u.some(a => parOf[a] && v.some(b => parOf[a] === parOf[b]));
    const sep = (u, v) => width(u) + (sibs(u, v) ? SIB_GAP : GROUP_GAP);
    const seps = row => row.slice(0, -1).map((u, i) => sep(u, row[i + 1]));
    let X = [];
    const where = {};
    const cx = p => { const [r, i, j] = where[p]; return X[r][i] + j * step + CARD_W / 2; };
    const dropX = fid => mean(pin[fid].map(cx));
    const kidsX = fid => mean(kin[fid].map(cx));
    const ancKey = u => Math.min(2, ...u.map(anchor).filter(a => a !== null));

    function turn(u, pos) {                // ancestors in Kekule order (husband on the left); other couples flipped only for a clear gain
      const known = u.map(anchor).filter(a => a !== null);
      if (known.length >= 2) return known.every((a, i) => !i || known[i - 1] <= a) ? u : [...u].reverse();
      const pulls = u.map(p => parOf[p] ? mean(pin[parOf[p]].map(x => pos[x])) : null);
      const c0 = mean(u.map(p => pos[p]));
      const cost = vals => vals.reduce((s, v, j) => v === null ? s : s + Math.abs(v - (c0 + (j - (u.length - 1) / 2) * step)), 0);
      return cost([...pulls].reverse()) < cost(pulls) - CARD_W / 2 ? [...u].reverse() : u;
    }

    function repack(pos) {
      X = rows.map(row => {
        if (pos) return placeRow(row.map(u => mean(u.map(p => pos[p])) - width(u) / 2), row.map(() => 1), seps(row));
        const xs = [];
        let x = 0;
        row.forEach((u, i) => { xs.push(x); if (i + 1 < row.length) x += sep(u, row[i + 1]); });
        return xs;
      });
      rows.forEach((row, r) => row.forEach((u, i) => u.forEach((p, j) => { where[p] = [r, i, j]; })));
    }

    function relax(rounds) {
      for (let it = 0; it < rounds; it++) {
        for (let k = 0; k < R; k++) {
          const r = it % 2 === 0 ? k : R - 1 - k, row = rows[r];
          const num = row.map(() => 0), den = row.map(() => 0);
          const groups = new Map();        // siblings packed and centred under their parents
          row.forEach((u, i) => {
            for (const fid of new Set(u.filter(p => parOf[p]).map(p => parOf[p]))) {
              if (!groups.has(fid)) groups.set(fid, []);
              groups.get(fid).push(i);
            }
          });
          for (const [fid, idx] of groups) {
            let x = dropX(fid) - (idx.reduce((s, i) => s + width(row[i]), 0) + SIB_GAP * (idx.length - 1)) / 2;
            for (const i of idx) { num[i] += x; den[i] += 1; x += width(row[i]) + SIB_GAP; }
          }
          row.forEach((u, i) => {          // parents above the middle of their children
            for (const fid of new Set(u.flatMap(p => own[p]))) {
              num[i] += kin[fid].length * (X[r][i] + kidsX(fid) - dropX(fid));
              den[i] += kin[fid].length;
            }
          });
          X[r] = placeRow(row.map((u, i) => den[i] ? num[i] / den[i] : X[r][i]), den.map(d => d || 0.05), seps(row));
        }
      }
    }

    // anchors: an ancestor sits at its Kekule slot; its siblings right next to it, on the outside (father's line
    // to the left, mother's to the right); everyone else inherits the anchor of the closest relative
    const vkey = new Map(pids.filter(p => anchor(p) !== null).map(p => [p, anchor(p)]));
    const kmin = x => Math.min(...kek[x]);
    for (const p of pids) {                // siblings, half-siblings too (at least one shared parent)
      const sibAnc = (parOf[p] ? pin[parOf[p]] : []).flatMap(q => own[q].flatMap(f => kin[f])).filter(x => kek[x]);
      if (!vkey.has(p) && sibAnc.length) {
        const a = sibAnc.reduce((best, x) => kmin(x) < kmin(best) ? x : best);
        vkey.set(p, anchor(a) + (kmin(a) % 2 === 0 ? -1e-4 : 1e-4));
      }
    }
    const queue = [...vkey.keys()];
    for (let i = 0; i < queue.length; i++) {
      const p = queue[i];
      for (const x of [...spouses[p], ...own[p].flatMap(f => kin[f]), ...(parOf[p] ? pin[parOf[p]] : [])]) {
        if (!vkey.has(x)) { vkey.set(x, vkey.get(p)); queue.push(x); }
      }
    }
    const orderKey = u => [ancKey(u) < 2 ? ancKey(u) : mean(u.map(p => vkey.has(p) ? vkey.get(p) : 2)),
                           Math.min(9999, ...u.map(p => byear[p]).filter(Boolean)), u[0]];
    for (const row of rows) {
      const keys = new Map(row.map(u => [u, orderKey(u)]));
      row.sort((a, b) => cmpKey(keys.get(a), keys.get(b)));
    }
    repack(null);
    relax(40);
    const pos = Object.fromEntries(pids.map(p => [p, cx(p)]));
    for (const row of rows) row.forEach((u, i) => { row[i] = turn(u, pos); });
    repack(pos);
    relax(300);

    const padX = 40, padY = Math.round(ROW_GAP * 0.45) + 10;
    const shift = padX - Math.min(...X.map(xs => xs[0]));
    X = X.map(xs => xs.map(x => x + shift));
    const top = r => padY + r * (CARD_H + ROW_GAP);
    const nodes = Object.fromEntries(pids.map(p => [p, [roundEven(cx(p) - CARD_W / 2), top(where[p][0])]]));
    const w = Math.max(...pids.map(p => cx(p) + CARD_W / 2)) + padX;
    const h = top(R - 1) + CARD_H + Math.round(ROW_GAP * 0.55);

    // -- lines: couple, drop from the couple, sibling bar (on tracks so they do not overlap), stems to children
    const fams = [], bars = new Map();
    for (const fid of fids) {
      const ps = pin[fid], ks = kin[fid];
      if (!ps.length) continue;
      const rec = { id: fid, parents: ps, children: ks, stems: {}, extra: [] };
      const low = ps.reduce((best, p) => where[p][0] > where[best][0] ? p : best);
      let dx, start;
      if (ps.length === 2 && where[ps[0]][0] === where[ps[1]][0]) {
        const [a, b] = [...ps].sort((p, q) => cx(p) - cx(q));
        const y = top(where[a][0]) + CARD_H / 2;
        if (Math.abs(where[a][2] - where[b][2]) === 1 && where[a][1] === where[b][1]) {
          rec.couple = [[cx(a) + CARD_W / 2, y], [cx(b) - CARD_W / 2, y]];
          start = y;
        } else {
          const yb = top(where[a][0]) + CARD_H + 8;
          rec.couple = [[cx(a), yb - 8], [cx(a), yb], [cx(b), yb], [cx(b), yb - 8]];
          start = yb;
        }
        dx = dropX(fid);
        const m = D.families[fid].m;
        rec.pill = { x: dx, y: top(where[a][0]) + CARD_H + 15, t: m ? '⚭ ' + m : '⚭' };
      } else {
        dx = cx(low);
        start = top(where[low][0]) + CARD_H;
        for (const p of ps) if (p !== low) rec.extra.push([[cx(p), top(where[p][0]) + CARD_H], [dx, start]]);
      }
      if (ks.length) {
        const xs = [...ks.map(cx), dx], rChild = Math.min(...ks.map(c => where[c][0]));
        if (!bars.has(rChild)) bars.set(rChild, []);
        bars.get(rChild).push([Math.min(...xs), Math.max(...xs), rec, dx, start]);
      }
      fams.push(rec);
    }
    for (const [rChild, items] of bars) {
      const tracks = [];
      for (const [lo, hi, rec, dx, start] of [...items].sort((a, b) => a[0] - b[0])) {
        let t = tracks.findIndex(end => end < lo - 8);
        if (t < 0) { t = tracks.length; tracks.push(hi); } else tracks[t] = hi;
        const yb = top(rChild) - 22 - 9 * t;
        rec.drop = [[dx, start], [dx, yb]];
        if (hi - lo > 1) rec.bar = [[lo, yb], [hi, yb]];
        for (const c of rec.children) rec.stems[c] = [[cx(c), yb], [cx(c), top(where[c][0])]];
      }
    }

    const lanes = gens.map((g, r) => {
      const years = pids.filter(p => gen[p] === g && byear[p]).map(p => byear[p]).sort((a, b) => a - b);
      const span = !years.length ? '' : years[0] === years.at(-1) ? `${years[0]}` : `${years[0]}–${years.at(-1)}`;
      const num = g + 1, older = -g;
      return { y: top(r) - Math.round(ROW_GAP * 0.45), h: CARD_H + ROW_GAP,
               title: g >= 0 ? `⟦Generation ${num}⟧` : '⟦Younger generation⟧' + (g < -1 ? ` (${older})` : ''),
               name: laneName(g), years: span && `⟦b. ${span}⟧` };
    });
    const rnd = v => Math.round(v * 10) / 10, pts = list => list.map(([x, y]) => [rnd(x), rnd(y)]);
    for (const rec of fams) {
      for (const k of ['couple', 'drop', 'bar']) if (rec[k]) rec[k] = pts(rec[k]);
      for (const c in rec.stems) rec.stems[c] = pts(rec.stems[c]);
      rec.extra = rec.extra.map(pts);
      if (rec.pill) { rec.pill.x = rnd(rec.pill.x); rec.pill.y = rnd(rec.pill.y); }
    }
    return { w: roundEven(w), h: roundEven(h), card: [CARD_W, CARD_H], nodes, fams, lanes };
  }

  /** Ancestors of `pb`, the siblings and half-siblings of every ancestor, the descendants of `pb`, and the spouses of them all. */
  function kin(D, G, kek, pb) {
    const set = new Set(Object.keys(kek));
    for (const a of Object.keys(kek)) for (const q of G.parents(a)) for (const fid of G.spouseIn[q] || []) D.families[fid].c.forEach(c => set.add(c));
    const seen = new Set([pb]), stack = [pb];
    while (stack.length) {
      for (const fid of G.spouseIn[stack.pop()] || []) for (const c of D.families[fid].c) if (!seen.has(c)) { seen.add(c); set.add(c); stack.push(c); }
    }
    for (const p of [...set]) for (const fid of G.spouseIn[p] || []) for (const x of [D.families[fid].h, D.families[fid].w]) if (x) set.add(x);
    return set;
  }

  /** The diagram from the perspective of `pb`. mode: 'anc' only their ancestors, 'kin' see kin(), 'all' every person. */
  function build(D, G, pb, mode) {
    const kek = kekule(D, G, pb), gen = generations(D, G, pb);
    let pids = Object.keys(D.persons), fids = Object.keys(D.families);
    if (mode === 'anc') {
      pids = Object.keys(kek).sort((a, b) => Math.min(...kek[a]) - Math.min(...kek[b]));
      fids = ancestralFamilies(D, G, kek);
    } else if (mode === 'kin') {
      const set = kin(D, G, kek, pb);
      pids = pids.filter(p => set.has(p));
      fids = fids.filter(fid => set.has(D.families[fid].h) || set.has(D.families[fid].w));
    }
    return { ...layoutView(D, G, pids, fids, gen, kek), kek, proband: D.persons[pb] ? pb : null };
  }

  return { graph, kekule, generations, ancestralFamilies, kin, layoutView, build };
})();
if (typeof module !== 'undefined') module.exports = TreeLayout;
