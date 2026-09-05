---
id: PL-W4H9
title: A session in auto mode cannot edit .claude/settings.json, and the cheap way past that guard is to append to an already-wired hook script, which is exactly what it must not do
priority: P2
effort: S
status: needs-decision
classes: infra, session-cost
feature: worker-instructions
touches: .claude/settings.json, tools/stop_hook_patch.py, pyproject.toml, docs/ARCHITECTURE.md
added: 2026-09-04
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

**Decision needed.** Which of two, both of which close the same one-file gap.

*Move the hook under the guard.* `tools/stop_hook_patch.py` becomes
`.claude/hooks/stop_hook_patch.py`, alongside the two hooks already there. The
harness enforces it, the boundary needs no maintenance and no prose, and any
hook added later is protected by being put where hooks go.
`docs/ARCHITECTURE.md` already calls this file "the one file here that is not a
check", so the move removes an exception rather than adding one. Costs: the
`command` path in `.claude/settings.json`, `.claude/hooks` added to
`pythonpath` and to mypy's `files` in `pyproject.toml` so the existing
`import stop_hook_patch` and the type gate keep reaching it, and two mentions
in `docs/ARCHITECTURE.md`.

*Name it in an `ask` rule.* `"ask": ["Edit(tools/stop_hook_patch.py)"]` in
`.claude/settings.json`. Three lines, the file stays where ruff, mypy and
pytest already reach it with no config change. Costs: it is a per-file
exception list rather than a boundary, so a hook wired outside `.claude/` later
is unguarded again and nothing says so.

Not a third option: writing the prohibition down. Points 1 and 2 above leave
nothing for prose to prohibit that the harness does not already stop, and
`CLAUDE.md` prefers deleting prose that something deterministic now enforces.

**Done when.** Every script wired as a hook in `.claude/settings.json` sits
behind the same review as the settings file itself, verified by resolving each
hook `command` path against the protected-path list rather than by assertion.
