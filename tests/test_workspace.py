import shutil
import unittest

from _common import CONFIG, EXAMPLE, ROOT, env, own_config, run, sample_copy, tmpdir

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
    def setUp(self):
        self.enterContext(own_config())

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


class Isolation(unittest.TestCase):
    def test_the_tests_never_touch_the_configuration_of_the_machine(self):
        self.assertEqual(workspace.registry_file(), CONFIG / "familytree" / "workspaces")
        self.assertEqual(workspace.POINTER, CONFIG / "app.workspace")


class Registry(unittest.TestCase):
    """The registry of every workspace on the machine, which the privacy guard checks (test_guard.SeveralWorkspaces)."""

    def setUp(self):
        self.enterContext(own_config())

    def test_register_list_and_unregister(self):
        a, b = sample_copy("a"), sample_copy("b")
        for path in (a, b, a):
            self.assertEqual(run(workspace.main, ["register", str(path)])[0], 0)
        self.assertEqual(workspace.registered(), [a, b])                       # registered twice, listed once
        code, stdout, _ = run(workspace.main, ["list"])
        self.assertEqual(code, 0)
        self.assertIn(f"{a}  (registered)", stdout)
        self.assertIn(f"{b}  (registered)", stdout)
        self.assertEqual(run(workspace.main, ["unregister", str(a)])[0], 0)
        self.assertEqual(workspace.registered(), [b])
        self.assertEqual(run(workspace.main, ["unregister", str(a)])[0], 1)   # not there any more

    def test_registry_is_plain_text_and_keeps_comments(self):
        a, b = sample_copy("a"), sample_copy("b")
        workspace.registry_file().parent.mkdir(parents=True)
        workspace.registry_file().write_text(f"# my trees\n\n{a}\n", encoding="utf-8")
        workspace.register(b)
        workspace.unregister(a)
        self.assertEqual(workspace.registry_file().read_text(encoding="utf-8"), f"# my trees\n\n{b}\n")

    def test_a_missing_workspace_is_listed_and_can_still_be_unregistered(self):
        gone = sample_copy("gone")
        workspace.register(gone)
        shutil.rmtree(gone)
        code, stdout, _ = run(workspace.main, ["list"])
        self.assertEqual(code, 1)
        self.assertIn(f"{gone}  (registered, but MISSING", stdout)
        self.assertEqual(run(workspace.main, ["unregister", str(gone)])[0], 0)
        self.assertEqual(workspace.registered(), [])

    def test_refuses_what_is_not_a_private_workspace(self):
        self.assertEqual(run(workspace.main, ["register", str(tmpdir())])[0], 1)
        code, _, stderr = run(workspace.main, ["register", str(EXAMPLE)])     # public: the guard must not block it
        self.assertEqual(code, 1)
        self.assertIn("public", stderr)
        self.assertEqual(workspace.registered(), [])

    def test_init_and_link_register_the_workspace(self):
        new, linked = (tmpdir() / "new-tree").resolve(), sample_copy("linked")
        self.assertEqual(run(workspace.main, ["init", str(new)])[0], 0)
        self.assertEqual(run(workspace.main, ["link", "--user", str(linked)])[0], 0)
        self.assertEqual(run(workspace.main, ["link", "--user", str(EXAMPLE)])[0], 0)   # linked, never registered
        self.assertEqual(workspace.registered(), [new, linked])
        code, stdout, _ = run(workspace.main, ["list"])
        self.assertEqual(code, 0)
        self.assertIn(f"{EXAMPLE}  (active, found via {workspace.user_config()})", stdout)
        self.assertIn(f"{new}  (registered)", stdout)


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
