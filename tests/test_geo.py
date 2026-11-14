import json
import re
import shutil
import unittest

from _common import EXAMPLE, run, tmpdir

from familytree import build, i18n
from familytree.geo import Geo, compass, distance_km, surname_key, valid_coords
from familytree.model import Tree


def sample_copy(name: str):
    ws = tmpdir() / name
    shutil.copytree(EXAMPLE, ws)
    return ws


class Helpers(unittest.TestCase):
    def test_coords_distance_and_direction(self):
        self.assertTrue(valid_coords([52.6, 20.4]))
        for bad in ([52.6], [95, 20], [52, 200], ["52", "20"], [True, 20], "52, 20"):
            self.assertFalse(valid_coords(bad), bad)
        self.assertAlmostEqual(distance_km((52.0, 20.0), (53.0, 20.0)), 111.2, delta=0.5)
        self.assertEqual(compass((52.0, 20.0), (53.0, 20.0)), "N")
        self.assertEqual(compass((52.0, 20.0), (51.5, 19.0)), "SW")

    def test_surname_key_matches_male_and_female_forms(self):
        self.assertEqual(surname_key("Kowalska"), surname_key("Kowalski"))
        self.assertEqual(surname_key("Wiśniewska"), "wisniewski")
        self.assertEqual(surname_key("Nowakówna"), "nowak")
        self.assertEqual(surname_key("Nowak"), "nowak")


class SampleGeography(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")
        self.tree = Tree(EXAMPLE / "data")
        self.geo = Geo(self.tree)

    def test_clusters_group_neighbouring_places(self):
        self.assertEqual(len(self.geo.clusters), 2)
        c1, c2 = self.geo.clusters
        self.assertEqual(set(c1.places), {"P0001", "P0002", "P0003"})
        self.assertEqual(c2.places, ["P0004"])
        self.assertEqual(self.geo.cluster_label(c1), "Przykładowo and surroundings")
        data = self.geo.cluster_json(c1)
        self.assertEqual(data["partitions"], ["russian"])
        self.assertIn("I0009", [a["id"] for a in data["ancestors"]])

    def test_places_without_coords_are_to_geocode(self):
        self.assertEqual([g["place"] for g in self.geo.to_geocode()], ["P0006"])
        self.assertNotIn("P0006", self.geo.coords)

    def test_place_takes_the_coords_of_its_parish(self):
        ws = sample_copy("parish-coords")
        places = ws / "data" / "places.yaml"
        places.write_text(places.read_text().replace("  coords: [52.31, 17.02]\n", ""))
        geo = Geo(Tree(ws / "data"))
        self.assertEqual(geo.basis["P0004"], "parish")
        self.assertEqual(geo.coords["P0004"], (52.32, 17.05))
        gaps = Tree(ws / "data").place_gaps()
        self.assertIn("coordinates (coords; the map uses the parish's for now)", dict(gaps)["P0004"])

    def test_trails_follow_the_lines_of_ancestors(self):
        trails = self.geo.trails()
        nowak = next(t for t in trails if "I0018" in [x["id"] for x in t["tops"]])
        self.assertEqual([s["kekule"] for s in nowak["steps"]], [24, 12, 6, 1])
        self.assertEqual(nowak["legs"][-1]["direction"], "E")
        self.assertGreater(nowak["net_km"], 200)
        merged = next(t for t in trails if "I0020" in [x["id"] for x in t["tops"]])
        self.assertIn("I0021", [x["id"] for x in merged["tops"]])           # identical trails are merged

    def test_research_hints_name_a_reference_place(self):
        hints = {h["id"]: h for h in self.geo.research_hints()}
        self.assertEqual(hints["I0015"]["needs"], ["birth_place"])
        self.assertEqual(hints["I0015"]["reference"]["place"], "P0002")
        self.assertIn("I0001", self.tree.kekule)
        self.assertNotIn("I0001", hints)                                     # living persons get no hints
        self.assertIsNone(hints["I0020"]["reference"])

    def test_person_hints_get_a_map_line(self):
        details = [d for h in self.tree.person_hints("I0015") for d in h.details]
        self.assertTrue(any(d.startswith("Map: no other parish within 25 km of Wzorcowo") for d in details), details)

    def test_living_persons_can_be_left_out(self):
        geo = Geo(self.tree, living=False)
        self.assertNotIn("I0001", geo.by_person)
        self.assertIn("I0001", self.geo.by_person)

    def test_emigration_shows_as_a_long_move(self):
        ws = sample_copy("emigrant")
        (ws / "data" / "places.yaml").write_text((ws / "data" / "places.yaml").read_text()
                                                 + "\n- id: P0007\n  name: Nowe Przykładowo\n  type: town\n  country: US\n"
                                                   "  coords: [41.85, -87.65]\n")
        persons = ws / "data" / "persons.yaml"
        persons.write_text(persons.read_text().replace('  birth: {date: "1901", place: P0001}\n',
                                                       '  birth: {date: "1901", place: P0001}\n'
                                                       '  death: {date: "1960", place: P0007}\n'))
        tree = Tree(ws / "data")
        self.assertEqual(tree.errors, [])
        geo = Geo(tree)
        self.assertIn("P0007", geo.coords)
        self.assertTrue(any(c.places == ["P0007"] for c in geo.clusters))


class Validation(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")

    def test_out_of_range_coords_are_an_error(self):
        ws = sample_copy("bad-coords")
        places = ws / "data" / "places.yaml"
        places.write_text(places.read_text().replace("coords: [52.61, 20.38]", "coords: [152.61, 20.38]"))
        self.assertIn(("bad-coords", "P0001"), {(e.code, e.record) for e in Tree(ws / "data").errors})

    def test_swapped_coords_are_a_warning(self):
        ws = sample_copy("swapped")
        places = ws / "data" / "places.yaml"
        places.write_text(places.read_text().replace("coords: [52.61, 20.38]", "coords: [20.38, 52.61]"))
        tree = Tree(ws / "data")
        self.assertEqual(tree.errors, [])
        self.assertIn(("suspicious-coords", "P0001"), {(w.code, w.record) for w in tree.warnings})


class BuildOutputs(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")

    def build(self, *extra):
        out = tmpdir()
        code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out), *extra])
        self.assertEqual(code, 0, stdout)
        return out

    def test_map_and_geography_outputs(self):
        out = self.build()
        for name in ("map.html", "map-artifact.html", "geography.md", "geography.json"):
            self.assertTrue((out / name).is_file(), name)
        page = (out / "map.html").read_text()
        self.assertNotIn("⟦", page)
        self.assertNotIn("__DATA__", page)
        self.assertIn('"europe":{"q":200', page)                             # the geometry is embedded
        hosts = set(re.findall(r"https?://([^/\"']+)", page))
        self.assertEqual(hosts, {"fonts.googleapis.com", "fonts.gstatic.com"})  # nothing else is loaded
        self.assertFalse((out / "map-artifact.html").read_text().startswith("<!doctype"))
        data = json.loads((out / "geography.json").read_text())
        self.assertEqual(data["summary"]["clusters"], 2)
        self.assertEqual(data["to_geocode"][0]["place"], "P0006")
        md = (out / "geography.md").read_text()
        self.assertIn("# Geography of the family", md)
        self.assertIn("## Where to look for missing ancestors", md)
        gaps = (out / "gaps.md").read_text()
        self.assertIn("## 6. Geography", gaps)
        self.assertIn("geography.md", gaps)

    def test_polish_names_and_public_mode(self):
        out = self.build("--lang", "pl", "--public")
        page = (out / "mapa.html").read_text()
        self.assertIn("Mapa rodziny", page)
        self.assertIn("zabór pruski", page)
        self.assertNotIn("Anna Kowalska", page)                               # living proband left out
        self.assertIn("Józef Kowalski", page)
        self.assertTrue((out / "geografia.md").read_text().startswith("# Geografia rodziny"))

    def test_schema_describes_coords(self):
        code, stdout, _ = run(build.main, ["--schema"])
        self.assertIn("place.coords", json.loads(stdout)["field_notes"])


if __name__ == "__main__":
    unittest.main()
