import ast
import importlib
import re
import shutil
import string
import subprocess
import unittest

from _common import EXAMPLE, ROOT, run, tmpdir

from familytree import build, i18n
from familytree.history import EVENTS
from familytree.schema import LANGUAGES

PACKAGE = ROOT / "familytree"


def message_strings(node) -> set[str]:
    """Strings a tr() argument can evaluate to: literals, both branches of `a if c else b`, dict values, and the
    arguments of `self.g(male, female, other)` (summary.py picks the id for the person's grammatical gender)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.IfExp):
        return message_strings(node.body) | message_strings(node.orelse)
    if isinstance(node, ast.Dict):
        return set().union(*(message_strings(v) for v in node.values))
    if isinstance(node, ast.Subscript):
        return message_strings(node.value)
    if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "g":
        return set().union(*(message_strings(a) for a in node.args))
    return set()


def code_message_ids(functions=("tr", "trn")) -> set[str]:
    """Message ids of every tr() and trn() call in the package (or of the calls of `functions` only)."""
    ids: set[str] = set()
    for path in PACKAGE.rglob("*.py"):
        if "locales" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) in functions and node.args:
                ids |= message_strings(node.args[0])
    if "tr" in functions:
        ids |= set(LANGUAGES.values())      # schema.language_names() translates these
        ids |= {e.name for e in EVENTS}     # history.lived_through() translates these
    return ids


def template_ids() -> set[str]:
    return {m for p in (PACKAGE / "templates").glob("*.*") if p.suffix in (".html", ".js")
            for m in i18n.template_ids(p.read_text(encoding="utf-8"))}


def fields(text: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(text) if f}


class Catalogs(unittest.TestCase):
    def test_every_message_has_a_translation_and_none_is_unused(self):
        used = code_message_ids() | template_ids()
        for lang in i18n.available():
            if lang == i18n.DEFAULT:
                continue
            catalog = importlib.import_module(f"familytree.locales.{lang}").MESSAGES
            self.assertEqual(sorted(used - catalog.keys()), [], f"{lang}: missing translations")
            self.assertEqual(sorted(catalog.keys() - used), [], f"{lang}: unused entries")

    def test_placeholders_match(self):
        templates = template_ids()
        for lang in i18n.available():
            if lang == i18n.DEFAULT:
                continue
            for msgid, text in importlib.import_module(f"familytree.locales.{lang}").MESSAGES.items():
                if msgid in templates:
                    self.assertEqual(re.findall(r"\$\{[^}]*\}", msgid), re.findall(r"\$\{[^}]*\}", text), msgid)
                else:
                    self.assertEqual(fields(msgid), fields(text), msgid)

    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(i18n.set_language("xx"), "en")
        self.assertEqual(i18n.tr("Birth"), "Birth")

    def test_plural_forms(self):
        i18n.set_language("en")
        self.assertEqual([i18n.trn("{n} year later|{n} years later", n) for n in (1, 2)], ["1 year later", "2 years later"])
        i18n.set_language("pl")
        self.assertEqual([i18n.trn("lasted {n} year|lasted {n} years", n) for n in (1, 2, 5, 12, 22, 25)],
                         ["trwało 1 rok", "trwało 2 lata", "trwało 5 lat", "trwało 12 lat", "trwało 22 lata", "trwało 25 lat"])
        self.assertEqual(i18n.trn("He lived {n} year|He lived {n} years", 54, n="ok. 54"), "Przeżył ok. 54 lata")
        catalog = importlib.import_module("familytree.locales.pl").MESSAGES
        for msgid in code_message_ids(("trn",)):                # Polish has three forms: one, few, many
            self.assertEqual(catalog[msgid].count("|"), 2, msgid)
        i18n.set_language("en")


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class PageScript(unittest.TestCase):
    def test_page_scripts_parse_in_every_language(self):
        for lang in i18n.available():
            out = tmpdir()
            code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out), "--lang", lang])
            self.assertEqual(code, 0, stdout)
            pages = sorted(out.glob("*-*.html"))                                  # the artifact variants: tree, map
            self.assertEqual(len(pages), 2, pages)
            for path in pages:
                scripts = re.findall(r"<script>(.*?)</script>", path.read_text(encoding="utf-8"), re.S)
                self.assertTrue(scripts, path.name)
                for i, script in enumerate(scripts):
                    js = out / f"page{i}.js"
                    js.write_text(script, encoding="utf-8")
                    result = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, f"{lang} {path.name} script {i}: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
