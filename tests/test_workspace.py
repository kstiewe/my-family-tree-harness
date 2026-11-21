import unittest

from _common import EXAMPLE, ROOT, env, run, tmpdir

from familytree import build, i18n, workspace


class FindWorkspace(unittest.TestCase):
    def test_explicit_path_wins(self):
        with env(FAMILYTREE_WORKSPACE=str(tmpdir())):
            ws = workspace.find_workspace(EXAMPLE)
        self.assertEqual((ws.root, ws.found_via), (EXAMPLE, "--workspace"))

    def test_environment_variable(self):
        with env(FAMILYTREE_WORKSPACE=str(EXAMPLE)):
            ws = workspace.find_workspace()
        self.assertEqual((ws.root, ws.found_via), (EXAMPLE, workspace.ENV_VAR))

    def test_current_directory_and_parents(self):
        with env(FAMILYTREE_WORKSPACE=None):
            ws = workspace.find_workspace(cwd=EXAMPLE / "research")
        self.assertEqual((ws.root, ws.found_via), (EXAMPLE, "current directory"))

    def test_pointer_file(self):
        pointer = tmpdir() / "workspace"
        pointer.write_text(f"{EXAMPLE}\n")
        self.assertEqual(workspace._read_pointer(pointer), EXAMPLE)

    def test_not_a_workspace(self):
        self.assertIsNone(workspace.find_workspace(tmpdir()))


class InitWorkspace(unittest.TestCase):
    def test_new_workspace_builds_cleanly(self):
        path = tmpdir() / "new-tree"
        code, stdout, _ = run(workspace.main, ["init", str(path), "--name", "Test tree", "--lang", "pl"])
        self.assertEqual(code, 0)
        for rel in ("data/project.yaml", "data/persons.yaml", "INSTRUCTIONS.md", "privacy.yaml", "research/log.md", ".gitignore"):
            self.assertTrue((path / rel).is_file(), rel)
        self.assertIn("language: pl", (path / "data/project.yaml").read_text())
        code, stdout, _ = run(build.main, ["--workspace", str(path)])
        self.assertEqual(code, 0, stdout)
        self.assertTrue((path / "output" / "drzewo.html").is_file())
        i18n.set_language("en")

    def test_refuses_to_create_a_workspace_inside_the_repository(self):
        code, _, stderr = run(workspace.main, ["init", str(ROOT / "data")])
        self.assertEqual(code, 1)
        self.assertIn("outside", stderr)
        self.assertFalse((ROOT / "data").exists())


class Context(unittest.TestCase):
    def test_context_contains_the_private_instructions(self):
        text = workspace.context_text(workspace.Workspace(EXAMPLE, "test"))
        self.assertIn("Private instructions", text)
        self.assertIn("Wzorcowo parish", text)
        self.assertIn("next free IDs: I0030", text)

    def test_hook_never_fails(self):
        with env(FAMILYTREE_WORKSPACE=str(tmpdir())):
            code, stdout, _ = run(workspace.main, ["context", "--hook"])
        self.assertEqual(code, 0)
        self.assertIn("No workspace found", stdout)


if __name__ == "__main__":
    unittest.main()
