---
id: PL-4J4H
title: A Projects thread started on 2026-11-14 in /home/user, above its one checkout, so the setup script's SessionStart entry looked for $CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py there, found nothing, and the thread ran with no guard hook and no digest
priority: P1
effort: S
status: done
classes: defect, infra
feature: projects-trial
milestone: v0.6.19
touches: .claude/hooks/thread_hooks.py, tests/unit/test_thread_hooks.py, docs/maintainer.md, .claude/skills/docket/modes/coordinator.md, docs/apparatus.md
deferred-from: v0.7.0 - a new problem: the setup entry it fails in came in with #1848 (50939e38, 2026-10-25, PL-X6VN), after the freeze
added: 2026-11-14
closed: 2026-11-22
pr: 2207
payoff: A Projects thread that starts above its checkout still runs with the guard hooks that refuse forbidden commands, and still sees the queue digest at start.
tests: tests/unit/test_thread_hooks.py::test_the_setup_script_s_entry_finds_the_hook_from_the_checkout_or_its_parent
reenters: PL-CR81
---

**Problem.** A Projects thread started on 2026-11-14 in /home/user, above its one checkout, so the setup script's SessionStart entry looked for $CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py there, found nothing, and the thread ran with no guard hook and no digest

**Measured 2026-11-14, about 03:15Z**, in the "Fix MAC age label and
"measured" wording" thread (Claude Code 2.1.325,
`CLAUDE_CODE_ENTRYPOINT=remote_projects`). The thread's primary working
directory at start was `/home/user`, which holds only the one checkout,
`/home/user/open-anesthesia-sim`; the project lists one repository. The
coordinator brief's probe, `uv run pytest -q tests/unit/test_line_splits.py`,
printed "5 passed", so no guard refused it, and no session-start digest
appeared. `~/.claude/settings.json` holds only the setup script's
`SessionStart` entry, whose command is `test -f
"$CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py" && python3 ... || true`.
With the thread starting above the checkout, that path does not exist, so the
entry did nothing and the repository's `hooks` block was never copied in.
`PL-CR81` (done) records the earlier probe that this setup did fix, and
`PL-9DYK` (done) the case of two configured repositories, which this is not.

**Candidate fix.** Let the setup script's entry also try
`"$CLAUDE_PROJECT_DIR"/*/.claude/hooks/thread_hooks.py` when the direct path
is missing, and have `thread_hooks.py` set `CLAUDE_PROJECT_DIR` to the
checkout it found, as `PL-TNY6` already does for a moved working directory.
`docs/maintainer.md` § on the setup script and `tests/unit/test_thread_hooks.py`
change with it.

**Checked 2026-11-22**, in the Projects thread that triaged this item. The fault is still there, and this thread has it too. The thread started in `/home/user`, and `~/.claude/settings.json` still holds only the setup script's `SessionStart` entry, `test -f "$CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py" && python3 ... || true`, with none of the repository's `PreToolUse`, `PostToolUse` or `PostToolUseFailure` hooks copied in. `.claude/hooks/thread_hooks.py` still tries only that one path. The entry came in with #1848 (50939e38, 2026-10-25 21:10 -04:00, `PL-X6VN`), after the freeze.

**Why it matters.** The guard hooks check each tool call before it runs, and refuse some, such as a `gh` command that can write to GitHub. The digest is what tells a session the queue's state at start. A thread that starts above its checkout runs without both, and nothing tells it so. Every such thread pays this, and the probe in `PL-CR81` (the earlier fix) does not catch it, because that probe assumed the thread starts inside the checkout.

**Done when.** A Projects thread whose working directory starts in the directory above its one checkout copies the repository's hooks into its user settings and prints the session-start digest, as a thread that starts inside the checkout does. A test of the setup entry shows both cases. `docs/maintainer.md` describes the entry as it then is.

**Generator check.** A re-entry of `PL-CR81` (Projects threads ran without this repository's hooks), closed 2026-11-03, eleven days before this was filed. Its fix assumed the thread's working directory is the checkout. The misread fact is where a session's working directory starts relative to its checkout. `PL-TNY6` (closed 2026-10-26: copied hooks lost their scripts when the working directory moved) and `PL-9DYK` (closed 2026-10-01: two configured repositories started threads above the checkout) misread the same fact, and no head's `misread:` line states it.

**Fixed 2026-11-22.** The thread "Restore guard hooks in project threads"
started in `/home/user` again, so the failure recurs whenever the harness
starts a thread there. The CLI diagnostics log showed the setup script's
`SessionStart` entry spawned and exited 0, and the probe printed "5 passed".
The entry now looks for `thread_hooks.py` in the start directory and then one
level below it, and runs the first copy it finds. `thread_hooks.py` already
pins every copied command to its own checkout (`PL-TNY6`), so nothing else
changed. The setup script is now one line that removes any older entry that
runs `thread_hooks.py` before it adds the current one. That lets the owner
paste it over the old block and still end with one entry.

The regression test, `test_the_setup_script_s_entry_finds_the_hook_from_the_checkout_or_its_parent[parent]`,
fails against the old entry with `assert (0, '') == (0, 'ran with..."startup"}\n')`
(`git show HEAD:.claude/hooks/thread_hooks.py > .claude/hooks/thread_hooks.py`,
then `uv run pytest -q tests/unit/test_thread_hooks.py -k parent`).

**Proved in that thread.** The new setup script was run over the thread's
`~/.claude/settings.json`, and its entry was run as Claude Code runs it, with
`CLAUDE_PROJECT_DIR=/home/user`. It printed the session-start digest and
copied the `SessionStart`, `PreToolUse`, `PostToolUse` and
`PostToolUseFailure` blocks. The next tool call carried the digest from the
`PostToolUse` hook, and the gate-status guard then refused
`uv run pytest -q tests/unit/test_line_splits.py | tail -1`, which had printed
"5 passed" a few minutes earlier. What only a new thread can show is that the
harness itself runs the new entry at the start; that needs the owner's paste.

**Documentation read 2026-11-22**, for the owner's question of which route is
standard. https://code.claude.com/docs/en/claude-projects.md § "What threads
pick up from your repositories" still lists `.claude/settings.json` hooks as
"Not run" in a cloud thread, and now lists the repository's skills, agents and
commands as loaded. Its § "Get skills, plugins, connectors, and tools into
threads" says plugins added in **Project settings > Plugins** load into each
new cloud thread. https://claude.com/docs/plugins/platform-support lists a
plugin's `hooks/hooks.json` as loading in Claude Code. In this thread, a plugin
synced from the owner's claude.ai account ran its `SessionStart` hook, which is
evidence for `PL-XFDQ` that plugin hooks reach a thread. Server-managed
settings also carry hooks into a thread
(https://code.claude.com/docs/en/cloud-environments.md § "Setup scripts vs.
SessionStart hooks"), but they need a Team or Enterprise plan
(https://code.claude.com/docs/en/server-managed-settings.md). A plugin's hook
command reads `CLAUDE_PROJECT_DIR` the same way, so the start-directory search
this item adds would be needed on that route too.

**Docs checked:** `docs/maintainer.md` § "Give Projects threads the
repository's hooks with one setup script" (updated), `.claude/skills/docket/modes/coordinator.md`
(the thread-probe bullet updated; its sentence that threads list none of the
repository's skills was false and is removed), `docs/apparatus.md` (its sentence that user settings never apply to a cloud
session now says the owner's own machine's settings never reach one, since a
thread reads the container's user settings), `CLAUDE.md`
and `docs/worker.md` (no mention).
