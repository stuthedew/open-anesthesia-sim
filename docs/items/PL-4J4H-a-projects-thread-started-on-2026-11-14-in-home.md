---
id: PL-4J4H
title: A Projects thread started on 2026-11-14 in /home/user, above its one checkout, so the setup script's SessionStart entry looked for $CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py there, found nothing, and the thread ran with no guard hook and no digest
priority: P1
effort: S
status: ready
classes: defect, infra
feature: projects-trial
touches: .claude/hooks/thread_hooks.py, tests/unit/test_thread_hooks.py, docs/maintainer.md
deferred-from: v0.7.0 - a new problem: the setup entry it fails in came in with #1848 (50939e38, 2026-10-25, PL-X6VN), after the freeze
added: 2026-11-14
payoff: A Projects thread that starts above its checkout still runs with the guard hooks that refuse forbidden commands, and still sees the queue digest at start.
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
