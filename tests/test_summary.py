"""The "At a glance" part of the person card (familytree/summary.py), on the fictional sample family: Jakub Kowalski
(I0022) is a widower married three times who rose from farmhand to farmer and moved away late in life."""

import json
import re
import shutil
import unittest

from _common import EXAMPLE, run, tmpdir

from familytree import build, i18n
from familytree.model import Tree
from familytree.summary import after, person_summary, plain, sentences, stratum
from familytree.dates import parse_date


def row(summary: dict, key: str) -> dict | None:
    return next((r for r in summary["rows"] if r["key"] == key), None)


def texts(lines: list[dict]) -> list[str]:
    return [" / ".join(it["t"] for it in ln["items"]) for ln in lines]


class SampleSummary(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")
        self.tree = Tree(EXAMPLE / "data")
        self.jakub = person_summary(self.tree, "I0022")

    def test_occupations_in_time_order_and_the_rise_in_standing(self):
        who = row(self.jakub, "who")
        self.assertEqual([(it["t"], it["y"]) for it in who["items"]],
                         [("parobek", "1893"), ("komornik", "1896"), ("gospodarz", "1903"), ("wycużnik", "1931")])
        self.assertEqual(who["tail"][0]["t"], "Roman Catholic")
        self.assertIn("Rise in standing: parobek (1893) → gospodarz (1903)", texts(who["more"]))
        self.assertTrue(all(it.get("r") for it in who["items"]))          # every occupation points to its record

    def test_free_text_occupations_without_a_date_keep_their_place(self):
        self.assertEqual(stratum("komornik (Einlieger, 1835)"), ("landless", 2))
        self.assertEqual(stratum("Hofbesitzer"), ("farmer", 4))
        self.assertEqual(stratum("robotnik (landwirtschaftlicher Arbeiter)"), ("landless", 2))
        self.assertEqual(stratum("Altsitzer"), ("retired", None))
        self.assertEqual(stratum("nauczyciel"), (None, None))
        ws = tmpdir() / "occupations"
        shutil.copytree(EXAMPLE, ws)
        persons = ws / "data" / "persons.yaml"
        persons.write_text(persons.read_text().replace("  occupation: [farmer]\n  events:\n    - {type: military",
                                                       "  occupation: [\"parobek (1922)\", robotnik, \"gospodarz (1932)\"]\n"
                                                       "  events:\n    - {type: military"))
        who = row(person_summary(Tree(ws / "data"), "I0009"), "who")
        self.assertEqual([it["t"] for it in who["items"]], ["parobek", "robotnik", "gospodarz"])

    def test_a_date_before_or_after_is_a_bound_not_a_year(self):
        def who(events: str) -> dict:
            ws = tmpdir() / "bounds"
            shutil.rmtree(ws, ignore_errors=True)
            shutil.copytree(EXAMPLE, ws)
            persons = ws / "data" / "persons.yaml"
            persons.write_text(persons.read_text().replace("  occupation: [farmer]\n  events:\n", "  events:\n" + events))
            return row(person_summary(Tree(ws / "data"), "I0009"), "who")

        # the record of a child's wedding calls him "the late labourer": he was one before 1975, not until 1975
        late = '    - {type: occupation, date: "<1975", value: robotnik, sources: [S0008], note: "the late labourer"}\n'
        both = who('    - {type: occupation, date: "1930", value: robotnik, sources: [S0008]}\n' + late)
        self.assertEqual([(it["t"], it["y"]) for it in both["items"]], [("robotnik", "1930")])
        self.assertEqual([ln["y"] for ln in both["more"]], ["1930", "before 1975"])
        self.assertEqual([(it["t"], it["y"]) for it in who(late)["items"]], [("robotnik", "before 1975")])

    def test_places_of_the_life_merged_with_distances(self):
        where = row(self.jakub, "where")
        self.assertEqual([(it["t"], it.get("y")) for it in where["items"]],
                         [("Bezparafie", "1873"), ("Przykładowo", "1893–1899"), ("Zmyślin", "1903"), ("Wzorki", "1926–1931")])
        self.assertNotIn("pl", where["items"][0])                         # no coordinates: no link to the map
        self.assertEqual(where["items"][1]["pl"], "P0001")
        stays = [ln for ln in where["more"] if ln["k"] == "stay"]
        self.assertEqual(stays[1]["items"][0]["t"], "Przykładowo house no. 12")
        self.assertIn("wedding 20 Nov 1893 (Wzorcowo)", stays[1]["n"])   # a wedding in the parish church is no move
        self.assertIn("births of 3 children", stays[1]["n"])
        moves = [ln["km"] for ln in where["more"] if ln["k"] == "move"]
        self.assertEqual(len(moves), 2)
        self.assertLess(moves[0], 10)
        self.assertGreater(moves[1], 200)
        wojciech = row(person_summary(self.tree, "I0015"), "where")
        self.assertEqual([it["t"] for it in wojciech["items"]], ["Przykładowo"])

    def test_marriages_tell_the_story_of_the_widower(self):
        w = row(self.jakub, "with")
        self.assertEqual([it.get("p") for it in w["items"]], ["I0023", "I0024", "I0025"])
        self.assertEqual(w["tail"][0]["t"], "4 children")
        lines = texts(w["more"])
        self.assertIn("groom 20, bride 19 / 3 children (2 died in childhood) / lasted 5 years", lines)
        self.assertIn("He was widowed on 10 Feb 1899; remarried 5 months later (15 Jul 1899)", lines)
        self.assertIn("He was widowed on 20 Jan 1925; remarried 14 months later (11 Apr 1926)", lines)
        self.assertIn("ended with his death on 3 Mar 1931", lines)
        end = next(ln for ln in w["more"] if ln["k"] == "end")
        self.assertEqual(end["n"], "aged 25, cause: puerperal fever")
        self.assertEqual([ln["num"] for ln in w["more"] if ln["k"] == "marriage"], [1, 2, 3])
        self.assertIn("witnesses: Antoni Kowalski, father of the groom; Józef Nowicki", lines)

    def test_facts_computed_from_the_data(self):
        facts = texts(row(self.jakub, "facts")["more"])
        self.assertIn("He lived 57 years", facts)
        self.assertIn("Father of 4 children; 2 of them died in childhood", facts)
        self.assertIn("first child at the age of 21, the last at 30", facts)
        self.assertIn("the youngest of 2 known children", facts)
        self.assertIn("He was the first known of the Kowalski line to leave the home area", facts)
        self.assertLess(facts.index("He could not write and made a mark instead of a signature"),
                        facts.index("He signed his name"))
        self.assertIn("godparents: Jan Malinowski; Franciszka Nowak", facts)
        self.assertIn("languages of the records: Russian (4), Polish (2)", facts)
        lines = row(self.jakub, "facts")["more"]
        self.assertEqual(lines[0]["n"], "cause of death: pneumonia")
        self.assertEqual(lines[1]["n"], "Jan (aged 3 months), Józefa (aged 24 days)")

    def test_the_longest_lived(self):
        helena = texts(row(person_summary(self.tree, "I0010"), "facts")["more"])
        self.assertIn("She was the longest-lived of the proband's ancestors (7 with a known age)", helena)
        jan = texts(row(person_summary(self.tree, "I0005"), "facts")["more"])
        self.assertIn("He was the longest-lived of the Kowalski line (6 with a known age)", jan)

    def test_military_service_and_the_record_age(self):
        jozef = texts(row(person_summary(self.tree, "I0009"), "facts")["more"])
        self.assertIn("military service", jozef)
        wojciech = row(person_summary(self.tree, "I0015"), "facts")["more"][0]
        self.assertEqual(wojciech["items"][0]["t"], "He lived 55 years")   # the age the death record gives

    def test_the_times_follow_the_partition(self):
        times = row(self.jakub, "times")
        self.assertEqual(times["items"][0]["t"], "Russian partition")
        events = texts(times["more"])
        self.assertIn("the Revolution of 1905", events)
        self.assertNotIn("the Kulturkampf", events)
        self.assertEqual(times["more"][0]["n"], "aged 31–32")
        august = texts(row(person_summary(self.tree, "I0018"), "times")["more"])
        self.assertIn("the Prussian deportations of Poles", august)
        self.assertNotIn("the Revolution of 1905", august)

    def test_quotes(self):
        self.assertEqual(self.jakub["quote"]["t"], "He used to say that the soil in Wzorki was better than in Zmyślin.")
        self.assertTrue(self.jakub["quote"]["by"].startswith("Ewa Kowalska née Nowak"))
        self.assertEqual(self.jakub["refs"][self.jakub["quote"]["r"][0] - 1], "S0016")
        weronika = person_summary(self.tree, "I0025")["quote"]["t"]
        self.assertEqual(weronika, "Aunt Weronika, his third wife, was about ten years older than people thought.")
        wojciech = person_summary(self.tree, "I0015")["quote"]
        self.assertTrue(wojciech["t"].startswith("Działo się we wsi Przykładowo"), wojciech)
        self.assertIn("Death record no. 31/1925", wojciech["by"])

    def test_probable_and_hypothetical_facts_are_marked(self):
        august = row(person_summary(self.tree, "I0018"), "with")
        self.assertEqual(august["items"][0]["c"], "hypothesis")
        self.assertEqual(person_summary(self.tree, "I0011").get("conf"), "probable")

    def test_rows_without_data_are_left_out(self):
        marianna = person_summary(self.tree, "I0021")                     # no occupation, dates or facts of her own
        self.assertEqual([r["key"] for r in marianna["rows"]], ["where", "with"])
        self.assertTrue(all(r["items"] for s in (self.jakub, marianna) for r in s["rows"]))

    def test_public_mode_respects_living_persons(self):
        self.assertIsNone(person_summary(self.tree, "I0001", public=True))
        self.assertIsNotNone(person_summary(self.tree, "I0001"))
        jan = person_summary(self.tree, "I0005", public=True)
        self.assertNotIn("first child", json.dumps(jan))                 # his only child is living
        jakub = person_summary(self.tree, "I0022", public=True)
        self.assertNotEqual(jakub["quote"]["by"][:12], "Ewa Kowalska")  # no family accounts and informants in public

    def test_polish(self):
        i18n.set_language("pl")
        s = person_summary(Tree(EXAMPLE / "data"), "I0022")
        lines = texts(row(s, "with")["more"])
        self.assertIn("Owdowiał 10.02.1899; ponowny ślub po 5 miesiącach (15.07.1899)", lines)
        self.assertIn("on 20 l., ona 19 l. / 3 dzieci (2 zmarło w dzieciństwie) / trwało 5 lat", lines)
        self.assertEqual(row(s, "who")["label"], "Kim był")
        self.assertIn("Przeżył 57 lat", texts(row(s, "facts")["more"]))
        helena = person_summary(Tree(EXAMPLE / "data"), "I0010")
        self.assertEqual(row(helena, "where")["label"], "Gdzie mieszkała")
        i18n.set_language("en")


class Helpers(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")

    def test_intervals(self):
        d = parse_date
        self.assertEqual(after(d("1899-02-10"), d("1899-07-15")), "5 months later")
        self.assertEqual(after(d("1899-02-10"), d("1899-02-20")), "10 days later")
        self.assertEqual(after(d("1890"), d("1893")), "about 3 years later")
        self.assertEqual(after(d("1890"), d("1890")), "the same year")
        self.assertIsNone(after(d("1893"), d("1890")))

    def test_sentences_of_a_transcription(self):
        text = "Nr. 12. Musterau am 3. März 1880. Vor dem\nStandesbeamten erschien der Arbeiter\nMichael Nowak. Ende."
        self.assertEqual(sentences(text), ["Nr. 12. Musterau am 3. März 1880.",
                                           "Vor dem Standesbeamten erschien der Arbeiter Michael Nowak.", "Ende."])
        self.assertEqual(plain("der Arbeiter [?] Jan [reading uncertain] Nowak [...] zu Wzorki"),
                         "der Arbeiter [?] Jan Nowak … zu Wzorki")


class Validation(unittest.TestCase):
    def setUp(self):
        i18n.set_language("en")

    def test_new_fields_are_checked(self):
        ws = tmpdir() / "fields"
        shutil.copytree(EXAMPLE, ws)
        persons = ws / "data" / "persons.yaml"
        text = persons.read_text()
        text = text.replace("value: mark, sources: [S0010]", "value: crosses, sources: [S0010]")
        text = text.replace('residence, date: "1926", place: P0004', 'residence, date: "1926", confidence: maybe, place: P0004')
        text = text.replace("quote: {text: \"He used", "quote: {source: S9999, txt: \"He used")
        persons.write_text(text)
        codes = {(e.code, e.record) for e in Tree(ws / "data").errors}
        self.assertIn(("bad-value", "I0022"), codes)
        self.assertIn(("bad-quote", "I0022"), codes)

    def test_the_page_carries_the_summary(self):
        out = tmpdir()
        code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out), "--public"])
        self.assertEqual(code, 0, stdout)
        page = (out / "tree-artifact.html").read_text(encoding="utf-8")
        data = json.loads(re.search(r'<script id="tree-data" type="application/json">(.*?)</script>', page, re.S)[1]
                          .replace("<\\/", "</"))
        self.assertIn("summary", data["persons"]["I0022"])
        self.assertNotIn("summary", data["persons"]["I0001"])           # living: nothing in public mode
        self.assertIn('data-card="${pid}"', page)                        # the card can be saved as an image
        self.assertIn("showPlace", page)


if __name__ == "__main__":
    unittest.main()
