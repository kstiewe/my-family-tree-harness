import json
import re
import shutil
import subprocess
import unittest

from _common import EXAMPLE, run, tmpdir

from familytree import build, i18n
from familytree.model import Tree

# Runs the page's layout script (familytree/templates/layout.js, as built into the page) on the exported data and
# prints the views as JSON, for a few probands.
HARNESS = """
const fs = require('fs');
const [page, out, ...probands] = process.argv.slice(2);
const html = fs.readFileSync(page, 'utf8');
const D = JSON.parse(html.match(/<script id="tree-data" type="application\\/json">([\\s\\S]*?)<\\/script>/)[1].replace(/<\\\\\\//g, '</'));
const layout = [...html.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)].map(m => m[1]).find(s => s.includes('const TreeLayout'));
const TreeLayout = new Function(layout + '; return TreeLayout;')();
const G = TreeLayout.graph(D), result = {};
for (const pb of probands) result[pb] = Object.fromEntries(['anc', 'kin', 'all'].map(m => [m, TreeLayout.build(D, G, pb, m)]));
fs.writeFileSync(out, JSON.stringify(result));
"""


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class PageLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        i18n.set_language("en")
        out = tmpdir()
        code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out)])
        assert code == 0, stdout
        (out / "harness.js").write_text(HARNESS, encoding="utf-8")
        subprocess.run(["node", str(out / "harness.js"), str(out / "tree-artifact.html"), str(out / "views.json"),
                        "I0001", "I0003"], check=True, capture_output=True, text=True)
        cls.views = json.loads((out / "views.json").read_text(encoding="utf-8"))
        cls.tree = Tree(EXAMPLE / "data")

    def test_kekule_numbers_match_the_model(self):
        self.assertEqual(self.views["I0001"]["anc"]["kek"], self.tree.kekule)

    def test_ancestors_view_shows_only_ancestors_of_the_picked_proband(self):
        self.assertEqual(set(self.views["I0001"]["anc"]["nodes"]), set(self.tree.kekule))
        father = self.views["I0003"]["anc"]
        self.assertEqual(father["proband"], "I0003")
        self.assertEqual(father["kek"]["I0003"], [1])
        expected = {}                                               # the father's line, renumbered: 2 -> 1, 4 -> 2, 5 -> 3 ...
        for pid, nums in self.tree.kekule.items():
            if rel := sorted(n - (1 << (n.bit_length() - 2)) for n in nums if n >= 2 and n >> (n.bit_length() - 2) == 2):
                expected[pid] = rel
        self.assertEqual({pid: sorted(nums) for pid, nums in father["kek"].items()}, expected)
        self.assertNotIn("I0001", father["nodes"])                 # the child of the proband is not an ancestor

    def test_kin_view_adds_siblings_of_ancestors_and_descendants(self):
        t = self.tree
        for pb in ("I0001", "I0003"):
            kek = self.views[pb]["anc"]["kek"]
            expected = set(kek)
            for a in kek:                                           # siblings and half-siblings of every ancestor
                for parent in t.parents(a):
                    for fid in t.spouse_in.get(parent, []):
                        expected |= set(t.families[fid].get("children") or [])
            stack = [pb]                                            # descendants of the proband
            while stack:
                for fid in t.spouse_in.get(stack.pop(), []):
                    for c in t.families[fid].get("children") or []:
                        if c not in expected:
                            expected.add(c)
                            stack.append(c)
            for x in list(expected):                                # and the spouses of them all
                for fid in t.spouse_in.get(x, []):
                    expected |= {y for y in (t.families[fid].get("husband"), t.families[fid].get("wife")) if y}
            view = self.views[pb]["kin"]
            self.assertEqual(set(view["nodes"]), expected, pb)
            self.assertLessEqual(set(self.views[pb]["anc"]["nodes"]), set(view["nodes"]))
        self.assertIn("I0001", self.views["I0003"]["kin"]["nodes"])            # the father's child is his descendant
        self.assertLess(len(self.views["I0003"]["kin"]["nodes"]), len(t.persons))  # the mother's side stays out

    def test_whole_tree_from_another_perspective_places_everyone(self):
        for pb in ("I0001", "I0003"):
            view = self.views[pb]["all"]
            self.assertEqual(set(view["nodes"]), set(self.tree.persons))
            self.assertEqual(view["lanes"][[l["title"] for l in view["lanes"]].index("Generation 1")]["name"],
                             "proband, siblings and cousins")
            proband_y = view["nodes"][pb][1]
            lane = next(l for l in view["lanes"] if l["y"] <= proband_y < l["y"] + l["h"])
            self.assertEqual(lane["title"], "Generation 1", pb)

    def test_cards_do_not_overlap_and_parents_are_above_children(self):
        for pb in ("I0001", "I0003"):
            for kind in ("anc", "kin", "all"):
                view = self.views[pb][kind]
                w, h = view["card"]
                by_row: dict[int, list[int]] = {}
                for x, y in view["nodes"].values():
                    by_row.setdefault(y, []).append(x)
                for xs in by_row.values():
                    xs.sort()
                    self.assertTrue(all(b - a >= w for a, b in zip(xs, xs[1:])), (pb, kind))
                self.assertTrue(all(0 <= x and x + w <= view["w"] and 0 <= y and y + h <= view["h"] for x, y in view["nodes"].values()))
                for fam in view["fams"]:
                    for parent in fam["parents"]:
                        for child in fam["children"]:
                            self.assertLess(view["nodes"][parent][1], view["nodes"][child][1], (pb, kind, fam["id"]))

    def test_page_has_proband_picker_and_image_export(self):
        out = tmpdir()
        run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out), "--lang", "pl"])
        text = (out / "drzewo-artefakt.html").read_text(encoding="utf-8")
        self.assertIn('id="pb-q"', text)
        self.assertIn('id="pb-only"', text)
        self.assertIn('data-z="png"', text)
        self.assertIn("claude.use('downloads')", text)
        self.assertNotIn("⟦", text)
        self.assertTrue(re.search(r"Przodkowie: \$\{name\}", text))


if __name__ == "__main__":
    unittest.main()
