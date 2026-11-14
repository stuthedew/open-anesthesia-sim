---
id: PL-4J4H
title: A Projects thread started on 2026-11-14 in /home/user, above its one checkout, so the setup script's SessionStart entry looked for $CLAUDE_PROJECT_DIR/.claude/hooks/thread_hooks.py there, found nothing, and the thread ran with no guard hook and no digest
status: untriaged
added: 2026-11-14
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
