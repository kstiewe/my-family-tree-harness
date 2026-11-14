@AGENTS.md

## Claude Code specifics

- `.claude/settings.json` runs `scripts/workspace.py context --hook` at session start; its output
  (workspace paths and the private INSTRUCTIONS.md) is your private context for the session.
- The workspace lives outside this directory. Add it to `permissions.additionalDirectories` in
  `.claude/settings.local.json` (git-ignored) so you can edit it without prompts.
- Preview the tree with the `tree` configuration of `.claude/launch.json`
  (`scripts/workspace.py serve`), or open `<workspace>/output/` files directly.
- Publishing the tree as an artifact: the URL and file are in the private instructions. If the
  artifact tool refuses a path outside the working directory, copy the file to your scratchpad
  first and publish that copy to the same URL.
