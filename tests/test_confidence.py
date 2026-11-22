"""The evidence-based confidence model (familytree/confidence.py) and the confidence filter of the page, on the
fictional sample family and on invented variations of it."""

import json
import re
import shutil
import subprocess
import unittest

import yaml
from _common import EXAMPLE, run, tmpdir

from familytree import build, i18n
from familytree.confidence import band, classify, scores
from familytree.html import html_data
from familytree.model import FIXES, Tree


def workspace(edit=None):
    """A copy of the sample family; `edit(data)` may change persons/families/sources (lists of dicts) first."""
    ws = tmpdir() / "ws"
    shutil.copytree(EXAMPLE, ws, ignore=shutil.ignore_patterns("output"))
    if edit:
        data = {k: yaml.safe_load((ws / "data" / f"{k}.yaml").read_text(encoding="utf-8"))
                for k in ("persons", "families", "sources")}
        edit(data)
        for k, v in data.items():
            (ws / "data" / f"{k}.yaml").write_text(yaml.safe_dump(v, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return ws


def tree_of(edit=None) -> Tree:
    return Tree(workspace(edit) / "data")


def rec(data, kind, rid):
    return next(r for r in data[kind] if r["id"] == rid)


def add_source(data, sid, **fields):
    data["sources"].append({"id": sid, "title": f"Invented source {sid}", **fields})


class Scoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        i18n.set_language("en")
        cls.tree = Tree(EXAMPLE / "data")
        cls.cf = scores(cls.tree)

    def test_classification_defaults(self):
        s = self.tree.sources
        self.assertEqual(classify(s["S0003"]), "original")        # image of a marriage record
        self.assertEqual(classify(s["S0002"]), "derivative")      # index entry
        self.assertEqual(classify(s["S0006"]), "derivative")      # transcription
        self.assertEqual(classify(s["S0001"]), "authored")        # family account
        self.assertEqual(classify(s["S0009"]), "authored")        # someone else's online tree

    def test_two_sources_of_one_act_count_once(self):
        m = self.cf.marriages["F0007"]                            # index S0002 + image S0003 of act 15/1898
        self.assertEqual(len(m.items), 1)
        self.assertEqual(m.items[0].sid, "S0003")
        self.assertEqual(m.value, 70 + 8 + 5)                     # original/primary/direct + local copy + transcription
        self.assertTrue(any("S0002 is the same record as S0003" in ln.text for ln in m.lines))
        self.assertEqual(m.band, "probable")                      # one record, however good, is not "confirmed"

    def test_original_primary_direct_with_independent_record_is_confirmed(self):
        birth = self.cf.facts["I0018"]["birth"]                   # civil birth record image + parish baptism transcription
        self.assertEqual([(i.sid, i.cls, i.info, i.ev) for i in birth.items],
                         [("S0005", "original", "primary", "direct"), ("S0006", "derivative", "primary", "direct")])
        self.assertGreaterEqual(birth.value, 85)
        self.assertEqual(birth.band, "confirmed")

    def test_single_index_entry_is_never_confirmed(self):
        m = self.cf.marriages["F0011"]                            # only the index entry S0017
        self.assertEqual(m.items[0].cls, "derivative")
        self.assertLess(m.value, 85)
        self.assertTrue(any("View the scan of the record behind the index entry S0017" in tip for tip in m.tips))

    def test_oral_account_alone_stays_low(self):
        self.assertLess(self.cf.facts["I0007"]["birth"].value, 60)
        self.assertLess(self.cf.link("I0007").value, 60)
        self.assertEqual(self.cf.link("I0007").items[0].cls, "authored")

    def test_direct_and_indirect_evidence_for_the_link(self):
        w = self.cf.link("I0015")                                 # Wojciech: his marriage and death records name the parents
        self.assertEqual({i.sid: (i.info, i.ev) for i in w.items},
                         {"S0003": ("secondary", "direct"), "S0004": ("secondary", "direct")})
        self.assertIn("Antoni", w.items[0].names)                 # found in the Russian (Cyrillic) transcription
        self.assertTrue(any("confirmed needs direct evidence from an original source with primary information" in ln.text
                            for ln in w.lines))
        self.assertLessEqual(w.value, 84)
        j = self.cf.link("I0009")                                 # Józef: only the parents' marriage
        self.assertEqual((j.items[0].role, j.items[0].ev), ("parents-marriage", "indirect"))
        self.assertLess(j.value, 60)

    def test_chronology_warning_lowers_the_link(self):
        k = self.cf.link("I0013")                                 # born after the father's recorded death
        self.assertTrue(any(ln.pts == -10 and ln.text.startswith("chronology warning") for ln in k.lines))
        self.assertEqual(k.value, 34 - 10)

    def test_family_label_caps_the_links_of_its_children(self):
        self.assertEqual(self.cf.node_cap.get("I0019"), 59)       # Paulina: manual hypothesis
        self.assertLessEqual(self.cf.link("I0006").value, 84)     # F0005 is probable

    def test_same_informant_counts_once(self):
        g = self.cf.groups
        self.assertEqual(g.find("S0001"), g.find("S0016"))        # both accounts of Ewa Kowalska
        self.assertNotEqual(g.find("S0003"), g.find("S0004"))


class Variations(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")

    def test_independent_records_corroborate_and_derived_ones_do_not(self):
        def image(data):
            add_source(data, "S0019", type="marriage_record", quality="image", transcription="… Jakub Kowalski … Katarzyna Lis …")
            rec(data, "families", "F0011")["marriage"]["sources"].append("S0019")
        independent = scores(tree_of(image)).marriages["F0011"]
        self.assertEqual([i.sid for i in independent.items], ["S0019", "S0017"])
        self.assertEqual(independent.band, "confirmed")

        def derived(data):
            image(data)
            rec(data, "sources", "S0017")["derived_from"] = "S0019"
        one = scores(tree_of(derived)).marriages["F0011"]
        self.assertEqual([i.sid for i in one.items], ["S0019"])
        self.assertLess(one.value, 85)

    def test_two_indexes_of_one_act_count_once(self):
        def second_index(data):
            add_source(data, "S0019", type="index", quality="index", parish="P0002", year=1899, act="33",
                       transcription="1899 | 33 | Jakub | Kowalski | Katarzyna | Lis")
            rec(data, "families", "F0011")["marriage"]["sources"].append("S0019")
        base = scores(Tree(EXAMPLE / "data")).marriages["F0011"].value
        m = scores(tree_of(second_index)).marriages["F0011"]
        self.assertEqual(len(m.items), 1)
        self.assertEqual(m.value, base)

    def test_local_copy_and_transcription_are_credited(self):
        def no_file(data):
            rec(data, "sources", "S0003").pop("file")
        def nothing(data):
            no_file(data)
            rec(data, "sources", "S0003").pop("transcription")
        self.assertEqual(scores(tree_of(no_file)).marriages["F0007"].value, 83 - 8)
        self.assertEqual(scores(tree_of(nothing)).marriages["F0007"].value, 83 - 8 - 5)
        tips = scores(tree_of(no_file)).marriages["F0007"].tips
        self.assertTrue(any("Save a local copy of S0003" in t for t in tips))

    def test_conflicts_lower_the_score_and_block_confirmed(self):
        def conflict(resolved):
            return lambda data: rec(data, "persons", "I0018").update(
                conflicts=[{"about": "birth", "note": "the baptism gives another day", "resolved": resolved}])
        base = scores(Tree(EXAMPLE / "data")).facts["I0018"]["birth"].value
        open_ = scores(tree_of(conflict(False))).facts["I0018"]["birth"]
        self.assertEqual(open_.value, min(base - 20, 84))
        self.assertTrue(any("unresolved conflict: the baptism gives another day" in ln.text for ln in open_.lines))
        closed = scores(tree_of(conflict(True))).facts["I0018"]["birth"]
        self.assertEqual(closed.value, base - 5)
        self.assertEqual(closed.band, "confirmed")

    def test_resolved_conflict_explains_a_chronology_warning(self):
        def explain(data):
            rec(data, "persons", "I0013")["conflicts"] = [{"about": "link", "resolved": True,
                                                           "note": "the family's death date of the father is wrong"}]
        k = scores(tree_of(explain)).link("I0013")
        self.assertEqual(k.value, 34 - 5)
        self.assertTrue(any("explained by a resolved conflict" in ln.text for ln in k.lines))

    def test_manual_confidence_is_an_upper_cap(self):
        def label(data):
            rec(data, "persons", "I0022")["confidence"] = "hypothesis"
            rec(data, "persons", "I0018")["birth"]["confidence"] = "probable"
        cf = scores(tree_of(label))
        self.assertEqual(cf.link("I0022").value, 59)
        self.assertTrue(any(ln.pts is None and ln.text.startswith("at most 59") for ln in cf.link("I0022").lines))
        self.assertEqual(cf.facts["I0018"]["birth"].value, 84)
        self.assertEqual(cf.node_cap["I0022"], 59)

    def test_override_replaces_the_score_with_its_reason(self):
        def override(data):
            rec(data, "persons", "I0013")["confidence_override"] = {"score": 70, "reason": "birth record checked in the archive"}
            rec(data, "families", "F0011")["confidence_override"] = {"score": 90, "reason": "civil duplicate seen"}
        cf = scores(tree_of(override))
        k = cf.link("I0013")
        self.assertEqual((k.value, k.computed), (70, 24))
        self.assertIn("birth record checked in the archive", k.lines[-1].text)
        self.assertEqual(cf.marriages["F0011"].value, 90)

    def test_namesakes(self):
        def namesakes(status):
            return lambda data: rec(data, "persons", "I0015").update(identity={"namesakes": status, "note": "index 1860–1880"})
        base = scores(Tree(EXAMPLE / "data")).link("I0015")
        excluded = scores(tree_of(namesakes("excluded"))).link("I0015")
        possible = scores(tree_of(namesakes("possible"))).link("I0015")
        self.assertTrue(any(ln.pts == 5 and "namesakes checked and excluded" in ln.text for ln in excluded.lines))
        self.assertLess(possible.value, base.value)
        self.assertTrue(any(ln.pts == -15 for ln in possible.lines))

    def test_family_account_on_an_event_counts_for_the_link(self):
        def account(*sources):
            def edit(data):
                p = rec(data, "persons", "I0007")              # Stanisław: his parents known only from the family
                p["birth"].pop("sources")
                p["events"] = [{"type": "other", "sources": [s],
                                "note": "parents: Karol Nowak and Marta Majewska (family account)"} for s in sources]
            return edit
        without = scores(tree_of(account()))
        self.assertEqual(without.link("I0007").value, 0)
        self.assertLess(without.paths("I0001", "anc")["I0013"], 30)    # a deceased parent-in-path: the branch above falls
        one = scores(tree_of(account("S0001")))
        k = one.link("I0007")
        self.assertEqual([(i.sid, i.role, i.cls, i.info, i.ev) for i in k.items],
                         [("S0001", "account", "authored", "secondary", "direct")])
        self.assertEqual(k.value, 34)
        self.assertGreaterEqual(one.paths("I0001", "anc")["I0013"], 30)
        two = scores(tree_of(account("S0001", "S0016"))).link("I0007")  # two accounts of one informant
        self.assertEqual([i.sid for i in two.items], ["S0016"])
        self.assertTrue(any("S0001 is the same record as S0016 (the same informant)" in ln.text for ln in two.lines))
        self.assertEqual(two.value, 34 + 5)                              # the transcription of S0016, no corroboration

    def test_records_on_residence_and_occupation_events_do_not_count_for_the_link(self):
        jakub = scores(Tree(EXAMPLE / "data")).link("I0022")            # S0011, S0012 are cited on such events
        self.assertFalse([i for i in jakub.items if i.role == "account"])
        self.assertNotIn("S0012", [i.sid for i in jakub.items])

    def test_parentage_field_cites_link_evidence(self):
        def parentage(data):
            rec(data, "persons", "I0009")["parentage"] = {"sources": ["S0008"], "note": "the service book names the father"}
        base = scores(Tree(EXAMPLE / "data")).link("I0009").value
        cf = scores(tree_of(parentage))
        k = cf.link("I0009")
        item = next(i for i in k.items if i.sid == "S0008")
        self.assertEqual((item.role, item.cls, item.info, item.ev), ("parentage", "original", "secondary", "direct"))
        self.assertGreater(k.value, base)
        self.assertFalse([w for w in cf.tree.warnings if w.code in ("unknown-field", "unused-source") and w.record == "S0008"])

    def test_another_persons_record_does_not_count_for_the_link(self):
        cf = scores(Tree(EXAMPLE / "data"))
        death = cf.facts["I0024"]["death"]                  # Jakub's death record of 1931 cited for his wife's death in 1925
        self.assertEqual([(i.sid, i.role, i.ev) for i in death.items], [("S0013", "other", "indirect")])
        self.assertLess(death.value, 60)

        def child_record(data):                             # Franciszek's birth record (1903) cited on Wojciech's birth
            rec(data, "persons", "I0015")["birth"]["sources"] = ["S0012"]
        changed = scores(tree_of(child_record))
        self.assertNotIn("S0012", [i.sid for i in changed.link("I0015").items])
        self.assertEqual(changed.link("I0015").value, cf.link("I0015").value)
        self.assertEqual([(i.sid, i.role, i.ev) for i in changed.facts["I0015"]["birth"].items if i.sid == "S0012"],
                         [("S0012", "other", "indirect")])

    def test_names_count_only_in_a_statement_of_the_parents(self):
        def witnesses(data):                                # the parents' names occur, but as witnesses
            rec(data, "sources", "S0004")["transcription"] = ("Działo się we wsi Przykładowo … zmarł Wojciech Kowalski, "
                                                              "lat 55, rolnik … świadkowie Antoni Nowak i Marianna Lis …")
        w = scores(tree_of(witnesses)).link("I0015")
        s0004 = next(i for i in w.items if i.sid == "S0004")
        self.assertEqual((s0004.names, s0004.ev, s0004.info), ([], "indirect", "secondary"))
        base = next(i for i in scores(Tree(EXAMPLE / "data")).link("I0015").items if i.sid == "S0004")
        self.assertEqual((base.names, base.ev, base.info), (["Antoni", "Marianna"], "direct", "secondary"))

    def test_a_record_naming_another_parent_is_a_conflict(self):
        def other_mother(data):
            rec(data, "sources", "S0004")["transcription"] = "… zmarł Wojciech Kowalski, lat 55, syn Antoniego i Katarzyny …"
        w = scores(tree_of(other_mother)).link("I0015")
        s0004 = next(i for i in w.items if i.sid == "S0004")
        self.assertEqual(s0004.ev, "indirect")
        self.assertIn("S0004 names another mother: Katarzyny", s0004.contradiction)
        self.assertTrue(any(ln.pts == -20 and ln.text.startswith("conflict: S0004 names another mother") for ln in w.lines))

        def documented(data):
            other_mother(data)
            rec(data, "persons", "I0015")["conflicts"] = [{"about": "link", "resolved": True,
                                                           "note": "Katarzyna is the stepmother; see the second marriage"}]
        d = scores(tree_of(documented)).link("I0015")
        self.assertTrue(any(ln.pts == 0 and ln.text.startswith("conflict explained") for ln in d.lines))

    def test_latin_form_of_a_name_is_not_a_conflict(self):
        def latin(data):                                    # Agnieszka written as Agnes, Wojciech as Adalbertus
            rec(data, "sources", "S0004")["transcription"] = "… obiit Adalbertus Kowalski, filius Antonii et Agnetis …"
            rec(data, "persons", "I0021")["given"] = "Agnieszka"
        w = scores(tree_of(latin)).link("I0015")
        self.assertFalse(next(i for i in w.items if i.sid == "S0004").contradiction)

    def test_shared_file_or_a_mentioned_id_does_not_join_sources(self):
        def share(data):
            rec(data, "sources", "S0018")["file"] = rec(data, "sources", "S0003")["file"]
            rec(data, "sources", "S0017")["notes"] = "See also S0010 for the first marriage."
        g = scores(tree_of(share)).groups
        self.assertNotEqual(g.find("S0018"), g.find("S0003"))
        self.assertNotEqual(g.find("S0017"), g.find("S0010"))

    def test_baptism_without_an_adult_record_naming_the_parents_stays_probable(self):
        def strong(names_parents):
            def edit(data):
                rec(data, "sources", "S0015")["quality"] = "image"
                add_source(data, "S0019", type="civil_record", quality="image", year=1873,
                           transcription="… urodził się Jakub, syn Antoniego i Marianny …")
                rec(data, "persons", "I0022")["baptism"]["sources"].append("S0019")
                if not names_parents:
                    rec(data, "sources", "S0010")["transcription"] = "… Якуб Ковальский, холостой, 20 лет, батрак …"
            return edit
        capped = scores(tree_of(strong(False))).link("I0022")
        self.assertEqual(capped.value, 84)
        self.assertTrue(any(ln.pts is None and "no record of the adult" in ln.text for ln in capped.lines))
        self.assertTrue(capped.tips[0].startswith("Tie the baptism to the adult"))
        self.assertEqual(scores(tree_of(strong(True))).link("I0022").band, "confirmed")

    def test_new_fields_are_validated(self):
        def bad(data):
            rec(data, "persons", "I0013").update(conflicts=[{"about": "weather", "note": "x"}, {"about": "birth"}],
                                                 confidence_override={"score": 150, "reason": "x"},
                                                 identity={"namesakes": "maybe"})
            rec(data, "families", "F0011")["confidence_override"] = {"score": 50}
            rec(data, "sources", "S0017").update(classification="copy", information="tertiary", same_record_as=["S9999"])
            rec(data, "persons", "I0014")["parentage"] = {"note": "no sources"}
            rec(data, "persons", "I0015")["parentage"] = {"sources": ["S9998"]}
        t = tree_of(bad)
        codes = {(e.code, e.record) for e in t.errors}
        for expected in (("bad-value", "I0013"), ("bad-conflict", "I0013"), ("bad-override", "I0013"),
                         ("bad-override", "F0011"), ("bad-value", "S0017"), ("unknown-source", "S0017"),
                         ("bad-parentage", "I0014"), ("unknown-source", "I0015")):
            self.assertIn(expected, codes)
        self.assertTrue(all(FIXES.get(code) for code, _ in codes))

    def test_valid_new_fields_build_without_issues(self):
        def good(data):
            rec(data, "persons", "I0015").update(identity={"namesakes": "excluded", "note": "checked"},
                                                 conflicts=[{"about": "death", "note": "age differs", "resolved": True,
                                                             "sources": ["S0004"]}])
            rec(data, "sources", "S0002").update(same_record_as=["S0003"], information="primary", evidence="direct",
                                                 classification="derivative")
        t = tree_of(good)
        self.assertEqual(t.errors, [])
        self.assertFalse([w for w in t.warnings if w.code == "unknown-field"])


class Paths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        i18n.set_language("en")
        cls.tree = Tree(EXAMPLE / "data")
        cls.cf = scores(cls.tree)

    def test_ancestor_path_is_the_weakest_link_on_the_line(self):
        t, cf = self.tree, self.cf
        path = cf.paths("I0001", "anc")
        self.assertEqual(set(path), set(t.kekule))
        self.assertEqual(path["I0001"], 100)
        for pid in t.kekule:
            if pid == "I0001":
                continue
            children = [c for c in t.kekule if pid in t.parents(c)]
            expected = max(min(path[c], cf.step[(c, t.child_of[c][0])], cf.node_cap.get(pid, 100)) for c in children)
            self.assertEqual(path[pid], expected, pid)
        self.assertEqual(path["I0018"], min(path["I0013"], cf.link("I0013").value))

    def test_links_of_living_persons_do_not_lower_the_path(self):
        cf = self.cf
        self.assertLess(cf.link("I0003").value, 60)               # an account only …
        self.assertEqual(cf.paths("I0001", "anc")["I0005"], 100)  # … but Piotr is living: his parents are known first-hand
        self.assertTrue(any(ln.text.startswith("living person") for ln in cf.link("I0003").lines))

    def test_spouse_joins_through_the_union(self):
        full = self.cf.paths("I0001", "all")
        self.assertEqual(full["I0024"], min(full["I0022"], self.cf.union_step["F0011"]))

    def test_weakest_links_put_the_branch_with_the_lowest_step_first(self):
        self.assertEqual(self.cf.weakest_links()[0][0], "I0013")


class Outputs(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")

    def test_page_data_carries_scores_and_hides_breakdowns_of_living_persons(self):
        t = Tree(EXAMPLE / "data")
        d = html_data(t, public=False)
        self.assertEqual([b[0] for b in d["confidence"]["bands"]], ["confirmed", "probable", "hypothesis", "unsupported"])
        w = d["persons"]["I0015"]["cf"]
        self.assertEqual(w["l"], scores(t).link("I0015").value)
        self.assertEqual(set(w["x"]), {"link", "birth", "death"})
        self.assertTrue(all(isinstance(line[1], str) for line in w["x"]["link"]["w"]))
        f = d["families"]["F0007"]
        self.assertEqual(f["k"], {"I0017": scores(t).step[("I0017", "F0007")], "I0009": scores(t).step[("I0009", "F0007")]})
        self.assertIn("x", f)
        self.assertEqual(d["persons"]["I0019"]["cf"]["c"], 59)
        public = html_data(t, public=True)
        self.assertNotIn("x", public["persons"]["I0001"]["cf"])  # living: the score for the paths, no sources
        self.assertIn("l", public["persons"]["I0001"]["cf"])
        self.assertIn("x", public["persons"]["I0015"]["cf"])

    def test_report_and_json(self):
        out = tmpdir()
        code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out), "--json"])
        self.assertEqual(code, 0, stdout)
        result = json.loads(stdout)["confidence"]
        self.assertEqual(result["thresholds"], {"confirmed": 85, "probable": 60, "hypothesis": 30, "unsupported": 0})
        self.assertEqual(result["weakest_links"][0]["id"], "I0013")
        self.assertEqual(result["persons"]["I0018"]["birth"], scores(Tree(EXAMPLE / "data")).facts["I0018"]["birth"].value)
        report = (out / "confidence.md").read_text(encoding="utf-8")
        self.assertIn("# Confidence of the tree", report)
        self.assertIn("## Weakest links on the line of ancestors", report)
        self.assertIn("Find the birth or baptism record of Karol Nowak", report)
        self.assertIn("**Exception to the weakest link:**", report)     # the living-persons rule is stated
        self.assertIn("links of living persons do not lower it", (out / "tree.html").read_text(encoding="utf-8"))
        out_pl = tmpdir()
        code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out_pl), "--lang", "pl"])
        self.assertEqual(code, 0, stdout)
        self.assertIn("# Pewność drzewa", (out_pl / "pewnosc.md").read_text(encoding="utf-8"))
        i18n.set_language("en")

    def test_schema_documents_the_new_fields(self):
        code, stdout, _ = run(build.main, ["--schema"])
        schema = json.loads(stdout)
        for name in ("conflicts", "confidence_override", "identity", "parentage"):
            self.assertIn(name, schema["person"])
        self.assertIn("person.parentage", schema["field_notes"])
        for name in ("classification", "information", "evidence", "same_record_as", "derived_from"):
            self.assertIn(name, schema["source"])
            self.assertIn(f"source.{name}", schema["field_notes"])
        self.assertEqual(schema["enums"]["identity_namesakes"], ["excluded", "possible"])


# The page's layout script, as built into the page, run in node: the path confidence for a proband and the filtered views.
HARNESS = """
const fs = require('fs');
const [page, out] = process.argv.slice(2);
const html = fs.readFileSync(page, 'utf8');
const D = JSON.parse(html.match(/<script id="tree-data" type="application\\/json">([\\s\\S]*?)<\\/script>/)[1].replace(/<\\\\\\//g, '</'));
const layout = [...html.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)].map(m => m[1]).find(s => s.includes('const TreeLayout'));
const TreeLayout = new Function(layout + '; return TreeLayout;')();
const G = TreeLayout.graph(D), result = {};
for (const pb of ['I0001', 'I0015']) result[pb] = { anc: TreeLayout.paths(D, G, pb, 'anc'), all: TreeLayout.paths(D, G, pb, 'all') };
result.views = {};
for (const min of [0, 30, 60, 85]) for (const mode of ['anc', 'kin', 'all']) {
  const v = TreeLayout.build(D, G, 'I0001', mode, min);
  result.views[`${mode}:${min}`] = { nodes: Object.keys(v.nodes), hidden: v.hidden, path: v.path };
}
fs.writeFileSync(out, JSON.stringify(result));
"""


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class PageFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        i18n.set_language("en")
        out = tmpdir()
        code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out)])
        assert code == 0, stdout
        (out / "harness.js").write_text(HARNESS, encoding="utf-8")
        subprocess.run(["node", str(out / "harness.js"), str(out / "tree-artifact.html"), str(out / "result.json")],
                       check=True, capture_output=True, text=True)
        cls.result = json.loads((out / "result.json").read_text(encoding="utf-8"))
        cls.tree = Tree(EXAMPLE / "data")
        cls.cf = scores(cls.tree)

    def test_page_paths_match_the_model(self):
        for pb in ("I0001", "I0015"):
            for mode in ("anc", "all"):
                self.assertEqual(self.result[pb][mode], self.cf.paths(pb, mode), f"{pb} {mode}")

    def test_threshold_hides_persons_below_it_and_the_branch_above_them(self):
        t = self.tree
        for key, view in self.result["views"].items():
            mode, min_ = key.split(":")
            shown, hidden = set(view["nodes"]), set(view["hidden"])
            self.assertFalse(shown & hidden, key)
            self.assertTrue(all(view["path"].get(p, -1) >= int(min_) for p in shown) or min_ == "0", key)
            self.assertIn("I0001", shown, key)                    # the proband is never hidden
            if mode == "anc":
                for p in hidden:                                  # nobody above a hidden ancestor stays
                    stack = list(t.parents(p))
                    while stack:
                        a = stack.pop()
                        self.assertNotIn(a, shown, f"{key}: {a} above hidden {p}")
                        stack += t.parents(a)
        self.assertEqual(self.result["views"]["anc:0"]["hidden"], [])
        self.assertEqual(set(self.result["views"]["anc:30"]["hidden"]), {"I0018", "I0019"})   # behind Karol's weak link
        self.assertGreater(len(self.result["views"]["anc:60"]["hidden"]), len(self.result["views"]["anc:30"]["hidden"]))

    def test_page_template_has_the_filter(self):
        out = tmpdir()
        run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out)])
        page = (out / "tree.html").read_text(encoding="utf-8")
        self.assertIn('id="cf"', page)
        self.assertTrue(re.search(r'"confidence": \{"bands": \[\["confirmed", 85', page))


if __name__ == "__main__":
    unittest.main()
