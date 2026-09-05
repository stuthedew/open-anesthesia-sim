---
id: PL-W4H9
title: A session in auto mode cannot edit .claude/settings.json, and the cheap way past that guard is to append to an already-wired hook script, which is exactly what it must not do
priority: P2
effort: S
status: done
classes: infra, session-cost
feature: worker-instructions
touches: .claude/settings.json, .claude/hooks/stop_hook_patch.py, .claude/hooks/ruff.toml, pyproject.toml, tools/ignore_check.py, tests/unit/test_tools_portability.py, docs/ARCHITECTURE.md, CLAUDE.md
added: 2026-09-04
closed: 2026-09-05
pr: 340
verify: uv run pytest tests/unit/test_stop_hook_patch.py && python3 -c 'import json,sys; h=json.load(open(".claude/settings.json"))["hooks"]; c=[k["command"] for v in h.values() for e in v for k in e["hooks"]]; sys.exit(1 if not c or [x for x in c if "$CLAUDE_PROJECT_DIR/.claude/" not in x] else 0)'
---

**Problem.** One of the three scripts wired as a hook in `.claude/settings.json`
sits outside `.claude/`, so it is an ordinary working-directory file that a
session in auto mode may rewrite without review - and its job is to rewrite
another hook. The other two are already protected. As captured, this item said
instead that the guard sits on `.claude/settings.json` while the hook *scripts* it points at are
ordinary files under no such guard, so the cheap way to change hook behaviour is
to append to a script that is already wired. It then asked for a choice between
opening the front door (an explicit `permissions.allow` entry for the settings
file) and writing the prohibition down.

Checked against the Claude Code documentation on 2026-09-05, the premise is
wrong in three places and both proposed options fail on it.

**1. The guard is on the whole of `.claude/`, not on `settings.json`.**
`.claude` is a *protected directory* in Claude Code's own list, "except for
`.claude/worktrees` where Claude stores its own git worktrees"
(https://code.claude.com/docs/en/permission-modes#protected-paths, read
2026-09-05). So `.claude/hooks/docket-digest.sh` and
`.claude/hooks/docket-branch-guard.sh` are protected exactly as much as the
settings file is. For two of the three wired hooks, the side door this item
describes does not exist.

**2. `permissions.allow` cannot open the front door, so option one is not
implementable.** Verbatim from the same page: "`permissions.allow` rules in
settings files do not pre-approve protected-path writes. The safety check runs
before Claude Code evaluates allow rules from settings, so an entry such as
`Edit(.claude/**)` in `~/.claude/settings.json` or `.claude/settings.json` does
not change the per-mode outcome." Adding the entry would be a no-op that looks
like a working guard-relaxation - itself the failure mode `CLAUDE.md` names for
tooling, arriving through the fix rather than the defect.

**3. Auto mode does not block the write; it routes it to the classifier.** The
per-mode table gives `auto` as "Routed to the classifier", against "Prompted"
for `default`/`acceptEdits`, "Denied" for `dontAsk` and "Allowed" for
`bypassPermissions`. So the sanctioned route already exists in every mode this
project runs: a second model reviews the write rather than a wall refusing it.
In the prompting modes the dialog additionally offers "Yes, and allow Claude to
edit its own settings for this session".

**Why it matters.** The guard's subject is the set of commands that run
automatically in every session, and for one member of that set the guard is
absent while the other two make it look present - a check whose guarantee is
void where nobody would think to look. The correction matters as much as the
gap: option one below was going to be implemented as a `permissions.allow`
entry that the documentation says is ignored, which would have left a
guard-relaxation in the settings file that never did anything.

**What is actually broken.** One file. `tools/stop_hook_patch.py` is wired as a
`SessionStart` hook and lives outside `.claude/`, so it is an ordinary
working-directory file: in auto mode "file edits in your working directory are
auto-approved, except writes to protected paths"
(https://code.claude.com/docs/en/permission-modes#how-the-classifier-evaluates-actions,
read 2026-09-05). It is also the worst of the three to leave unguarded, because
its job is to rewrite *another* hook - `~/.claude/stop-hook-git-check.sh` - so
write access to it is write access to what every `Stop` in the session runs.

The cheap routes to it are all covered by an `Edit` rule if one existed: Read
and Edit rules "apply to Claude's built-in file tools and to file commands
Claude Code recognizes in Bash, such as `cat`, `head`, `tail`, and `sed`", and
"Claude Code checks the target of an output redirection, such as `>`, `>>`, or
`2>`, as a file write" against those rules and the protected paths
(https://code.claude.com/docs/en/permissions, read 2026-09-05). A Python script
that opens the file itself is not covered, and that is a determined bypass
rather than the cheap one this item is about.

**Decided (project owner, 2026-09-05): move the hook under the guard.**
`tools/stop_hook_patch.py` is now `.claude/hooks/stop_hook_patch.py`, alongside
the two hooks already there, so all three wired scripts sit behind the same
review as the settings file that names them. The harness enforces it, the
boundary needs no maintenance and no prose, and a hook added later is protected
by being put where hooks go. `docs/ARCHITECTURE.md` already called this file
"the one file here that is not a check", so the move removed an exception from
`tools/` rather than adding one; that section now explains the guard where the
next reader meets the directory.

Carried with it: the `command` path in `.claude/settings.json`; `.claude/hooks`
added to `pythonpath` and to mypy's `files` in `pyproject.toml` and to
`MYPY_PATH` in `tools/ignore_check.py`, so the test's bare
`import stop_hook_patch` and both type gates keep reaching it; the `tools/`
package map and prose in `docs/ARCHITECTURE.md`, where the hooks now have a
section of their own; the path in `CLAUDE.md`'s stale-ref rule; the test's own
docstring; and `PL-90CJ`'s brief.

**The move had to carry the bare-interpreter guard with it, and that is the
part worth recording.** `tools/ruff.toml` pins the formatter to Python 3.11
because everything under `tools/` runs as bare `python3` with no virtualenv,
and `tests/unit/test_tools_portability.py` globbed `tools/` to hold every file
there to that floor. A hook is invoked as bare `python3` too, so moving this
one out of `tools/` would have left it formatted at the repository's 3.14
target - which has already produced an unparseable file in this tree once, on
2026-08-31. The move therefore added `.claude/hooks/ruff.toml`, inheriting the
pin through `extend` so the floor stays declared in one place, and widened the
portability suite from one directory to a `BARE_ROOTS` tuple so the guard
follows the next hook without being extended by hand. Verified by removing the
pin and watching `test_the_formatter_target_matches_the_declared_floor` fail.

That near-miss is the item's own defect in miniature: a guard that stays
attached to a path rather than to the property it protects stops applying the
moment the file moves, and goes on looking present.

The rejected alternative was `"ask": ["Edit(tools/stop_hook_patch.py)"]` - three
lines and no config change, but a per-file exception list rather than a
boundary, leaving the next hook wired outside `.claude/` unguarded with nothing
to say so.

Not built: a prohibition in prose. Points 1 and 2 above leave nothing for prose
to forbid that the harness does not already stop.

Captured, not fixed: `PL-0SHZ` - `README.md`'s bare-interpreter paragraph names
two `ruff.toml` pins and there are now three. `.claude/rules/readme-hold.md`
freezes that file and says explicitly that a doc sweep does not override the
freeze, so it is recorded rather than edited.

`PL-WW08`'s `verify:` greps `.claude/settings.json` for the old path and no
longer resolves. That is left alone deliberately: a closed item's command is the
record of what was run on a tree that no longer exists, and `docket check`
errors on re-pointing one.

**Done when (met).** Every script wired as a hook in `.claude/settings.json` sits
behind the same review as the settings file itself, verified by resolving each
hook `command` path against the protected-path list rather than by assertion.
