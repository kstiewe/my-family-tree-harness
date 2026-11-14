import ast
import importlib
import re
import shutil
import string
import subprocess
import unittest

from _common import EXAMPLE, ROOT, run, tmpdir

from familytree import build, i18n
from familytree.schema import LANGUAGES

PACKAGE = ROOT / "familytree"


def message_strings(node) -> set[str]:
    """Strings a tr() argument can evaluate to: literals, both branches of `a if c else b`, dict values."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.IfExp):
        return message_strings(node.body) | message_strings(node.orelse)
    if isinstance(node, ast.Dict):
        return set().union(*(message_strings(v) for v in node.values))
    if isinstance(node, ast.Subscript):
        return message_strings(node.value)
    return set()


def code_message_ids() -> set[str]:
    """Message ids of every tr() call in the package."""
    ids: set[str] = set()
    for path in PACKAGE.rglob("*.py"):
        if "locales" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "tr" and node.args:
                ids |= message_strings(node.args[0])
    ids |= set(LANGUAGES.values())          # schema.language_names() translates these
    return ids


def template_ids() -> set[str]:
    return {m for p in (PACKAGE / "templates").glob("*.html") for m in i18n.template_ids(p.read_text(encoding="utf-8"))}


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


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class PageScript(unittest.TestCase):
    def test_page_script_parses_in_every_language(self):
        for lang in i18n.available():
            out = tmpdir()
            code, stdout, _ = run(build.main, ["--workspace", str(EXAMPLE), "--out", str(out), "--lang", lang])
            self.assertEqual(code, 0, stdout)
            page = next(out.glob("*-*.html")).read_text(encoding="utf-8")          # the artifact variant
            script = page.rsplit("<script>", 1)[1].split("</script>", 1)[0]
            js = out / "page.js"
            js.write_text(script, encoding="utf-8")
            result = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"{lang}: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
