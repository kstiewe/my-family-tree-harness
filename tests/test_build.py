import json
import shutil
import unittest

from _common import EXAMPLE, run, tmpdir

from familytree import build, i18n
from familytree.model import Tree


class BuildSampleFamily(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")

    def build(self, *extra):
        out = tmpdir()
        code, stdout, stderr = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out), *extra])
        return code, stdout, out

    def test_builds_all_outputs_in_english(self):
        code, stdout, out = self.build()
        self.assertEqual(code, 0, stdout)
        for name in ("tree.html", "tree-artifact.html", "tree.mmd", "ancestors.mmd", "tree.ged", "gaps.md", "ancestors.md"):
            self.assertTrue((out / name).is_file(), name)
        self.assertIn("Next free IDs: I0030 F0013 P0007 S0019", stdout)
        self.assertIn("# Gaps in the data and research suggestions", (out / "gaps.md").read_text())
        self.assertNotIn("⟦", (out / "tree.html").read_text())

    def test_polish_outputs(self):
        code, stdout, out = self.build("--lang", "pl")
        self.assertEqual(code, 0, stdout)
        self.assertIn("Następne wolne ID:", stdout)
        self.assertIn("# Luki w danych i sugestie poszukiwań", (out / "luki.md").read_text())
        html = (out / "drzewo.html").read_text()
        self.assertIn('<html lang="pl">', html)
        self.assertIn("Przodkowie probanta", html)
        self.assertNotIn("⟦", html)

    def test_json_result(self):
        code, stdout, _ = self.build("--json")
        self.assertEqual(code, 0)
        result = json.loads(stdout)
        self.assertTrue(result["ok"])
        self.assertEqual(result["next_ids"], {"person": "I0030", "family": "F0013", "place": "P0007", "source": "S0019"})
        codes = {(w["code"], w["record"]) for w in result["warnings"]}
        self.assertIn(("unused-source", "S0009"), codes)
        self.assertIn(("chronology", "I0013"), codes)
        self.assertTrue(all(w["fix"] for w in result["warnings"]))

    def test_errors_block_outputs_and_are_coded(self):
        ws = tmpdir() / "broken"
        shutil.copytree(EXAMPLE, ws)
        persons = ws / "data" / "persons.yaml"
        persons.write_text(persons.read_text() + "\n- id: I90099\n  given: X\n  birth: {date: \"1850-13-40\", place: P0999}\n")
        out = tmpdir()
        code, stdout, _ = run(build.main, ["--workspace", str(ws), "--out", str(out), "--json"])
        self.assertEqual(code, 1)
        errors = {(e["code"], e["record"]) for e in json.loads(stdout)["errors"]}
        self.assertIn(("bad-date", "I90099"), errors)
        self.assertIn(("unknown-place", "I90099"), errors)
        self.assertFalse(any(out.iterdir()))

    def test_public_mode_hides_living_persons(self):
        code, _, out = self.build("--public")
        self.assertEqual(code, 0)
        ged = (out / "tree.ged").read_text()
        self.assertNotIn("Anna /Kowalska/", ged)
        self.assertIn("1 NAME Living person", ged)
        self.assertNotIn("Anna Kowalska", (out / "tree.html").read_text())
        self.assertIn("Jan /Kowalski/", ged)          # deceased persons stay

    def test_document_language_is_exported(self):
        code, _, out = self.build()
        self.assertEqual(code, 0)
        self.assertIn('"language": "German"', (out / "tree.html").read_text())
        self.assertIn("Language of the document: Latin", (out / "tree.ged").read_text())

    def test_find_ignores_diacritics_and_uses_married_names(self):
        tree = Tree(EXAMPLE / "data")
        self.assertIn("I0001", tree.find("kowal"))
        self.assertEqual(tree.find("wisniewska"), ["I0006"])
        self.assertIn("I0004", tree.find("ewa kowalska"))
        self.assertEqual(tree.find("no such person"), [])

    def test_kekule_numbers(self):
        tree = Tree(EXAMPLE / "data")
        self.assertEqual(tree.kekule["I0001"], [1])
        self.assertEqual(tree.kekule["I0003"], [2])
        self.assertEqual(tree.kekule["I0004"], [3])
        self.assertEqual(tree.kekule["I0020"], [32])

    def test_gap_report_has_geneteka_links_and_place_gaps(self):
        code, _, out = self.build()
        gaps = (out / "gaps.md").read_text()
        self.assertIn("https://geneteka.genealodzy.pl/index.php?", gaps)
        self.assertIn("`P0006` Bezparafie: missing", gaps)

    def test_schema(self):
        code, stdout, _ = run(build.main, ["--schema"])
        schema = json.loads(stdout)
        self.assertIn("language", schema["source"])
        self.assertIn("russian", schema["enums"]["partition"])
        self.assertIn("rosyjski", schema["enums"]["partition"])

    def test_polish_value_aliases_are_accepted(self):
        ws = tmpdir() / "aliases"
        shutil.copytree(EXAMPLE, ws)
        places = ws / "data" / "places.yaml"
        places.write_text(places.read_text().replace("partition: russian", "partition: rosyjski")
                          .replace("type: parish", "type: parafia"))
        tree = Tree(ws / "data")
        self.assertEqual(tree.errors, [])
        self.assertEqual(tree.parish_of("P0001")["id"], "P0002")


if __name__ == "__main__":
    unittest.main()
