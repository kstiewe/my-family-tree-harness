import unittest
from urllib.parse import parse_qs, urlparse

from _common import run

from familytree import geneteka


def params(url):
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}


class Links(unittest.TestCase):
    def test_page_url(self):
        p = params(geneteka.page_url(kind="S", w="07mz", surname="Kowalski", surname2="Nowak", lo=1870, hi=1880, pair=True))
        self.assertEqual((p["bdm"], p["w"], p["rid"], p["pair"]), ("S", "07mz", "S", "1"))
        self.assertEqual((p["search_lastname"], p["search_lastname2"], p["from_date"], p["to_date"]),
                         ("Kowalski", "Nowak", "1870", "1880"))

    def test_record_type_letters(self):
        self.assertEqual({k: geneteka.KINDS[k] for k in "BMDUZS"}, {"B": "B", "M": "S", "D": "D", "U": "B", "Z": "D", "S": "S"})

    def test_english_and_polish_options_give_the_same_link(self):
        en = run(geneteka.main, ["--link", "Kowalski", "-i", "Jan", "-t", "B", "-w", "07mz", "--from", "1840", "--to", "1860",
                                 "--exact", "--recent", "7"])
        pl = run(geneteka.main, ["--link", "Kowalski", "--imie", "Jan", "-t", "U", "-w", "07mz", "--od", "1840", "--do", "1860",
                                 "--dokladnie", "--ostatnie", "7"])
        self.assertEqual(en[0], 0)
        self.assertEqual(en[1], pl[1])
        p = params(en[1].strip())
        self.assertEqual((p["bdm"], p["search_name"], p["exac"], p["lastdays"]), ("B", "Jan", "1", "7"))

    def test_regions_list(self):
        code, out, _ = run(geneteka.main, ["--regions"])
        self.assertEqual(code, 0)
        self.assertIn("07mz  mazowieckie", out)


if __name__ == "__main__":
    unittest.main()
