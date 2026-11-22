"""The privacy guard, tested against an invented "private" family created on the fly
(the Zawadzki family of Brzozówka) — it stands in for someone's real workspace."""

import contextlib
import shutil
import subprocess
import unittest
from pathlib import Path

from _common import env, own_config, run, sample_copy, tmpdir

from familytree import guard, workspace
from familytree.workspace import Workspace

PRIVATE = {
    "project.yaml": "name: Private test tree\nproband: I90042\nsurnames:\n  - {surname: Zawadzki, variants: [Zawadzky]}\n"
                    "regions: [\"okolice Olszynki (Brzozówka)\"]\n",
    "persons.yaml": "- id: I90042\n  given: Bronisława\n  surname: Zawadzka\n  married_surnames: [Ostrowska]\n"
                    "  variants: [Bronislava, Sawadzka]\n  birth: {date: \"1931-05-17\", place: P90042}\n",
    "families.yaml": "[]\n",
    "places.yaml": "- id: P90042\n  name: Brzozówka\n  aliases: [Birkenfelde]\n  parish: P90043\n"
                   "- id: P90043\n  name: Olszynka Wielka\n  type: parish\n",
    "sources.yaml": "- id: S90042\n  type: index\n  title: x\n  url: \"https://example.net/scan?id=987654\"\n"
                    "- id: S90043\n  type: online_tree\n  title: y\n  url: \"https://drzewo-test.example/osoba/1\"\n",
}


def private_workspace() -> Workspace:
    root = tmpdir() / "private"
    (root / "data").mkdir(parents=True)
    (root / "research").mkdir()
    for name, text in PRIVATE.items():
        (root / "data" / name).write_text(text, encoding="utf-8")
    (root / "research" / "notes.md").write_text("Unit 30301234 has the record.\n", encoding="utf-8")
    (root / "privacy.yaml").write_text('block: ["Ciocia Bronia"]\nallow: ["Archiwum w Brzozówce"]\n', encoding="utf-8")
    return Workspace(root, "test")


class Terms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws = private_workspace()
        cls.T = guard.load_terms(cls.ws)

    def found(self, text):
        return guard.scan_text(self.T, text, "t")

    def assertBlocked(self, text):
        self.assertTrue(self.found(text), f"not blocked: {text!r}")

    def assertClean(self, text):
        self.assertEqual(self.found(text), [], f"blocked: {text!r}")

    def test_surnames_and_inflected_forms(self):
        for text in ("Zawadzka", "rodzina Zawadzkich", "u Zawadzkiego", "OSTROWSKA", "Sawadzka", "Zawadzky"):
            self.assertBlocked(text)

    def test_places_inflected_aliases_and_regions(self):
        for text in ("Brzozówka", "w Brzozówce", "z Brzozowki", "Birkenfelde", "parafia Olszynka", "w Olszynce"):
            self.assertBlocked(text)

    def test_ids_dates_numbers_urls_and_block_list(self):
        for text in ("see I90042", "P90043", "born 1931-05-17", "ur. 17.05.1931", "unit 30301234",
                     "example.net/scan?id=987654", "on drzewo-test.example", "Ciocia Bronia mówiła"):
            self.assertBlocked(text)

    def test_generic_text_passes(self):
        for text in ("Jan Kowalski from Przykładowo", "Bronisława", "Nowa Wieś, gmina Wielka", "I0001 F0001 P0001 S0001",
                     "born 1850-03-12", "Archiwum w Brzozówce has the books", "a given name: Bronislava",
                     'key("Archiwum w Brzozówce"), "Archiwum w Brzozówce"'):
            self.assertClean(text)

    def test_artifact_links_are_blocked_even_without_private_data(self):
        T = guard.Terms(private=False)
        self.assertTrue(guard.scan_text(T, "https://claude.ai/" + "artifact/AbCdEf123456", "t"))
        self.assertEqual(guard.scan_text(T, "https://claude.ai/artifact/<id>", "t"), [])

    def test_workspace_paths(self):
        for path in ("data/persons.yaml", "research/log.md", "INSTRUCTIONS.md", "x/privacy.yaml", "out/tree.ged", ".workspace"):
            self.assertTrue(guard.scan_path(path), path)
        for path in ("examples/sample-family/data/persons.yaml", "examples/sample-family/INSTRUCTIONS.md", "docs/privacy.md"):
            self.assertEqual(guard.scan_path(path), [], path)


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class Hooks(unittest.TestCase):
    def setUp(self):
        self.enterContext(own_config())
        self.ws = private_workspace()
        self.repo = tmpdir() / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.old, guard.REPO = guard.REPO, self.repo

    def tearDown(self):
        guard.REPO = self.old

    def git(self, *args):
        env = {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.org", "GIT_COMMITTER_NAME": "Test",
               "GIT_COMMITTER_EMAIL": "test@example.org", "HOME": str(self.repo), "PATH": "/usr/bin:/bin"}
        return subprocess.run(["git", *args], cwd=self.repo, env=env, capture_output=True, check=True)

    def hook(self, *args):
        with _git_identity():
            return run(guard.main, ["--workspace", str(self.ws.root), *args])[0]

    def test_pre_commit_blocks_private_content_and_paths(self):
        (self.repo / "notes.md").write_text("Our grandmother Bronisława Zawadzkiego …\n")
        self.git("add", "notes.md")
        self.assertEqual(self.hook("pre-commit"), 1)

    def test_pre_commit_passes_clean_content(self):
        (self.repo / "README.md").write_text("Jan Kowalski from Przykładowo (fictional).\n")
        self.git("add", "README.md")
        self.assertEqual(self.hook("pre-commit"), 0)

    def test_commit_message(self):
        msg = self.repo / "MSG"
        msg.write_text("Add the Brzozówka parish\n")
        self.assertEqual(self.hook("commit-msg", str(msg)), 1)
        msg.write_text("Add a region guide\n")
        self.assertEqual(self.hook("commit-msg", str(msg)), 0)

    def test_audit_lists_and_scans_the_working_tree(self):
        (self.repo / "ok.md").write_text("Fictional Kowalski family.\n")
        (self.repo / "leak.md").write_text("w Brzozówce\n")
        with _git_identity():
            code, out, _ = run(guard.main, ["--workspace", str(self.ws.root), "audit"])
        self.assertEqual(code, 1)
        self.assertIn("leak.md", out)
        self.assertIn("ok.md", out)

    def test_fails_closed_without_workspace(self):
        with _git_identity():
            code = run(guard.main, ["--workspace", str(tmpdir()), "pre-commit"])[0]
        self.assertEqual(code, 1)


class SeveralWorkspaces(unittest.TestCase):
    """Two families on one machine: the invented Zawadzki family is the active workspace, a copy of the fictional
    sample family (Kowalski, Przykładowo) stands in for a second family's workspace that is registered, not linked."""

    def setUp(self):
        self.enterContext(own_config())
        self.active = private_workspace()
        self.other = sample_copy("other-family")
        self.msg = tmpdir() / "MSG"

    def commit_msg(self, text: str, *options: str) -> tuple[int, str]:
        self.msg.write_text(text, encoding="utf-8")
        code, _, stderr = run(guard.main, [*options, "commit-msg", str(self.msg)])
        return code, stderr

    def test_a_registered_workspace_is_checked_besides_the_active_one(self):
        active = ("--workspace", str(self.active.root))
        self.assertEqual(self.commit_msg("Notes on the Kowalski family", *active)[0], 0)
        workspace.register(self.other)
        code, stderr = self.commit_msg("Notes on the Kowalski family", *active)
        self.assertEqual(code, 1)
        self.assertIn("surnames: 'kowalski'", stderr)
        self.assertEqual(self.commit_msg("rodzina Zawadzkich", *active)[0], 1)
        self.assertEqual(self.commit_msg("A region guide", *active)[0], 0)

    def test_without_an_active_workspace_the_registered_ones_are_checked(self):
        # e.g. a new checkout of the application that has no .workspace file yet
        with env(FAMILYTREE_WORKSPACE=None), contextlib.chdir(tmpdir()):
            self.assertEqual(self.commit_msg("A region guide")[0], 1)          # no workspace at all: fail closed
            workspace.register(self.other)
            self.assertEqual(self.commit_msg("w Przykładowie")[0], 1)
            self.assertEqual(self.commit_msg("A region guide")[0], 0)

    def test_one_familys_allow_list_never_hides_another_familys_terms(self):
        text = "Archiwum w Brzozówce has the books"
        self.assertEqual(self.commit_msg(text, "--workspace", str(self.active.root))[0], 0)   # allowed by its family
        (self.other / "privacy.yaml").write_text('block: ["Brzozówka"]\n', encoding="utf-8")  # private for the other
        workspace.register(self.other)
        code, stderr = self.commit_msg(text, "--workspace", str(self.active.root))
        self.assertEqual(code, 1)
        self.assertIn("block: 'brzozowce'", stderr)

    def test_a_missing_registered_workspace_blocks(self):
        workspace.register(self.other)
        shutil.rmtree(self.other)
        code, stderr = self.commit_msg("A region guide", "--workspace", str(self.active.root))
        self.assertEqual(code, 1)
        self.assertIn(str(self.other), stderr)
        self.assertIn("unregister", stderr)
        self.assertEqual(self.commit_msg("A region guide", "--no-private")[0], 0)     # generic checks need no data
        with env(FAMILYTREE_GUARD_NO_PRIVATE="1"):
            self.assertEqual(self.commit_msg("A region guide")[0], 0)
        workspace.unregister(self.other)                                         # removed on purpose
        self.assertEqual(self.commit_msg("A region guide", "--workspace", str(self.active.root))[0], 0)

    def test_an_unreadable_registry_blocks(self):
        workspace.registry_file().mkdir(parents=True)                           # a directory, not a file
        self.assertEqual(self.commit_msg("A region guide", "--workspace", str(self.active.root))[0], 1)

    def test_terms_counts_every_workspace_and_shows_no_term(self):
        workspace.register(self.other)
        code, stdout, _ = run(guard.main, ["--workspace", str(self.active.root), "terms"])
        self.assertEqual(code, 0)
        self.assertIn("'workspaces': 2", stdout)
        self.assertIn("1. --workspace: {", stdout)
        self.assertIn(f"2. {workspace.REGISTERED}: {{", stdout)
        for term in ("zawadz", "brzoz", "kowalsk", "przyklad", "other-family"):
            self.assertNotIn(term, guard.fold(stdout))

    def test_each_workspace_is_matched_on_its_own(self):
        A = guard.load_terms(self.active)
        B = guard.load_terms(Workspace(self.other, "test"))
        text = "Zawadzka and Kowalska"
        self.assertEqual({f.found for f in guard.scan_text([A, B], text, "t")}, {"zawadzka", "kowalska"})
        self.assertEqual(guard.scan_text([A, A], text, "t"), guard.scan_text(A, text, "t"))   # no repeated findings


class _git_identity:
    """git var GIT_AUTHOR_IDENT needs an identity; provide a neutral one."""
    def __enter__(self):
        import os
        self.saved = {k: os.environ.get(k) for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL")}
        os.environ.update(GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.org",
                          GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.org")

    def __exit__(self, *exc):
        import os
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


if __name__ == "__main__":
    unittest.main()
